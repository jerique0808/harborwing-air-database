\# HarborWing Air Database \& Data Generator



This project implements a complete relational database schema and synthetic data generation pipeline for HarborWing Air.



\## Deliverables Included

\* `generate\_data.py` - Python script using `Faker` to populate all 11 tables.

\* `harborwing\_eer\_diagram.png` - High-resolution export of the EER Diagram.

\* `harborwing\_eer\_diagram.mwb` - Native MySQL Workbench database model\[cite: 3].



\## Database Schema (11 Tables)

1\. `airport`

2\. `passenger`

3\. `booking\_agent`

4\. `flight\_schedule`

5\. `flight\_leg`

6\. `calendar\_date`

7\. `flight\_cost`

8\. `reservation`

9\. `payment`

10\. `reservation\_payment\_link`

11\. `reservation\_leg\_link`



\## Setup \& Execution



\### Prerequisites

\* MySQL Server \& MySQL Workbench\[cite: 3]

\* Python 3.x

\* Required Python modules:

&#x20; ```bash

&#x20; pip install mysql-connector-python faker

