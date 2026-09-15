import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()

# ============================================
# CONFIG
# ============================================

NUM_CUSTOMERS = 10000
NUM_ORDERS = 100000

countries = [
    "India", "USA", "Canada", "Germany", "UK",
    "Australia", "France", "Japan", "Brazil", "Singapore"
]

statuses = ["SUCCESS", "FAILED", "PENDING"]

# ============================================
# GENERATE CUSTOMERS
# ============================================

customers = []

for customer_id in range(1, NUM_CUSTOMERS + 1):

    customers.append({
        "customer_id": customer_id,
        "name": fake.name(),
        "country": random.choice(countries)
    })

customers_df = pd.DataFrame(customers)

# ============================================
# GENERATE ORDERS
# ============================================

orders = []

start_date = datetime(2025, 1, 1)

for order_id in range(1, NUM_ORDERS + 1):

    customer_id = random.randint(1, NUM_CUSTOMERS)

    amount = round(random.uniform(10, 5000), 2)

    status = random.choices(
        statuses,
        weights=[0.85, 0.10, 0.05]
    )[0]

    order_time = start_date + timedelta(
        days=random.randint(0, 365),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

    # FAILED transactions may have negative amount
    if status == "FAILED":
        amount = -abs(amount)

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "status": status,
        "order_time": order_time.strftime("%Y-%m-%d %H:%M:%S")
    })

orders_df = pd.DataFrame(orders)

# ============================================
# ADD DUPLICATES
# ============================================

duplicate_rows = orders_df.sample(500)

orders_df = pd.concat(
    [orders_df, duplicate_rows],
    ignore_index=True
)

# ============================================
# ADD NULLS
# ============================================

null_indices = random.sample(
    range(len(orders_df)),
    300
)

orders_df.loc[null_indices, "customer_id"] = None

# ============================================
# CREATE OUTPUT DIRECTORY
# ============================================

output_dir = "data/raw"

os.makedirs(output_dir, exist_ok=True)

# ============================================
# SAVE FILES
# ============================================

customers_df.to_json(
    f"{output_dir}/customers_large.json",
    orient="records",
    indent=2
)

orders_df.to_json(
    f"{output_dir}/orders_large.json",
    orient="records",
    indent=2
)

print("Large synthetic datasets generated successfully!")

print(f"Customers: {len(customers_df)}")
print(f"Orders: {len(orders_df)}")