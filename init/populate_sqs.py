import json
import boto3
import time
import random
from datetime import datetime, timedelta

# Direct connection configuration
sqs = boto3.client("sqs", endpoint_url="http://localhost:4566", region_name="us-east-1")

QUEUE_URL = "http://localhost:4566/000000000000/orders-queue"

def generate_random_order_id():
    """Generate a random order ID."""
    return f"ORD{random.randint(1000, 9999)}"

def generate_random_user_id():
    """Generate a random user ID."""
    return f"U{random.randint(1, 20)}"

def generate_random_order_value():
    """Generate a random order value."""
    return round(random.uniform(20.0, 200.0), 2)

def generate_random_items():
    """Generate a list of items for the order."""
    products = ["P001", "P002", "P003", "P004"]
    items = []
    
    for _ in range(random.randint(1, 3)):  # Order can have 1 to 3 items
        product_id = random.choice(products)
        quantity = random.randint(1, 5)  # Quantity between 1 and 5
        price_per_unit = round(random.uniform(10.0, 100.0), 2)  # Random price per unit between 10 and 100
        items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price_per_unit": price_per_unit
        })
    
    return items

def generate_random_shipping_address():
    """Generate a random shipping address."""
    addresses = [
        "123 Main St, Springfield",
        "456 Oak Ave, Rivertown",
        "789 Pine Rd, Lakeside",
        "101 Elm St, Hill Valley"
    ]
    return random.choice(addresses)

def generate_random_payment_method():
    """Generate a random payment method."""
    return random.choice(["CreditCard", "DebitCard", "PayPal", "CashOnDelivery"])

def generate_random_timestamp():
    """Generate a random order timestamp."""
    base_time = datetime.utcnow() - timedelta(days=random.randint(0, 30))  # Orders in the last 30 days
    return base_time.strftime("%Y-%m-%dT%H:%M:%SZ")

def populate_sample_events():
    for i in range(1, 11):  # Simulating 10 events
        order_event = {
            "order_id": generate_random_order_id(),
            "user_id": generate_random_user_id(),
            "order_timestamp": generate_random_timestamp(),
            "order_value": generate_random_order_value(),
            "items": generate_random_items(),
            "shipping_address": generate_random_shipping_address(),
            "payment_method": generate_random_payment_method()
        }
        
        # Send the generated order event to the SQS queue
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(order_event)
        )
        print(f"Sent order event for user {order_event['user_id']} with order_id {order_event['order_id']}")
        time.sleep(1)

if __name__ == "__main__":
    populate_sample_events()
