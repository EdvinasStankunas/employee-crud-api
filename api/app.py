import os
import mysql.connector
from flask import Flask, request, jsonify
from functools import wraps
from dotenv import load_dotenv
from init_db import get_db_connection, setup_database # Import helper functions

load_dotenv() # Load environment variables from .env file (optional for local dev)

app = Flask(__name__)

# --- Configuration ---
# Load sensitive data from environment variables
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('MYSQL_USER', 'app_user')
DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
DB_NAME = os.environ.get('MYSQL_DATABASE', 'company_db')
DB_PORT = os.environ.get('DB_PORT', 3306)
API_KEY = os.environ.get('API_KEY', 'default-secret-key') # Get API Key

# --- Database Connection Pool (Example - more robust for high traffic) ---
# For simplicity in this example, we'll use the get_db_connection from init_db
# In a real app, consider a connection pool like dbcp or SQLAlchemy's pool

# --- API Key Authorization ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-KEY')
        if not provided_key or provided_key != API_KEY:
            return jsonify({"error": "Unauthorized - Invalid or missing API Key"}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Error Handling ---
@app.errorhandler(mysql.connector.Error)
def handle_db_errors(err):
    print(f"Database Error: {err}")
    return jsonify({"error": "Database operation failed", "details": str(err)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "details": str(error)}), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error"}), 500

# --- Helper to execute queries ---
def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    conn = None
    cursor = None
    result = None
    try:
        conn = get_db_connection() # Use the connection function with retry
        if conn is None:
             raise mysql.connector.Error("Failed to connect to the database.")

        cursor = conn.cursor(dictionary=True) # Use dictionary cursor for JSON output
        cursor.execute(query, params or ())

        if commit:
            conn.commit()
            result = cursor.lastrowid or True # Return insert ID or True for update/delete
        elif fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()

    # Don't catch mysql.connector.Error here, let the error handler do it
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
    return result


# --- API Endpoints ---

@app.route('/health', methods=['GET'])
def health_check():
    # Basic check if the API is running
    return jsonify({"status": "healthy"}), 200

@app.route('/employees', methods=['POST'])
@require_api_key
def add_employee():
    """Adds a new employee."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Missing 'name' in request body"}), 400

    name = data['name']
    department = data.get('department') # Department is optional

    sql = "INSERT INTO employees (name, department) VALUES (%s, %s)"
    try:
        employee_id = execute_query(sql, (name, department), commit=True)
        if employee_id:
             # Fetch the newly created employee to return it
            new_employee = execute_query("SELECT * FROM employees WHERE id = %s", (employee_id,), fetchone=True)
            return jsonify(new_employee), 201 # 201 Created
        else:
             # This case might indicate an issue if lastrowid isn't returned as expected
             return jsonify({"message": "Employee created, but could not retrieve ID."}), 201

    except Exception as e: # Catch potential issues during insert/fetch
        print(f"Error adding employee: {e}")
        return jsonify({"error": "Failed to add employee", "details": str(e)}), 500


@app.route('/employees', methods=['GET'])
@require_api_key
def get_employees():
    """Retrieves all employees."""
    employees = execute_query("SELECT * FROM employees", fetchall=True)
    return jsonify(employees or []) # Return empty list if no employees

@app.route('/employees/<int:employee_id>', methods=['GET'])
@require_api_key
def get_employee(employee_id):
    """Retrieves a specific employee by ID."""
    employee = execute_query("SELECT * FROM employees WHERE id = %s", (employee_id,), fetchone=True)
    if employee:
        return jsonify(employee)
    else:
        # Use Flask's abort to trigger the 404 error handler
        from flask import abort
        abort(404)

@app.route('/employees/<int:employee_id>', methods=['PUT'])
@require_api_key
def update_employee(employee_id):
    """Updates an existing employee."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    # Check if employee exists first
    existing_employee = execute_query("SELECT id FROM employees WHERE id = %s", (employee_id,), fetchone=True)
    if not existing_employee:
        from flask import abort
        abort(404)

    # Build the update query dynamically based on provided fields
    fields = []
    params = []
    if 'name' in data:
        fields.append("name = %s")
        params.append(data['name'])
    if 'department' in data:
        fields.append("department = %s")
        params.append(data['department'])

    if not fields:
        return jsonify({"error": "No fields provided for update"}), 400

    params.append(employee_id) # Add the ID for the WHERE clause
    sql = f"UPDATE employees SET {', '.join(fields)} WHERE id = %s"

    updated = execute_query(sql, tuple(params), commit=True)

    if updated:
        # Fetch the updated employee data
        updated_employee = execute_query("SELECT * FROM employees WHERE id = %s", (employee_id,), fetchone=True)
        return jsonify(updated_employee)
    else:
        # This path might indicate an issue if the update affected 0 rows unexpectedly
        # Or if execute_query didn't return True for commit=True without error
        return jsonify({"error": "Update operation reported no changes or failed silently"}), 500


@app.route('/employees/<int:employee_id>', methods=['DELETE'])
@require_api_key
def delete_employee(employee_id):
    """Deletes an employee."""
     # Check if employee exists first
    existing_employee = execute_query("SELECT id FROM employees WHERE id = %s", (employee_id,), fetchone=True)
    if not existing_employee:
        from flask import abort
        abort(404)

    sql = "DELETE FROM employees WHERE id = %s"
    deleted = execute_query(sql, (employee_id,), commit=True)

    if deleted:
        return jsonify({"message": f"Employee with ID {employee_id} deleted successfully."}), 200 # Or 204 No Content
    else:
         # This path might indicate an issue
         return jsonify({"error": "Delete operation reported no changes or failed silently"}), 500

# --- Main Execution ---
if __name__ == '__main__':
    print("Starting API service...")
    # Run initial database setup (create table, populate if empty)
    # This should ideally run *after* the DB service is confirmed ready.
    # Docker Compose `depends_on` helps, but readiness checks are better.
    # The get_db_connection function now includes retries.
    setup_database()

    # Start the Flask development server
    # Host 0.0.0.0 makes it accessible outside the container
    app.run(host='0.0.0.0', port=5000, debug=True) # Turn debug=False for production
