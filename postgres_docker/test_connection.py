# test_db_connection.py
#!/usr/bin/env python3

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def test_connection():
    connection_params = {
        'host': 'localhost',
        'port': 5433,  # Changed to port 5433
        'database': 'insors_db',
        'user': 'insors_demo',
        'password': 'p@ssW0rd!'
    }
    
    try:
        print("Testing database connection...")
        
        with psycopg2.connect(**connection_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"Connected to: {version['version']}")
                
                cursor.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name;")
                schemas = cursor.fetchall()
                print(f"Available schemas: {[s['schema_name'] for s in schemas]}")
                
                cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = 'json-master');")
                json_master_exists = cursor.fetchone()
                
                if json_master_exists['exists']:
                    print("json-master schema found - dump loaded successfully")
                    
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'json-master'
                        ORDER BY table_name;
                    """)
                    tables = cursor.fetchall()
                    if tables:
                        print(f"Tables in json-master: {[t['table_name'] for t in tables]}")
                    else:
                        print("No tables found in json-master schema")
                else:
                    print("json-master schema not found - dump may not be loaded")
                
                return True
                
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)