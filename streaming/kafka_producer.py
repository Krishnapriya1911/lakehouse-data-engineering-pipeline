import json
import os
import time
from pathlib import Path

# pyrefly: ignore [missing-import]
from confluent_kafka import Producer
from dotenv import load_dotenv


# ============================================================
# LOAD .ENV FROM PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

print(f"📁 Project root: {PROJECT_ROOT}")
print(f"📄 Loading environment file: {ENV_FILE}")

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f".env file not found at: {ENV_FILE}"
    )

load_dotenv(ENV_FILE, override=True)

print(
    "🔐 Environment loaded:",
    bool(os.getenv("KAFKA_BOOTSTRAP_SERVERS"))
)


# ============================================================
# KAFKA CONFIGURATION
# ============================================================

KAFKA_CONFIG = {
    "bootstrap.servers": os.environ["KAFKA_BOOTSTRAP_SERVERS"],
    "security.protocol": "SASL_SSL",
    "sasl.mechanism": "PLAIN",
    "sasl.username": os.environ["KAFKA_API_KEY"],
    "sasl.password": os.environ["KAFKA_API_SECRET"],
}

TOPIC = os.environ.get("KAFKA_TOPIC", "orders")


# ============================================================
# DELIVERY CALLBACK
# ============================================================

def delivery_report(err, msg):
    """Report whether a Kafka message was delivered successfully."""

    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        print(
            f"✅ Message delivered to "
            f"{msg.topic()} "
            f"[partition {msg.partition()}] "
            f"at offset {msg.offset()}"
        )


# ============================================================
# CREATE SAMPLE ORDER EVENT
# ============================================================

def create_order_event(order_id):
    """Create a sample order event."""

    return {
        "order_id": order_id,
        "customer_id": 1000 + order_id,
        "amount": round(100 + (order_id * 17.35), 2),
        "status": "SUCCESS",
        "order_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }


# ============================================================
# MAIN PRODUCER
# ============================================================

def main():

    print("\n🚀 Starting Kafka Producer...")
    print(f"📡 Topic: {TOPIC}")

    producer = Producer(KAFKA_CONFIG)

    try:

        for order_id in range(1, 11):

            order = create_order_event(order_id)

            message = json.dumps(order)

            producer.produce(
                TOPIC,
                key=str(order_id),
                value=message,
                callback=delivery_report,
            )

            producer.poll(0)

            print(f"📤 Sent: {message}")

            time.sleep(1)

        print("\n⏳ Waiting for Kafka delivery...")

        producer.flush()

        print("\n🎉 Kafka Producer completed successfully!")

    except Exception as e:

        print(f"\n❌ Producer error: {e}")

        producer.flush()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()