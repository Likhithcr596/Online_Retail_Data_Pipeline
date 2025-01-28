import json
import time
import boto3
from redis import Redis
from botocore.exceptions import ClientError

# Set dummy credentials for LocalStack
import os
os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"

# Direct connection configuration
sqs = boto3.client("sqs", endpoint_url="http://localstack:4566", region_name="us-east-1")
redis_client = Redis(host="redis", port=6379, db=0)

# Create the SQS queue if it doesn't exist
response = sqs.create_queue(QueueName="orders-queue")
QUEUE_URL = response["QueueUrl"]  # Get the Queue URL from the response


def validate_event(event):
    """ Validate required fields and cross-check order value """
    try:
        # Validate user_id
        user_id = event.get("user_id")
        if not user_id or not isinstance(user_id, str) or user_id.strip() == "":
            raise ValueError("Invalid 'user_id': Cannot be blank or null")

        # Validate order_id
        order_id = event.get("order_id")
        if not order_id or not isinstance(order_id, str) or order_id.strip() == "":
            raise ValueError("Invalid 'order_id': Cannot be blank or null")

        # Validate and handle order_value
        order_value = event.get("order_value")
        if order_value is None or order_value == "":
            print(f"'order_value' is null or blank, setting to 0 for order_id {order_id}")
            order_value = 0.0
        elif not isinstance(order_value, (int, float)) or order_value < 0:
            raise ValueError("Invalid 'order_value': Must be positive")

        event["order_value"] = float(order_value)  # Normalize the value

        # Cross-check order_value with sum of items
        items = event.get("items", [])
        if not isinstance(items, list):
            raise ValueError("Invalid 'items': Must be a list")

        calculated_order_value = sum(
            item["quantity"] * item["price_per_unit"]
            for item in items
            if "quantity" in item and "price_per_unit" in item
        )

        # Allow correction of mismatched order_value
        if abs(calculated_order_value - event["order_value"]) > 0.01:  # Allow small floating-point errors
            print(
                f"Mismatch in 'order_value' for order_id {order_id}: "
                f"Expected {calculated_order_value}, Found {event['order_value']}. Correcting it."
            )
            event["order_value"] = calculated_order_value

        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False


def process_event(event):
    """ Process incoming event to update Redis cache """
    if not validate_event(event):
        print(f"Invalid event: {event}")
        return

    order_id = event["order_id"]
    user_id = event["user_id"]
    order_value = float(event["order_value"])
    order_timestamp = event.get("order_timestamp", "Unknown")
    items = event.get("items", [])
    shipping_address = event.get("shipping_address", "Unknown")
    payment_method = event.get("payment_method", "Unknown")

    # Log essential information for aggregation
    print(f"Processing order {order_id} for user {user_id} at {order_timestamp}, value: {order_value}")

    # Update individual user statistics
    redis_client.incrbyfloat(f"user:{user_id}:cumulative_spend", order_value)
    redis_client.incr(f"user:{user_id}:total_orders", 1)

    # Update global statistics
    redis_client.incrbyfloat("global:cumulative_spend", order_value)
    redis_client.incr("global:total_orders", 1)

    # Process items within the order
    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]
        price_per_unit = item["price_per_unit"]

        # Update product statistics
        redis_client.incrbyfloat(f"product:{product_id}:total_sales", quantity * price_per_unit)
        redis_client.incr(f"product:{product_id}:total_quantity_sold", quantity)

    # Store shipping address and payment method
    redis_client.set(f"user:{user_id}:shipping_address", shipping_address)
    redis_client.set(f"user:{user_id}:payment_method", payment_method)


def consume_sqs():
    """ Consume messages from SQS and process them """
    while True:
        try:
            # Poll for messages from the SQS queue
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )

            if "Messages" in response:
                for message in response["Messages"]:
                    event = json.loads(message["Body"])
                    process_event(event)
                    
                    # Delete message from the queue after processing
                    sqs.delete_message(
                        QueueUrl=QUEUE_URL,
                        ReceiptHandle=message["ReceiptHandle"]
                    )

        except ClientError as e:
            print(f"Error: {e} from consume_sqs")
        time.sleep(1)


if __name__ == "__main__":
    consume_sqs()
