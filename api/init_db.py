import mysql.connector
import os
import time
from faker import Faker

# Database connection details from environment variables
DB_HOST = os.environ.get('DB_HOST', 'db') # Use service name 'db' from docker-compose
DB_USER = os.environ.get('MYSQL_USER', 'app_user')
DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
DB_NAME = os.environ.get('MYSQL_DATABASE', 'company_db')
DB_PORT = os.environ.get('DB_PORT', 3306)

# --- Database Connection Logic with Retry ---
def get_db_connection(retries=10, delay=5):
    """Attempts to connect to the database with retries."""
    attempt = 1
    while attempt <= retries:
        try:
            print(f"Attempting to connect to database (Attempt {attempt}/{retries})...")
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT
            )
            print("Database connection successful!")
            return conn
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            if attempt == retries:
                print("Max retries reached. Could not connect to the database.")
                return None
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            attempt += 1
    return None # Should not be reached if retries > 0

# --- Table Creation and Data Population ---
def setup_database():
    """Creates the table if it doesn't exist and populates it if empty."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None or not conn.is_connected():
            print("Failed to establish database connection for setup.")
            return # Exit if connection failed

        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                department VARCHAR(255)
            ) ENGINE=InnoDB;
        """)
        conn.commit()
        print("Table 'employees' ensured to exist.")

        # Check if table is empty
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]

        if count == 0:
            print("Table 'employees' is empty. Populating with 500 random entries...")
            fake = Faker()
            employees_data = []
            departments = [fake.job() for _ in range(15)] # Create some sample departments

            for _ in range(500):
                name = fake.name()
                department = fake.random_element(elements=departments)
                employees_data.append((name, department))

            # Insert data
            sql = "INSERT INTO employees (name, department) VALUES (%s, %s)"
            cursor.executemany(sql, employees_data)
            conn.commit()
            print(f"Successfully inserted {len(employees_data)} random employees.")
        else:
            print(f"Table 'employees' already contains {count} records. No population needed.")

    except mysql.connector.Error as err:
        print(f"Database setup error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed after setup.")

# --- Main execution block ---
if __name__ == "__main__":
    print("Running Database Initialization...")
    setup_database()
    print("Database Initialization Finished.")
