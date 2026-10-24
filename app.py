import streamlit as st
from db import execute_query

st.set_page_config(page_title="HarborWing Air - Staff Portal", layout="wide")
st.title("🛫 HarborWing Air - Employee Management Portal")

menu = [
    "Passengers",
    "Booking Agents",
    "Reservations & Links",
    "Payments",
    "Airports",
    "Flight Schedules & Legs",
    "Flight Costs"
]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# ==========================================
# 1. PASSENGERS CRUD
# ==========================================
if choice == "Passengers":
    st.header("👤 Passenger Management")
    
    # SEARCH / READ
    st.subheader("🔍 Search Passengers")
    search_term = st.text_input("Search by Last Name")
    if search_term:
        passengers = execute_query(
            "SELECT * FROM passenger WHERE last_name LIKE %s",
            (f"%{search_term}%",)
        )
    else:
        passengers = execute_query("SELECT * FROM passenger LIMIT 50")
    st.dataframe(passengers, use_container_width=True)

    # CREATE
    with st.expander("➕ Create New Passenger"):
        col1, col2 = st.columns(2)
        fn = col1.text_input("First Name")
        ln = col2.text_input("Last Name")
        email = col1.text_input("Email")
        phone = col2.text_input("Phone Number")
        address = col1.text_input("Address")
        city = col2.text_input("City")
        state = col1.text_input("State/Province")
        country = col2.text_input("Country")
        
        if st.button("Save Passenger"):
            if fn and ln and email:
                try:
                    q = """
                    INSERT INTO passenger 
                    (first_name, last_name, email, phone_number, address_lines, city, state_province, country)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    new_id = execute_query(
                        q,
                        (fn, ln, email, phone, address, city, state, country),
                        commit=True
                    )
                    st.success(f"Passenger created successfully! Allocated ID: {new_id}")
                except Exception as e:
                    st.error(f"Failed to create passenger: {e}")
            else:
                st.warning("First Name, Last Name, and Email are required!")

    # UPDATE
    with st.expander("✏️ Update Passenger Record"):
        update_id = st.number_input("Passenger ID to Update", min_value=1, step=1)
        new_email = st.text_input("New Email Address")
        if st.button("Update Email"):
            if new_email:
                try:
                    execute_query(
                        "UPDATE passenger SET email = %s WHERE idpassenger = %s",
                        (new_email, update_id),
                        commit=True
                    )
                    st.success("Passenger email updated successfully!")
                except Exception as e:
                    st.error(f"Update failed: {e}")

    # DELETE SAFELY
    with st.expander("🗑️ Delete Passenger"):
        del_id = st.number_input("Passenger ID to Delete", min_value=1, step=1)
        if st.button("Delete Passenger Record"):
            try:
                execute_query(
                    "DELETE FROM passenger WHERE idpassenger = %s",
                    (del_id,),
                    commit=True
                )
                st.success("Passenger deleted successfully!")
            except Exception as e:
                st.error(f"Cannot delete record. Foreign key constraint active: {e}")

# ==========================================
# 2. BOOKING AGENTS CRUD
# ==========================================
elif choice == "Booking Agents":
    st.header("📋 Booking Agent Management")
    agents = execute_query("SELECT * FROM booking_agent LIMIT 50")
    st.dataframe(agents, use_container_width=True)

    with st.expander("➕ Add Booking Agent"):
        agent_name = st.text_input("Agent Name")
        details = st.text_area("Additional Details")
        if st.button("Save Agent"):
            if agent_name:
                execute_query(
                    "INSERT INTO booking_agent (agent_name, additional_details) VALUES (%s, %s)",
                    (agent_name, details),
                    commit=True
                )
                st.success("Booking agent saved successfully!")

# ==========================================
# 3. RESERVATIONS & LINKS
# ==========================================
elif choice == "Reservations & Links":
    st.header("🎟️ Reservation & Link Management")

    # VIEW COMPLETE RESERVATION
    st.subheader("🔎 View Complete Reservation Record")
    res_lookup_id = st.number_input("Enter Reservation ID", min_value=1, step=1)
    if st.button("Fetch Complete Summary"):
        res_info = execute_query(
            "SELECT * FROM reservation WHERE idreservation = %s",
            (res_lookup_id,)
        )
        if res_info:
            st.write("### Reservation Details", res_info[0])
            
            # Linked Flight Legs
            legs = execute_query("""
                SELECT fl.* FROM flight_leg fl
                JOIN reservation_leg_link rll ON fl.idflight_leg = rll.leg_id
                WHERE rll.reservation_id = %s
            """, (res_lookup_id,))
            st.write("#### Linked Flight Legs", legs)

            # Linked Payments
            payments = execute_query("""
                SELECT p.* FROM payment p
                JOIN reservation_payment_link rpl ON p.idpayment = rpl.payment_id
                WHERE rpl.reservation_id = %s
            """, (res_lookup_id,))
            st.write("#### Linked Payments", payments)
        else:
            st.error("No reservation found for that ID.")

    st.markdown("---")

    # CREATE RESERVATION
    st.subheader("➕ Create New Reservation")
    c1, c2 = st.columns(2)
    p_id = c1.number_input("Passenger ID", min_value=1, step=1)
    status = c2.selectbox("Status Code", ["CONF", "PEND", "CANC"])
    t_type = c1.selectbox("Ticket Type", ["ONEWAY", "ROUND"])
    t_class = c2.selectbox("Travel Class", ["ECON", "BUS", "FIRST"])
    party = c1.number_input("Party Size", min_value=1, value=1)
    
    if st.button("Create Reservation"):
        try:
            q = """
            INSERT INTO reservation 
            (passenger_id, reservation_status_code, ticket_type_code, travel_class_code, creation_datetime, party_size)
            VALUES (%s, %s, %s, %s, NOW(), %s)
            """
            new_res_id = execute_query(
                q,
                (p_id, status, t_type, t_class, party),
                commit=True
            )
            st.success(f"Reservation created! ID: {new_res_id}")
        except Exception as e:
            st.error(f"Failed to create reservation: {e}")

    st.markdown("---")

    # LINK FLIGHT LEG
    st.subheader("🔗 Link Flight Leg to Reservation")
    lc1, lc2 = st.columns(2)
    link_res_id = lc1.number_input("Target Reservation ID", min_value=1, step=1, key="l_res")
    link_leg_id = lc2.number_input("Target Flight Leg ID", min_value=1, step=1, key="l_leg")
    if st.button("Link Flight Leg"):
        try:
            execute_query(
                "INSERT INTO reservation_leg_link (reservation_id, leg_id) VALUES (%s, %s)",
                (link_res_id, link_leg_id),
                commit=True
            )
            st.success("Flight Leg linked to Reservation successfully!")
        except Exception as e:
            st.error(f"Error: Invalid ID or relationship link already exists! Details: {e}")

    # UNLINK FLIGHT LEG SAFELY
    st.subheader("✂️ Remove Flight Leg Link (Preserves Leg Record)")
    uc1, uc2 = st.columns(2)
    unlink_res_id = uc1.number_input("Reservation ID", min_value=1, step=1, key="u_res")
    unlink_leg_id = uc2.number_input("Flight Leg ID to Unlink", min_value=1, step=1, key="u_leg")
    if st.button("Unlink Flight Leg"):
        execute_query(
            "DELETE FROM reservation_leg_link WHERE reservation_id = %s AND leg_id = %s",
            (unlink_res_id, unlink_leg_id),
            commit=True
        )
        st.success("Link safely removed! The original flight leg remains intact in the database.")

# ==========================================
# 4. PAYMENTS CRUD & LINKS
# ==========================================
elif choice == "Payments":
    st.header("💳 Payment Management & Linking")
    payments = execute_query("SELECT * FROM payment LIMIT 50")
    st.dataframe(payments, use_container_width=True)

    with st.expander("➕ Create New Payment"):
        pay_status = st.selectbox("Status", ["PAID", "PENDING", "REFUNDED"])
        amount = st.number_input("Amount", min_value=1.0, value=150.00, step=10.0)
        if st.button("Record Payment"):
            try:
                new_p_id = execute_query(
                    "INSERT INTO payment (payment_status_code, payment_date, payment_amount) VALUES (%s, NOW(), %s)",
                    (pay_status, amount),
                    commit=True
                )
                st.success(f"Payment recorded! Allocated ID: {new_p_id}")
            except Exception as e:
                st.error(f"Error recording payment: {e}")

    with st.expander("🔗 Link Payment to Reservation"):
        r_id_pay = st.number_input("Reservation ID", min_value=1, step=1, key="p_res")
        p_id_pay = st.number_input("Payment ID", min_value=1, step=1, key="p_pay")
        if st.button("Link Payment"):
            try:
                execute_query(
                    "INSERT INTO reservation_payment_link (reservation_id, payment_id) VALUES (%s, %s)",
                    (r_id_pay, p_id_pay),
                    commit=True
                )
                st.success("Payment successfully linked to reservation!")
            except Exception as e:
                st.error(f"Failed to link payment: {e}")

# ==========================================
# 5. AIRPORTS CRUD
# ==========================================
elif choice == "Airports":
    st.header("🛫 Airport Reference Records")
    airports = execute_query("SELECT * FROM airport LIMIT 50")
    st.dataframe(airports, use_container_width=True)

# ==========================================
# 6. FLIGHT SCHEDULES & LEGS
# ==========================================
elif choice == "Flight Schedules & Legs":
    st.header("🗓️ Flight Schedules & Legs")
    st.subheader("Schedules")
    st.dataframe(execute_query("SELECT * FROM flight_schedule LIMIT 25"), use_container_width=True)
    st.subheader("Actual Legs")
    st.dataframe(execute_query("SELECT * FROM flight_leg LIMIT 25"), use_container_width=True)

# ==========================================
# 7. FLIGHT COSTS
# ==========================================
elif choice == "Flight Costs":
    st.header("💰 Flight Costs Reference")
    st.dataframe(execute_query("SELECT * FROM flight_cost LIMIT 50"), use_container_width=True)