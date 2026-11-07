# REST API Using Python and MySQL

A FastAPI-based employee management system that stores employee records in MySQL and supports file, CSV, and JSON operations inside a safe project reports folder.

## Project Overview

This project demonstrates how to build a backend API using:

- Python
- FastAPI
- MySQL
- mysql-connector-python
- python-dotenv

It provides REST endpoints to:

- Create, read, update, and delete employee records
- Search employees by name or department
- Validate requests using Pydantic models
- Work with text, CSV, and JSON files in a controlled directory
- Import CSV data into the MySQL database
- Export employee data to CSV and JSON files

## Features

### Employee Management

- Add a new employee
- Retrieve all employees
- Get a single employee by ID
- Update employee details
- Delete an employee
- Search employees by partial keyword match

### Database Connectivity

- Connects to MySQL using environment-based configuration
- Uses a reusable `get_connection()` helper
- Validates DB health via `/test-db`

### File Operations

The API restricts file access to the `employee_api/reports` folder to prevent directory traversal attacks.

Supported operations include:

- Create a text file
- Write content to a file
- Append content to a file
- Read file contents
- Read file line by line
- Check whether a file exists
- Rename a file
- Copy a file
- Delete a file
- Get file size

### CSV and JSON Support

- Read CSV files from the safe reports directory
- Import CSV records into the `employees` table
- Export employees to CSV
- Read JSON files
- Write JSON data to a file
- Export employees to JSON

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- MySQL Server
- mysql-connector-python
- python-dotenv
- Pydantic for validation

## Project Structure

```text
REST-API-USING-PYTHON-AND-MySQL/
├── README.md
├── employee_api/
│   ├── main.py
│   ├── database.py
│   ├── employee_queries.py
│   ├── file_operations.py
│   ├── requirements.txt
│   └── reports/
│       ├── sample_employees.csv
│       ├── sample_data.json
│       └── ...
└── .gitignore
```

## Prerequisites

Before running the project, make sure you have:

- Python installed
- MySQL Server installed and running
- A database created in MySQL
- Access to the database credentials

## Setup Instructions

1. Clone the repository

```bash
git clone https://github.com/bhagirathidharigoud/REST-API-USING-PYTHON-AND-MySQL.git
cd REST-API-USING-PYTHON-AND-MySQL
```

2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies

```bash
cd employee_api
pip install -r requirements.txt
```

4. Configure the database connection

Create a `.env` file inside the `employee_api` directory with the following content:

```env
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=employee_db
```

> If your local MySQL uses a different port or credentials, update these values accordingly.

5. Create the database and the `employees` table

Example MySQL setup:

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

## Run the Application

From the `employee_api` directory:

```bash
uvicorn main:app --reload
```

The application will start at:

```text
http://127.0.0.1:8000
```

You can open the interactive API documentation here:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Endpoints

### Health Checks

- `GET /` — API status
- `GET /test-db` — verify MySQL connectivity

### Employee Endpoints

- `POST /employees` — create an employee
- `GET /employees` — fetch all employees
- `GET /employees/{employee_id}` — fetch an employee by ID
- `PUT /employees/{employee_id}` — update an employee
- `DELETE /employees/{employee_id}` — delete an employee
- `GET /employees/search/results?keyword=...` — search employees by name or department

### Text File Endpoints

- `POST /files/text/create`
- `POST /files/text/write`
- `POST /files/text/append`
- `GET /files/text/read`
- `GET /files/text/read-lines`
- `GET /files/text/exists`
- `POST /files/text/rename`
- `POST /files/text/copy`
- `DELETE /files/text/delete`
- `GET /files/text/size`

### CSV Endpoints

- `GET /files/csv/read`
- `POST /files/csv/import`
- `POST /files/csv/export`

### JSON Endpoints

- `GET /files/json/read`
- `POST /files/json/write`
- `POST /files/json/export`

## Example Requests

### Add an employee

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

### Get all employees

```bash
curl "http://127.0.0.1:8000/employees"
```

### Search employees

```bash
curl "http://127.0.0.1:8000/employees/search/results?keyword=engineering"
```

### Read a text file

```bash
curl "http://127.0.0.1:8000/files/text/read?filename=notes.txt"
```

### Export employees to CSV

```bash
curl -X POST "http://127.0.0.1:8000/files/csv/export" \
  -H "Content-Type: application/json" \
  -d '{
    "output_filename": "employees_export.csv"
  }'
```

## Notes

- All file-based operations are restricted to the project `reports` directory for security.
- The project is beginner-friendly and designed to help understand FastAPI + MySQL integration.
- This API is a practical example for learning API design, database operations, and safe file handling in Python.

## License

This project is available for learning and educational use.
