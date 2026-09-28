# Architecture Specification: Chronicle Ingestion & Analytics Platform

This document outlines the software architecture, design principles, component interactions, and data flow of the Chronicle platform.

---

## 1. High-Level Architectural Diagram

```mermaid
flowchart TD
    subgraph DataSources["Data Sources Layer"]
        CSV[CSV Files]
        XLS[Excel Spreadsheets]
        JSON[JSON Feeds / APIs]
        REST[External REST APIs]
    end

    subgraph Ingestion["Ingestion & ETL Layer"]
        EX[Extractor Engine]
        VAL{Validator Engine}
        TR[Transformer Engine]
        DLQ[(Dead-Letter Quarantine)]
        LOG[Structured JSON Logger]
    end

    subgraph Storage["Storage & Persistence Layer"]
        PG[(PostgreSQL 16 / SQLite)]
        S3[(Amazon S3 Data Lake)]
    end

    subgraph BackendAPI["Backend API & Services Layer (FastAPI)"]
        AUTH[JWT & RBAC Security]
        ING_SVC[Ingestion Service]
        AN_SVC[Analytics Service]
        AUDIT[Audit Service]
    end

    subgraph Presentation["Presentation & BI Layer"]
        DASH[Web Analytics Dashboard]
        PBI[Power BI DirectQuery]
        SWAG[OpenAPI / Swagger Docs]
    end

    CSV --> EX
    XLS --> EX
    JSON --> EX
    REST --> EX

    EX --> VAL
    VAL -- "Invalid Records" --> DLQ
    VAL -- "Valid Records" --> TR
    TR --> PG
    EX -.-> S3
    DLQ --> PG
    LOG -.-> BackendAPI

    PG <--> AN_SVC
    PG <--> ING_SVC
    PG <--> AUDIT

    AUTH --> ING_SVC
    AUTH --> AN_SVC

    AN_SVC --> DASH
    AN_SVC --> PBI
    AN_SVC --> SWAG
```

---

## 2. End-to-End Pipeline Execution Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Client as User / Scheduler / API
    participant API as FastAPI Backend (/upload)
    participant Pipe as ETL Pipeline Orchestrator
    participant Ext as Extractor Strategy
    participant Val as Validator Engine
    participant Trans as Transformer Engine
    participant Loader as Relational Loader
    participant DB as PostgreSQL Database
    participant DLQ as Quarantine Table

    Client->>API: POST /upload (file, domain="retail")
    API->>Pipe: run(source, domain, source_type)
    Pipe->>DB: INSERT IngestionBatch (status="running")
    
    Pipe->>Ext: extract(file_path)
    Ext-->>Pipe: raw_dataframe
    
    Pipe->>Val: validate(raw_dataframe)
    Val-->>Pipe: ValidationResult (valid_df, rejected_records)
    
    opt Has Rejected Records
        Pipe->>Loader: quarantine(rejected_records)
        Loader->>DLQ: INSERT INTO rejected_records
    end
    
    Pipe->>Trans: transform(valid_df)
    Note over Trans: Dates standardized, Currency to USD,<br/>Derived revenue/taxes, Tier calculation
    Trans-->>Pipe: transformed_df
    
    Pipe->>Loader: load(transformed_df)
    Loader->>DB: Bulk Upsert Entities (Customers, Orders, Items, Transactions)
    DB-->>Loader: Commit Transaction
    
    Pipe->>DB: UPDATE IngestionBatch (status="completed", counts, duration)
    Pipe-->>API: Batch Execution Summary JSON
    API-->>Client: 200 OK (batch_id, valid, rejected, duration)
```

---

## 3. Core Architectural Principles

1. **Strategy Pattern for Extensibility**:
   Extractors (`CSVExtractor`, `ExcelExtractor`, `JSONExtractor`, `RestAPIExtractor`), Validators (`RetailValidator`, `BankingValidator`), and Transformers (`RetailTransformer`, `BankingTransformer`) implement common abstract base classes. Adding a new data source or business domain requires zero modifications to the core pipeline orchestrator.

2. **Strict Data Quality Gatekeeping**:
   Data corruption is stopped at the ingestion boundary. Valid records proceed to normalization and relational persistence, while invalid records are automatically quarantined into the `rejected_records` dead-letter table with the original row payload and explicit violation diagnostics.

3. **Separation of Concerns (Clean Architecture)**:
   - **API Layer**: Route handling, request validation, authentication, and HTTP response formatting.
   - **Service Layer**: Business logic, analytical aggregations, and audit logging.
   - **ETL Engine**: Data extraction, transformation algorithms, currency conversions, and bulk loading.
   - **Data Access Layer**: Normalized SQLAlchemy 2.0 ORM models and Alembic migrations.

4. **Database Portability**:
   Engine configurations automatically support production PostgreSQL (`postgresql+psycopg://...`) with connection pooling and local zero-configuration SQLite (`sqlite:///...`) for development and automated testing.
