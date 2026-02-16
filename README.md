# PostgreSQL CSV Data Loader

---

Automated CSV to PostgreSQL data loader.

---

Author: [Christian Velasco-Gallego](https://www.velascogallego.com/)

## Overview

Main functionalities include:

- CSV parsing with automatic column detection
- Configurable database connection parameters
- Bulk data insertion using COPY for performance

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
- PostgreSQL 16+ 
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
| `CSV.file_path` | Path to CSV file | `"data_processed.csv"` |
| `TABLE.name` | Target table name | `"data_processed"` |
| `TABLE.schema` | Database schema | `"public"` |
| `TABLE.primary_key` | Primary key column name (optional) | `"emergency_id"` |




