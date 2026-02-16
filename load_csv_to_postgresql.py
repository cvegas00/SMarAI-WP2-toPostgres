import csv
import os
import psycopg2
from psycopg2 import sql
from config import POSTGRESQL, CSV, TABLE


def get_connection():
    return psycopg2.connect(
        host=POSTGRESQL["host"],
        port=POSTGRESQL["port"],
        database=POSTGRESQL["database"],
        user=POSTGRESQL["user"],
        password=POSTGRESQL["password"],
    )


def infer_column_type(column_name, sample_values):
    """Infer PostgreSQL column type from column name and sample values."""
    if column_name == "emergency_id":
        return "INTEGER"
    if column_name == "fecha_real":
        return "TIMESTAMP"

    non_empty = [v for v in sample_values if v.strip() != ""]
    if not non_empty:
        return "TEXT"

    for val in non_empty:
        try:
            int_val = int(float(val))
            if float(val) == int_val and "." not in val:
                continue
            else:
                return "DOUBLE PRECISION"
        except ValueError:
            return "TEXT"

    return "INTEGER"


def build_create_table_sql(table_name, schema, columns, column_types, primary_key=None):
    """Build the CREATE TABLE SQL statement."""
    col_defs = []
    for col, col_type in zip(columns, column_types):
        safe_col = f'"{col}"'
        # Add PRIMARY KEY constraint if this column is the primary key
        if primary_key and col == primary_key:
            col_defs.append(f"    {safe_col} {col_type} PRIMARY KEY")
        else:
            col_defs.append(f"    {safe_col} {col_type}")

    cols_sql = ",\n".join(col_defs)
    return f'CREATE TABLE "{schema}"."{table_name}" (\n{cols_sql}\n);'


def main():
    table_name = TABLE["name"]
    schema = TABLE["schema"]
    primary_key = TABLE.get("primary_key")  # Optional primary key column
    csv_file = CSV["file_path"]
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_file)

    # Read CSV to get columns and sample data for type inference
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        columns = next(reader)

        # Collect sample values (up to 100 rows) for type inference
        sample_rows = []
        for i, row in enumerate(reader):
            sample_rows.append(row)
            if i >= 99:
                break

    # Infer column types from sample data
    column_types = []
    for col_idx, col_name in enumerate(columns):
        sample_vals = [row[col_idx] for row in sample_rows if col_idx < len(row)]
        column_types.append(infer_column_type(col_name, sample_vals))

    print(f"Detected {len(columns)} columns in CSV file.")

    # Connect to PostgreSQL
    conn = get_connection()
    conn.autocommit = False
    cur = conn.cursor()

    try:
        # Check if table exists and drop it
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s);",
            (schema, table_name),
        )
        table_exists = cur.fetchone()[0]

        if table_exists:
            print(f'Table "{schema}"."{table_name}" exists. Dropping it...')
            cur.execute(sql.SQL("DROP TABLE {}.{}").format(
                sql.Identifier(schema), sql.Identifier(table_name)
            ))
            conn.commit()
            print("Table dropped successfully.")
        else:
            print(f'Table "{schema}"."{table_name}" does not exist. Creating it...')

        # Create table
        create_sql = build_create_table_sql(table_name, schema, columns, column_types, primary_key)
        print("Creating table...")
        cur.execute(create_sql)
        conn.commit()
        print("Table created successfully.")

        # Insert data using COPY for performance
        print("Inserting data from CSV...")
        with open(csv_path, "r", encoding="utf-8") as f:
            cur.copy_expert(
                sql.SQL("COPY {}.{} FROM STDIN WITH (FORMAT csv, HEADER true)").format(
                    sql.Identifier(schema), sql.Identifier(table_name)
                ),
                f,
            )
        conn.commit()

        # Verify row count
        cur.execute(sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
            sql.Identifier(schema), sql.Identifier(table_name)
        ))
        row_count = cur.fetchone()[0]
        print(f'Successfully inserted {row_count} rows into "{schema}"."{table_name}".')

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()
        print("Connection closed.")


if __name__ == "__main__":
    main()
