 
# Employee CRUD API with Flask, MySQL, and Docker

This project provides a simple RESTful API service for managing employee records (Create, Read, Update, Delete). The API is built with Python (Flask) and interacts with a MySQL database. Both the API service and the database run as separate Docker containers, orchestrated using Docker Compose.

## Features

* **CRUD Operations:** Endpoints for creating, retrieving (all and specific), updating, and deleting employee records.
* **Database Initialization:** Automatically creates the `employees` table (`id`, `name`, `department`) if it doesn't exist.
* **Automatic Data Population:** Populates the database with 500 random employee entries on the *first run* if the table is empty.
* **Persistent Database Storage:** Uses a Docker named volume (`mysql_data`) to persist MySQL data across container restarts.
* **API Key Authorization:** Basic protection requiring an API key passed via the `X-API-KEY` header for most endpoints.
* **Error Handling:** Basic error handling for common HTTP statuses (400, 401, 404, 500) and database errors.
* **Optional Read-Only User:** Includes an example SQL script (`mysql_init/`) to create a read-only database user on initial setup.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* [Docker Engine](https://docs.docker.com/engine/install/)
* [Docker Compose](https://docs.docker.com/compose/install/) (Included with Docker Desktop)

## Setup and Running

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/EdvinasStankunas/employee-crud-api.git
    cd employee-crud-api
    ```

2.  **Configure Environment Variables:**
        * Open the `.env` file and edit the following variables:
        * `MYSQL_ROOT_PASSWORD`: Set a strong password for the MySQL root user.
        * `MYSQL_PASSWORD`: Set a strong password for the application's MySQL user (`app_user`).
        * `API_KEY`: **Generate a secure, random API key.**

3.  **Build and Start Containers:**
    * Run the following command from the project root directory:
        ```bash
        docker compose up --build -d
        ```
        * `--build`: Ensures the API image is built based on the `Dockerfile`.
        * `-d`: Runs the containers in detached mode (in the background).

4.  **Check Logs (Optional):**
    * View logs for the API service:
        ```bash
        docker compose logs -f api
        ```
    * View logs for the Database service:
        ```bash
        docker compose logs -f db
        ```
    * Press `Ctrl+C` to stop viewing logs. On the first run, you should see messages about the database initializing and potentially the data population script running.

The API service should now be running and accessible at `http://localhost:5000`.

## API Endpoints

**Base URL:** `http://localhost:5000`

**Authentication:**
Most endpoints require an API key for authorization. You must include the following header in your requests:
`X-API-KEY: your_super_secret_api_key`
(Replace `your_super_secret_api_key` with the key you set in the `.env` file).

---

### 1. Health Check

* **Endpoint:** `GET /health`
* **Description:** Checks if the API service is running. No authentication required.
* **Success Response (200 OK):**
    ```json
    {
      "status": "healthy"
    }
    ```
* **Example:**
    ```bash
    curl http://localhost:5000/health
    ```

---

### 2. Create Employee

* **Endpoint:** `POST /employees`
* **Description:** Adds a new employee record.
* **Headers:** `X-API-KEY: your_super_secret_api_key`, `Content-Type: application/json`
* **Request Body (JSON):**
    ```json
    {
      "name": "John Doe",
      "department": "Engineering"
    }
    ```
* **Success Response (201 Created):** Returns the newly created employee object.
    ```json
    {
      "id": 501,
      "name": "John Doe",
      "department": "Engineering"
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Missing `name` or invalid JSON.
    * `401 Unauthorized`: Missing or invalid API Key.
    * `500 Internal Server Error`: Database error during insertion.
* **Example:**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -H "X-API-KEY: your_super_secret_api_key" \
    -d '{"name": "Jane Smith", "department": "Marketing"}' \
    http://localhost:5000/employees
    ```

---

### 3. Get All Employees

* **Endpoint:** `GET /employees`
* **Description:** Retrieves a list of all employee records.
* **Headers:** `X-API-KEY: your_super_secret_api_key`
* **Success Response (200 OK):** Returns a JSON array of employee objects.
    ```json
    [
      {
        "id": 1,
        "name": "...",
        "department": "..."
      },
      {
        "id": 2,
        "name": "...",
        "department": "..."
      }
    ]
    ```
* **Error Responses:**
    * `401 Unauthorized`: Missing or invalid API Key.
    * `500 Internal Server Error`: Database error during retrieval.
* **Example:**
    ```bash
    curl -H "X-API-KEY: your_super_secret_api_key" http://localhost:5000/employees
    ```

---

### 4. Get Specific Employee

* **Endpoint:** `GET /employees/{id}`
* **Description:** Retrieves a single employee record by its ID.
* **Headers:** `X-API-KEY: your_super_secret_api_key`
* **Path Parameter:** `id` (integer) - The ID of the employee to retrieve.
* **Success Response (200 OK):** Returns the employee object.
    ```json
    {
      "id": 1,
      "name": "...",
      "department": "..."
    }
    ```
* **Error Responses:**
    * `401 Unauthorized`: Missing or invalid API Key.
    * `404 Not Found`: Employee with the specified ID does not exist.
    * `500 Internal Server Error`: Database error during retrieval.
* **Example:**
    ```bash
    curl -H "X-API-KEY: your_super_secret_api_key" http://localhost:5000/employees/10
    ```

---

### 5. Update Employee

* **Endpoint:** `PUT /employees/{id}`
* **Description:** Updates an existing employee's details. You can update `name`, `department`, or both.
* **Headers:** `X-API-KEY: your_super_secret_api_key`, `Content-Type: application/json`
* **Path Parameter:** `id` (integer) - The ID of the employee to update.
* **Request Body (JSON):** Include the fields you want to update.
    ```json
    {
      "name": "Jane Updated Doe", // Optional
      "department": "Senior Engineering" // Optional
    }
    ```
* **Success Response (200 OK):** Returns the full updated employee object.
    ```json
    {
      "id": 10,
      "name": "Jane Updated Doe",
      "department": "Senior Engineering"
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Invalid JSON or no fields provided for update.
    * `401 Unauthorized`: Missing or invalid API Key.
    * `404 Not Found`: Employee with the specified ID does not exist.
    * `500 Internal Server Error`: Database error during update.
* **Example:**
    ```bash
    curl -X PUT -H "Content-Type: application/json" \
    -H "X-API-KEY: your_super_secret_api_key" \
    -d '{"department": "Product Management"}' \
    http://localhost:5000/employees/10
    ```

---

### 6. Delete Employee

* **Endpoint:** `DELETE /employees/{id}`
* **Description:** Deletes an employee record by its ID.
* **Headers:** `X-API-KEY: your_super_secret_api_key`
* **Path Parameter:** `id` (integer) - The ID of the employee to delete.
* **Success Response (200 OK):**
    ```json
    {
      "message": "Employee with ID 10 deleted successfully."
    }
    ```
* **Error Responses:**
    * `401 Unauthorized`: Missing or invalid API Key.
    * `404 Not Found`: Employee with the specified ID does not exist.
    * `500 Internal Server Error`: Database error during deletion.
* **Example:**
    ```bash
    curl -X DELETE -H "X-API-KEY: your_super_secret_api_key" http://localhost:5000/employees/10
    ```

---

## Database Details

* **Read-Only User (Optional):**
    * The `mysql_init/create_readonly_user.sql` script is provided as an example.
    * If this script is present in `mysql_init/` when the database container starts for the *first time with an empty data volume*, it will automatically create a user named `readonly_user` with password `readonly_password`.
    * This user only has `SELECT` privileges on the `company_db` database.
    * **Remember to change the password** in the script if you plan to use this user.


## Removing Data

* To stop the containers AND remove the persistent database data volume:
    ```bash
    docker compose down -v
    ```
    **Warning:** This action is irreversible and will delete all employee data stored in the database.

