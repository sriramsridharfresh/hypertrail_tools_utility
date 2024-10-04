"""
Table verification Script
This script is to verify the tables are created in each database inside the rds machines
you can download the result using the command below
mysql -h rdsmachine1.use.feeds -u feedsmaster -pass < print.sql > output.txt
sql is 
SELECT         
    TABLE_SCHEMA AS DatabaseName,        
    TABLE_NAME AS TableName        
FROM         
    information_schema.TABLES        
WHERE         
    TABLE_TYPE = 'BASE TABLE'        
ORDER BY         
    TABLE_SCHEMA, TABLE_NAME; 
"""
import re

def read_db_tables(file_path):
    """Reads the file and returns a list of (db, table) pairs."""
    db_tables = {}
    with open(file_path, 'r') as f:
        next(f)  # Skip the header
        for line in f:
            db, table = line.strip().split()
            if db not in db_tables:
                db_tables[db] = []
            db_tables[db].append(table)
    return db_tables

def check_table_sequence(db_tables):
    """Checks that audit_dimensions tables are numbered from 0 to 63."""
    missing_tables = {}
    extra_tables = {}

    for db, tables in db_tables.items():
        if db in ["mysql","performance_schema","sys"]:
            break
        # Filter tables matching the pattern
        audit_tables = [t for t in tables if re.match(r'^extended_dashboard_dimensions_\d+$', t)]
        
        # Extract numbers and convert to integers
        table_numbers = sorted(int(re.findall(r'\d+', t)[0]) for t in audit_tables)
        
        # Check if the sequence is 0 to 63
        expected_numbers = list(range(64))
        missing = set(expected_numbers) - set(table_numbers)
        extra = set(table_numbers) - set(expected_numbers)

        if missing:
            missing_tables[db] = sorted(missing)
        if extra:
            extra_tables[db] = sorted(extra)

    return missing_tables, extra_tables

def main():
    file_path = 'Path/to/output.txt'
    
    # Read DB and table names
    db_tables = read_db_tables(file_path)
    
    # Check for missing or extra tables in the 0-63 range
    missing_tables, extra_tables = check_table_sequence(db_tables)
    
    if missing_tables:
        for db, missing in missing_tables.items():
            print(f"In Database '{db}', these dimensions tables are missing:")
            for number in missing:
                print(f" - dimensions_{number}")
    
    if extra_tables:
        for db, extra in extra_tables.items():
            print(f"In Database '{db}', these dimensions tables are extra:")
            for number in extra:
                print(f" - dimensions_{number}")

    if not missing_tables and not extra_tables:
        print("All databases have the correct dimensions_0 to dimensions_63 tables.")

if __name__ == '__main__':
    main()
