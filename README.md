# REST API Using Python and MySQL

A beginner-friendly FastAPI application for managing employee records in MySQL, while also supporting safe file, CSV, and JSON operations inside a restricted `reports/` folder.

This project is designed to demonstrate how to:

- build a REST API with Python and FastAPI
- connect to a MySQL database using environment-based configuration
- perform CRUD operations on a relational database
- validate inbound request payloads with Pydantic models
- restrict file access to a safe project directory
- import and export data in CSV and JSON formats

## Project overview

This repository contains a simple backend API that stores employee information in a MySQL table called `employees` and exposes endpoints for creating, retrieving, updating, deleting, and searching employees.

It also includes file-management features to create, modify, read, rename, copy, delete, and inspect text files, as well as CSV and JSON operations for working with structured data.

The project is intentionally straightforward and educational, making it suitable for learning how REST APIs, database integration, validation, and secure file handling work together in a real application.

## Why this project exists

This project is useful for learning and practicing:

- FastAPI route creation and request validation
- MySQL connection handling and parameterized SQL queries
- CRUD logic in Python
- secure file access patterns
- CSV validation and bulk import
- JSON export and parsing
- environment configuration with `.env`

## Tech stack

- Python 3.10+
- FastAPI
- Uvicorn
- MySQL Server
- mysql-connector-python
- python-dotenv
- Pydantic
- CSV/JSON standard library utilities

## Features

### Employee management

- Create a new employee
- Retrieve all employees
- Retrieve a single employee by ID
- Update employee information
- Delete an employee record
- Search employees by partial name or department match
- Prevent duplicate emails using MySQL uniqueness constraints

### Database connectivity

- Connects to MySQL through environment variables
- Uses a reusable `get_connection()` helper in `database.py`
- Verifies database connectivity with `/test-db`
- Uses parameterized SQL queries to prevent SQL injection

### File operations

All file requests are restricted to the project’s `employee_api/reports/` directory. The API prevents unsafe paths such as `../` or absolute paths from escaping the allowed folder.

Supported operations include:

- create a text file
- write to a file (overwrite)
- append text to a file
- read an entire file
- read line by line
- check if a file exists
- rename a file
- copy a file
- delete a file
- get file size in bytes/KB/MB

### CSV operations

- read a CSV file from the safe directory
- validate required columns and row values
- import valid rows into MySQL
- export all employee data to a CSV file
- skip malformed or duplicate entries and report them in the response

### JSON operations

- read JSON content from a file
- write JSON data to a file
- export employee data to JSON
- validate JSON structure and malformed inputs

## Project structure

```text
REST-API-USING-PYTHON-AND-MySQL/
├── README.md
├── .gitignore
├── employee_api/
│   ├── main.py
│   ├── database.py
│   ├── employee_queries.py
│   ├── file_operations.py
│   ├── requirements.txt
│   └── reports/
│       ├── sample_employees.csv
│       ├── sample_data.json
│       ├── notes.txt
│       ├── nighan2.txt
│       └── ssms.txt
└── ...
```

### Module responsibilities

- `main.py`  
  FastAPI app definition, request models, and route handlers.

- `database.py`  
  Reads MySQL settings from environment variables and opens database connections.

- `employee_queries.py`  
  Contains the pure SQL logic for employee CRUD and search operations.

- `file_operations.py`  
  Handles safe file access, CSV parsing/importing, and JSON read/write/export functions.

- `requirements.txt`  
  Lists all Python dependencies required to run the project.

- `reports/`  
  Safe storage directory for sample data and generated files.

## Prerequisites

Before running the project, make sure you have:

- Python 3.10 or newer installed
- MySQL Server installed and running
- A MySQL database created for the project
- Database credentials available (host, port, user, password, database name)
- Access to a terminal or command prompt

## Setup instructions

### 1. Clone the repository

```bash
git clone https://github.com/bhagirathidharigoud/REST-API-USING-PYTHON-AND-MySQL.git
cd REST-API-USING-PYTHON-AND-MySQL
```

### 2. Create and activate a virtual environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
cd employee_api
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file inside `employee_api/` with the following content:

```env
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=employee_db
```

> If your local MySQL server uses a different port or different credentials, update the values accordingly.

### 5. Create the MySQL database and table

Open MySQL and run:

```sql
CREATE DATABASE employee_db;
USE employee_db;

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) NOT NULL
);
```

You can also insert a sample row for testing:

```sql
INSERT INTO employees (name, email, department, salary)
VALUES ('Alice Johnson', 'alice@example.com', 'Engineering', 75000.00);
```

## Run the application

From the `employee_api/` directory, start the API server:

```bash
uvicorn main:app --reload
```

The app will run at:

```text
http://127.0.0.1:8000
```

You can access the interactive documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API overview

### Health endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API status message |
| GET | `/test-db` | Verifies MySQL connectivity |

### Employee endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/employees` | Create a new employee |
| GET | `/employees` | Retrieve all employees |
| GET | `/employees/{employee_id}` | Get one employee by ID |
| PUT | `/employees/{employee_id}` | Update an employee |
| DELETE | `/employees/{employee_id}` | Delete an employee |
| GET | `/employees/search/results?keyword=...` | Search employees by name or department |

### Text file endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/files/text/create` | Create an empty file |
| POST | `/files/text/write` | Overwrite file content |
| POST | `/files/text/append` | Append content to a file |
| GET | `/files/text/read` | Read file contents |
| GET | `/files/text/read-lines` | Read file line by line |
| GET | `/files/text/exists` | Check if a file exists |
| POST | `/files/text/rename` | Rename a file |
| POST | `/files/text/copy` | Copy a file |
| DELETE | `/files/text/delete` | Delete a file |
| GET | `/files/text/size` | Get file size |

### CSV endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/files/csv/read` | Read CSV file contents |
| POST | `/files/csv/import` | Import CSV rows into MySQL |
| POST | `/files/csv/export` | Export employee records to CSV |

### JSON endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/files/json/read` | Read a JSON file |
| POST | `/files/json/write` | Write JSON data to file |
| POST | `/files/json/export` | Export employees to JSON |

## Request and response examples

### Create an employee

```bash
curl -X POST "http://127.0.0.1:8000/employees" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "department": "Engineering",
    "salary": 75000.00
  }'
```

Example response:

```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@example.com",
  "department": "Engineering",
  "salary": 75000.0
}
```

### Get all employees

```bash
curl "http://127.0.0.1:8000/employees"
```

### Search employees

```bash
curl "http://127.0.0.1:8000/employees/search/results?keyword=engineering"
```

### Update an employee

```bash
curl -X PUT "http://127.0.0.1:8000/employees/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice.johnson@example.com",
    "department": "Platform Engineering",
    "salary": 82000.00
  }'
```

### Delete an employee

```bash
curl -X DELETE "http://127.0.0.1:8000/employees/1"
```

### Create a text file

```bash
curl -X POST "http://127.0.0.1:8000/files/text/create" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "notes.txt"
  }'
```

### Write to a text file

```bash
curl -X POST "http://127.0.0.1:8000/files/text/write" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "notes.txt",
    "content": "Hello from the API!\nThis is a second line."
  }'
```

### Read a text file

```bash
curl "http://127.0.0.1:8000/files/text/read?filename=notes.txt"
```

### Read a CSV file from reports

```bash
curl "http://127.0.0.1:8000/files/csv/read?filename=sample_employees.csv"
```

### Import a CSV file into MySQL

```bash
curl -X POST "http://127.0.0.1:8000/files/csv/import?filename=sample_employees.csv"
```

### Export employees to CSV

```bash
curl -X POST "http://127.0.0.1:8000/files/csv/export" \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "employees_export.csv"
  }'
```

### Export employees to JSON

```bash
curl -X POST "http://127.0.0.1:8000/files/json/export" \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "employees_export.json"
  }'
```

## CSV validation rules

When importing CSV data, each row must contain:

- `name` (required, non-empty)
- `email` (required, must look like a valid email)
- `department` (required, non-empty)
- `salary` (required, positive numeric value)

Rows are rejected if:

- the CSV is missing required headers
- a field is empty
- the email format is invalid
- the salary is not numeric or is zero/negative
- the email already exists in the database

## Security notes

This project includes a small but important security layer for file operations:

- file paths are validated against the `employee_api/reports/` folder
- attempts to access files outside the allowed directory are blocked
- the API prevents traversal such as `../../` and absolute paths

This is a good example of restricting filesystem access in a web application.

## Production considerations

This project is a learning/demo API and is not meant to be a full production system without further hardening. For production, you would typically add:

- JWT or OAuth authentication
- role-based access control
- input sanitization and stronger validation
- logging and monitoring
- environment-specific config management
- database migrations
- tests for endpoints and data integrity
- HTTPS and secure deployment configuration

## Troubleshooting

### MySQL connection errors

Check:

- MySQL is running
- `.env` values are correct
- database exists
- port matches actual MySQL server configuration
- user has access to the database

### `Access denied` errors for files

This usually means the filename contains a path traversal attempt or points outside the `reports/` folder. Use simple names such as `notes.txt` or `employees.csv` instead of paths like `../../secret.txt`.

### Import CSV fails

Confirm the file has the required headers:

```text
name,email,department,salary
```

If headers are wrong or values are invalid, the import will skip those rows and return details in the response.

## License

This project is provided as an educational sample for learning Python, FastAPI, and MySQL integration.

## Summary

This repository demonstrates a complete beginner-level API project that combines:

- FastAPI backend development
- MySQL database operations
- Pydantic validation
- CSV import/export
- JSON file handling
- secure file-path restrictions

It is a practical foundation for building more advanced web services and data-driven applications.


## Notes

- All file-based operations are restricted to the project `reports` directory for security.
- The project is beginner-friendly and designed to help understand FastAPI + MySQL integration.
- This API is a practical example for learning API design, database operations, and safe file handling in Python.

## License

This project is available for learning and educational use.
