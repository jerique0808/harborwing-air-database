import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
random.seed(42)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'alawakbar08',     'database': 'mydb'                       
}

def generate_data():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    print("Clearing old data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tables = [
        "reservation_leg_link", "reservation_payment_link", "payment",
        "reservation", "flight_cost", "calendar_date", "flight_leg",
        "flight_schedule", "booking_agent", "passenger", "airport"
    ]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    print("Populating database...")

    # 1. Airport
    airports = []
    for _ in range(50):
        code = fake.unique.lexify(text='???').upper()
        name = f"{fake.city()} International Airport"
        loc = fake.city()
        cursor.execute(
            "INSERT INTO airport (idairport, airport_code, airport_name, location) VALUES (%s, %s, %s, %s)",
            (code, code, name, loc)
        )
        airports.append(code)

    # 2. Passenger
    passengers = []
    for _ in range(60):
        cursor.execute("""
            INSERT INTO passenger (first_name, second_name, last_name, phone_number, email, address_lines, city, state_province, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            fake.first_name(),
            fake.first_name() if random.choice([True, False]) else None,
            fake.last_name(),
            fake.phone_number()[:20],
            fake.unique.email(),
            fake.street_address(),
            fake.city(),
            fake.state(),
            fake.country()
        ))
        passengers.append(cursor.lastrowid)

    # 3. Booking Agent
    agents = []
    for _ in range(50):
        cursor.execute("INSERT INTO booking_agent (agent_name, additional_details) VALUES (%s, %s)",
                       (fake.company(), fake.sentence()))
        agents.append(cursor.lastrowid)

    # 4. Flight Schedule
    schedules = []
    for i in range(50):
        flight_num = f"HW{100 + i}"
        orig, dest = random.sample(airports, 2)
        sched_dep = fake.date_time_this_year()
        sched_arr = sched_dep + timedelta(hours=random.randint(1, 6))
        cursor.execute("""
            INSERT INTO flight_schedule (flight_number, airline_code, aircraft_type_code, origin_airport, destination_airport, schedule_departure, schedule_arrival)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (flight_num, "HW", random.choice(["B737", "A320", "E190"]), orig, dest, sched_dep, sched_arr))
        schedules.append(flight_num)

    # 5. Flight Leg
    legs = []
    for sched in schedules:
        orig, dest = random.sample(airports, 2)
        act_dep = fake.date_time_this_year()
        act_arr = act_dep + timedelta(hours=random.randint(1, 6))
        cursor.execute("""
            INSERT INTO flight_leg (flight_number, origin_airport, destination_airport, actual_departure, actual_arrival, flight_schedule_flight_number)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sched, orig, dest, act_dep, act_arr, sched))
        legs.append(cursor.lastrowid)

    # 6. Calendar Date
    dates = []
    start_date = datetime(2026, 1, 1)
    for i in range(60):
        curr_date = (start_date + timedelta(days=i)).date()
        cursor.execute("INSERT INTO calendar_date (date_id, day_of_month, business_day_indicator) VALUES (%s, %s, %s)",
                       (curr_date, curr_date.day, 1 if curr_date.weekday() < 5 else 0))
        dates.append(curr_date)

    # 7. Flight Cost
    for i in range(50):
        v_from = dates[i % len(dates)]
        v_to = dates[(i + 5) % len(dates)]
        if v_to < v_from:
            v_from, v_to = v_to, v_from
        cursor.execute("""
            INSERT INTO flight_cost (flight_number, aircraft_type_code, valid_from_date, cost_amount)
            VALUES (%s, %s, %s, %s)
        """, (schedules[i], "B737", v_from, round(random.uniform(100.0, 500.0), 2)))

    # 8. Reservation
    reservations = []
    for _ in range(60):
        agent_id = random.choice(agents) if random.choice([True, False]) else None
        cursor.execute("""
            INSERT INTO reservation (passenger_id, booking_agent_id, reservation_status_code, ticket_type_code, travel_class_code, creation_datetime, party_size)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            random.choice(passengers),
            agent_id,
            random.choice(["CONF", "PEND", "CANC"]),
            random.choice(["ONEWAY", "ROUND"]),
            random.choice(["ECON", "BUS"]),
            fake.date_time_this_year(),
            random.randint(1, 5)
        ))
        reservations.append(cursor.lastrowid)

    # 9. Payment
    payments = []
    for _ in range(60):
        cursor.execute("""
            INSERT INTO payment (payment_status_code, payment_date, payment_amount)
            VALUES (%s, %s, %s)
        """, ("PAID", fake.date_time_this_year(), round(random.uniform(150.0, 1200.0), 2)))
        payments.append(cursor.lastrowid)

    # 10. Reservation Payment Link
    for res_id in reservations[:50]:
        pay_id = random.choice(payments)
        cursor.execute("INSERT INTO reservation_payment_link (reservation_id, payment_id) VALUES (%s, %s)",
                       (res_id, pay_id))

    # 11. Reservation Leg Link
    for res_id in reservations[:50]:
        leg_id = random.choice(legs)
        cursor.execute("INSERT INTO reservation_leg_link (reservation_id, leg_id) VALUES (%s, %s)",
                       (res_id, leg_id))

    conn.commit()
    cursor.close()
    conn.close()
    print("Database successfully populated with at least 50 records per table!")

if __name__ == '__main__':
    generate_data()