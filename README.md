# End-to-End Lakehouse Data Engineering Pipeline

## Project Overview

This project demonstrates a complete modern data engineering pipeline built using:

- Databricks
- PySpark
- Delta Lake
- Snowflake
- Kafka Streaming
- Medallion Architecture
- Data Quality Validation

The pipeline ingests raw transactional JSON data, processes it through Bronze, Silver, and Gold layers, validates data quality, exports curated datasets into Snowflake, and supports both batch and streaming workloads.

This project simulates a production-grade cloud data engineering workflow aligned with real-world enterprise data platforms.

---

# Architecture

```text
Raw JSON Data
      ↓
Bronze Layer (Raw Ingestion)
      ↓
Silver Layer (Cleaning & Validation)
      ↓
Gold Layer (Business Aggregations)
      ↓
Snowflake Data Warehouse
      ↓
Analytics / Reporting
```

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Databricks | Data Engineering Platform |
| PySpark | Distributed Data Processing |
| Delta Lake | ACID Storage Layer |
| Snowflake | Cloud Data Warehouse |
| Kafka | Real-Time Streaming |
| Python | ETL Development |
| SQL | Analytics & Validation |
| GitHub | Version Control |

---

# Project Structure

```text
lakehouse-pipeline/
│
├── configs/
├── dashboards/
├── data/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── raw/
│   └── warehouse/
│
├── docs/
├── monitoring/
├── notebooks/
├── reconciliation/
├── screenshots/
├── src/
│   └── utils/
│
├── streaming/
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Pipeline Stages

## 1. Schema Setup

Creates Delta Lake storage structure and initializes the Medallion Architecture folders.

### Key Features
- Folder initialization
- Delta storage preparation
- Warehouse setup

---

## 2. Bronze Layer Pipeline

Loads raw JSON data into Delta Bronze tables.

### Key Features
- Raw ingestion
- Schema inference
- Delta table creation
- Initial storage optimization

### Inputs
- customers.json
- orders.json

### Outputs
- bronze/customers
- bronze/orders

---

## 3. Silver Layer Pipeline

Cleans and transforms Bronze data into validated Silver tables.

### Key Features
- Null handling
- Deduplication
- Invalid record filtering
- Data type standardization

### Outputs
- silver/customers_clean
- silver/orders_clean

---

## 4. Gold Layer Pipeline

Builds analytical business datasets from Silver data.

### Key Features
- Revenue aggregation
- Customer analytics
- Business KPI generation

### Gold Tables
- TOP_CUSTOMERS
- DAILY_REVENUE
- REVENUE_BY_COUNTRY

---

## 5. Snowflake Export

Exports curated Gold tables into Snowflake for analytics and reporting.

### Key Features
- Snowflake integration
- Table overwrite
- Data warehouse loading

---

## 6. Kafka Streaming Pipeline

Implements real-time streaming ingestion using Kafka and Structured Streaming.

### Key Features
- Streaming ingestion
- Checkpointing
- Incremental processing
- Delta sink

---

## 7. Data Quality Checks

Validates data integrity before downstream consumption.

### Checks Performed
- Null customer IDs
- Duplicate orders
- Negative revenue validation
- Null amount checks

### Example Output

```text
DATA QUALITY PASSED
```

---

# Sample Business Metrics

## Top Customers

Tracks highest spending customers across all successful transactions.

## Daily Revenue

Provides aggregated revenue by transaction date.

## Revenue by Country

Provides geographic revenue distribution for analytics.

---

# Screenshots

## Workflow Execution

![Workflow](screenshots/workflow_execution.png)

## Snowflake Tables

![Snowflake](screenshots/snowflake_tables.png)

## Kafka Streaming

![Kafka](screenshots/kafka_streaming.png)

## Data Quality Checks

![Quality](screenshots/data_quality_pass.png)

---

# How to Run

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/lakehouse-pipeline.git
cd lakehouse-pipeline
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Execute Pipelines

Run notebooks in this order:

1. schema_setup
2. bronze_pipeline
3. silver_pipeline
4. gold_pipeline
5. snowflake_export
6. kafka_streaming_pipeline
7. data_quality_checks

---

# Key Data Engineering Concepts Demonstrated

- Medallion Architecture
- Batch ETL Pipelines
- Streaming ETL Pipelines
- Delta Lake
- Data Quality Validation
- Snowflake Integration
- Workflow Orchestration
- Distributed Processing
- Cloud Data Warehousing

---

# Resume-Relevant Skills

- PySpark
- Databricks
- Delta Lake
- Kafka
- Snowflake
- SQL
- Data Engineering
- ETL Pipelines
- Big Data Processing
- Workflow Automation

---

# Future Enhancements

- CI/CD integration
- Airflow orchestration
- dbt transformations
- Real-time dashboards
- Monitoring & alerting
- Unity Catalog integration
