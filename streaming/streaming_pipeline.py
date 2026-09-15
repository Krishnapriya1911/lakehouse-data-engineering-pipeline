"""
Kafka Streaming Pipeline

The Kafka streaming consumer runs in Databricks:
    notebooks/kafka_streaming_consumer.ipynb

Architecture:
    Kafka Producer
        -> Confluent Cloud
        -> Databricks Structured Streaming
        -> Delta Lake

The Databricks notebook uses:
- Kafka SASL/SSL authentication
- JSON parsing
- Spark Structured Streaming
- AvailableNow trigger
- Delta Lake sink
- Checkpointing

Run the producer locally with:
    python streaming/kafka_producer.py

Run the consumer from the Databricks notebook:
    notebooks/kafka_streaming_consumer.ipynb
"""


def main() -> None:
    print(
        "Kafka streaming consumer is implemented in "
        "notebooks/kafka_streaming_consumer.ipynb."
    )


if __name__ == "__main__":
    main()