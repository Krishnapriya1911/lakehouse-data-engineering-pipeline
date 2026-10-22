# Lakehouse Data Engineering Pipeline

**[Open the live batch explorer](https://lakehouse-pipeline-explorer.krishnapriyakella07.chatgpt.site)** — synthetic reference outputs, quality counts and revenue charts. This demo does not host the full streaming/cloud stack.

A portfolio implementation of batch and streaming data pipelines using **Python, PySpark, Delta Lake, Databricks, Kafka and Snowflake**. Customer and order data move through Bronze, Silver and Gold layers to produce analytics tables, with separate quality and reconciliation notebooks.

[Architecture](docs/architecture.md) · [Data flow](docs/data_flow.md) · [Batch notebooks](notebooks) · [Sample outputs](data/gold)

## What to review

| Engineering area | Implementation |
| --- | --- |
| Raw ingestion | [Bronze pipeline](notebooks/bronze_pipeline.ipynb) reads customer and order JSON into Delta tables |
| Cleaning | [Silver pipeline](notebooks/silver_pipeline.ipynb) normalizes records and removes invalid or duplicate data |
| Analytics | [Gold pipeline](notebooks/gold_pipeline.ipynb) calculates daily revenue, top customers and revenue by country |
| Data quality | [Quality notebook](notebooks/data_quality_checks.ipynb) reports null IDs, null amounts, duplicates and negative amounts |
| Reconciliation | [Reconciliation notebook](notebooks/reconciliation_pipeline.ipynb) compares Bronze and Silver counts with rejected and duplicate records |
| Streaming | [Local producer](streaming/kafka_producer.py) sends synthetic orders to Kafka; the [Databricks consumer](notebooks/kafka_streaming_consumer.ipynb) parses events and writes Delta with a checkpoint |
| Warehouse integration | [Snowflake loader](notebooks/snowflake_loader.ipynb) exports Gold tables through the Spark connector |
| Orchestration | [Orchestration notebook](notebooks/pipeline_orchestration.ipynb) runs the batch notebook sequence |

The streaming consumer uses an `availableNow` trigger: it processes available events and exits.

## Inspect without cloud credentials

The repository includes small example datasets and CSV outputs for review:

- [Raw customers](data/raw/customers.json) and [raw orders](data/raw/orders.json)
- [Daily revenue](data/gold/daily_revenue.csv)
- [Top customers](data/gold/top_customers.csv)
- [Revenue by country](data/gold/revenue_by_country.csv)

These files illustrate the data shapes and outputs; they are not a throughput benchmark or evidence of a running cloud deployment.

## Run the local reference demonstration

No cloud credentials or third-party Python packages are required:

```bash
python3 scripts/run_local_demo.py
python3 -m unittest discover -s tests -v
python3 -m http.server 8080 --directory artifacts/local-demo
```

Open `http://localhost:8080` to explore generated revenue charts, quality counts and CSV downloads. This separate SQLite reference follows the batch notebook rules; it does not execute Spark, Delta Lake, Kafka or Snowflake. Conflicting duplicate order IDs keep the first source row deterministically. The original notebook's distributed deduplication can choose a different row for conflicting duplicates.

The runner reads the committed raw JSON and writes only under `artifacts/local-demo/`. The small CSVs already in `data/bronze`, `data/silver` and `data/gold` are separate illustrative fixtures, not exports of this larger raw dataset.

## Run the batch pipeline in Databricks

### Prerequisites

- A Databricks workspace with Spark, Delta Lake and access to a Unity Catalog Volume.
- Permission to read and write a dedicated demo Volume.
- Snowflake access and a compatible Snowflake Spark connector for the warehouse export steps.

```bash
git clone https://github.com/Krishnapriya1911/lakehouse-data-engineering-pipeline.git
cd lakehouse-data-engineering-pipeline
```

1. Import the notebooks from `notebooks/` into Databricks.
2. Upload `data/raw/customers.json` and `data/raw/orders.json` into your demo Volume root.
3. Set each notebook's `base_path` widget to that Volume path. Editing `configs/app_config.yaml` alone does not reconfigure the notebooks.
4. Run `schema_setup`, `bronze_pipeline`, `silver_pipeline`, then `gold_pipeline`.
5. Inspect the Gold Delta tables and run `data_quality_checks` and `reconciliation_pipeline` to review the quality reports.
6. Configure the Snowflake environment variables described in [the configuration reference](configs/app_config.yaml), install the compatible Spark connector, and run `snowflake_loader` or `snowflake_export`.

Use a demo Volume: the Bronze and Gold notebooks remove or overwrite their output paths when rerun. The orchestration notebook includes Snowflake export, so configure Snowflake before running the full sequence.

## Run the Kafka producer locally

Use a Python virtual environment. The producer imports `confluent_kafka`, which is not currently included in `requirements.txt`, so install it explicitly:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install confluent-kafka python-dotenv
```

Create a local `.env` file in the repository root with these keys, using your own Kafka credentials:

```dotenv
KAFKA_BOOTSTRAP_SERVERS=
KAFKA_API_KEY=
KAFKA_API_SECRET=
KAFKA_TOPIC=orders
```

```bash
python streaming/kafka_producer.py
```

In Databricks, open `notebooks/kafka_streaming_consumer.ipynb`, configure the Kafka widgets, and update its output and checkpoint paths to your demo Volume before running. Use a Kafka-enabled runtime and keep credentials out of committed notebooks and output cells.

`streaming/streaming_pipeline.py` is a pointer to the Databricks consumer. Installing `requirements.txt` locally does not provide Databricks' `dbutils` or configure its cloud services.

## Repository guide

| Directory | Contents |
| --- | --- |
| `notebooks/` | Databricks ingestion, transformation, streaming and validation notebooks |
| `streaming/` | Local Kafka producer and consumer entry-point notes |
| `src/utils/` | Data generation and quality helpers |
| `configs/` | Schema and non-secret configuration references |
| `data/` | Example raw data and exported layer outputs |
| `monitoring/` | Monitoring helper |
| `docs/` | Architecture and data-flow documentation |

## Current scope and next steps

This is a learning and portfolio project. Cloud execution requires the accounts and configuration above. Next improvements include reproducible local execution, automated assertions for quality failures, configurable streaming paths, and CI validation. Performance, availability and anomaly-detection results have not been benchmarked here.
