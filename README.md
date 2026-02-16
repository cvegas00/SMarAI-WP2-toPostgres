# PostgreSQL CSV Data Loader

---

Automated CSV to PostgreSQL data loader with intelligent type inference and configurable primary key support. This tool streamlines the process of importing large CSV files into PostgreSQL databases with automatic schema creation.

---

## Overview

This project provides a simple yet powerful solution for loading CSV data into PostgreSQL databases:

- **Automatic type inference**: Intelligently detects column data types (INTEGER, DOUBLE PRECISION, TEXT, TIMESTAMP)
- **Configurable primary keys**: Define primary key columns through configuration file
- **High-performance loading**: Uses PostgreSQL's COPY command for optimal performance
- **Table management**: Automatically drops and recreates tables for fresh data loads
- **Type-specific handling**: Special handling for emergency_id and fecha_real columns

Main functionalities include:

- CSV parsing with automatic column detection
- Intelligent data type inference from sample data
- Configurable database connection parameters
- Primary key constraint support
- Bulk data insertion using COPY for performance
- Transaction management with rollback support

## Project Structure

```
PostgreSQL/
│
├── config.py                        # Database and table configuration
├── load_csv_to_postgresql.py       # Main CSV loader script
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## Installation

### Requirements

- Python 3.8+
- PostgreSQL 16+ (tested with PostgreSQL 18)
- Dependencies specified in `requirements.txt`

**Key packages:**

- **psycopg2**: PostgreSQL adapter for Python

### Setup

```bash
# Create and activate virtual environment (optional)
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### PostgreSQL Configuration

The script requires PostgreSQL to be configured with `md5` authentication. Update your `pg_hba.conf` file:

```conf
# IPv4 local connections:
host    all             all             127.0.0.1/32            md5
# IPv6 local connections:
host    all             all             ::1/128                 md5
```

After modifying `pg_hba.conf`, restart PostgreSQL service.

## Configuration

Edit `config.py` to configure your database connection and table settings:

```python
POSTGRESQL = {
    "host": "localhost",
    "port": 5432,
    "database": "SmarAI",
    "user": "postgres",
    "password": "postgres",
}

CSV = {
    "file_path": "data_processed.csv",
}

TABLE = {
    "name": "data_processed",
    "schema": "public",
    "primary_key": "emergency_id",  # Optional: set to None for no primary key
}
```

### Configuration Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `POSTGRESQL.host` | PostgreSQL server hostname | `"localhost"` |
| `POSTGRESQL.port` | PostgreSQL server port | `5432` |
| `POSTGRESQL.database` | Target database name | `"SmarAI"` |
| `POSTGRESQL.user` | Database username | `"postgres"` |
| `POSTGRESQL.password` | Database password | `"postgres"` |
| `CSV.file_path` | Path to CSV file (relative or absolute) | `"data_processed.csv"` |
| `TABLE.name` | Target table name | `"data_processed"` |
| `TABLE.schema` | Database schema | `"public"` |
| `TABLE.primary_key` | Primary key column name (optional) | `"emergency_id"` |

## Usage

### Running the Script

```bash
python load_csv_to_postgresql.py
```

### What the Script Does

1. **Reads CSV file**: Loads the CSV file specified in configuration
2. **Infers column types**: Analyzes first 100 rows to determine data types
3. **Connects to PostgreSQL**: Establishes connection using configured credentials
4. **Drops existing table**: If table exists, drops it (WARNING: data loss)
5. **Creates new table**: Generates CREATE TABLE statement with inferred types and primary key
6. **Loads data**: Uses COPY command for high-performance bulk insert
7. **Verifies**: Counts and reports number of rows inserted

### Type Inference Rules

The script automatically infers column types based on these rules:

| Column Name | Inferred Type | Logic |
|-------------|---------------|-------|
| `emergency_id` | `INTEGER` | Always treated as integer ID |
| `fecha_real` | `TIMESTAMP` | Always treated as timestamp |
| Other columns | `INTEGER` | If all non-empty values are integers |
| Other columns | `DOUBLE PRECISION` | If any value contains decimal point |
| Other columns | `TEXT` | Default fallback for all other cases |

### Example Output

```
Detected 127 columns in CSV file.
Table "public"."data_processed" exists. Dropping it...
Table dropped successfully.
Creating table...
Table created successfully.
Inserting data from CSV...
Successfully inserted 39,213 rows into "public"."data_processed".
Connection closed.
```

## Input Data Format

The CSV file should:

- Have a header row with column names
- Use standard CSV format (comma-separated)
- Be encoded in UTF-8
- Contain consistent data types per column

Example CSV structure:
```csv
emergency_id,fecha_real,emergencia_latitud,emergencia_longitud,t2m_minus_0,...
507269,2010-01-03 20:06:00,0.622,0.103,0.484,...
507480,2010-01-04 16:55:00,0.622,0.100,0.477,...
```

## SQL Queries

After loading, retrieve data using standard SQL:

```sql
-- Retrieve all data
SELECT * FROM public.data_processed;

-- Retrieve specific columns
SELECT emergency_id, fecha_real, emergencia_latitud
FROM public.data_processed;

-- Filter by date range
SELECT * FROM public.data_processed
WHERE fecha_real BETWEEN '2010-01-01' AND '2010-12-31'
ORDER BY fecha_real;

-- Aggregate statistics
SELECT
    COUNT(*) as total_records,
    MIN(fecha_real) as earliest_date,
    MAX(fecha_real) as latest_date
FROM public.data_processed;
```

## Troubleshooting

### Connection Issues

**Error: `psycopg2.OperationalError`**

- Verify PostgreSQL service is running
- Check `pg_hba.conf` authentication method (should be `md5` not `scram-sha-256`)
- Verify database exists: `psql -l` or connect to `postgres` database first
- Check credentials in `config.py`

### Performance Issues

For large CSV files (>1 million rows):

- The script uses COPY command which is already optimized
- Consider increasing PostgreSQL's `maintenance_work_mem` setting
- Disable indexes temporarily if adding to existing table

### Type Inference Issues

If types are incorrectly inferred:

- Check first 100 rows have representative data
- Modify `infer_column_type()` function in `load_csv_to_postgresql.py`
- Add custom type rules for specific column names

## Technical Notes

- **Transaction safety**: All operations are wrapped in transactions with rollback on error
- **Table recreation**: Script drops existing table - ensure you have backups if needed
- **Primary key uniqueness**: CSV must have unique values in primary key column
- **Performance**: COPY command is fastest method for bulk loading (typically 10-100x faster than INSERT)
- **Encoding**: CSV must be UTF-8 encoded

## Author

Christian Velasco-Gallego
[www.velascogallego.com](https://www.velascogallego.com/)

## License

This project is provided as-is for data loading purposes.
