# ─────────────────────────────────────────────────────────────
# main.py  –  Entry point of the application
#
# Responsibility:
#   • Creates the FastAPI app object.
#   • Registers all HTTP endpoints (routes).
#   • Validates incoming request data using Pydantic models.
#   • Calls employee_queries.py for database logic.
#   • Calls file_operations.py for file logic.
#   • Returns JSON responses with correct HTTP status codes.
#
# How to run:
#   uvicorn main:app --reload
# ─────────────────────────────────────────────────────────────

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from database import get_connection
import employee_queries as eq
import file_operations as fo

# ── App setup ────────────────────────────────────────────────
app = FastAPI(
    title="Employee Management API",
    description="A beginner-friendly REST API for managing employees and files",
    version="1.0.0"
)


# ═══════════════════════════════════════════════════════════════
#  PYDANTIC INPUT MODELS
#  These define the shape of JSON bodies we accept from clients.
# ═══════════════════════════════════════════════════════════════

class EmployeeInput(BaseModel):
    name:       str   = Field(..., min_length=1, max_length=100)
    email:      str   = Field(..., min_length=5, max_length=150)
    department: str   = Field(..., min_length=1, max_length=100)
    salary:     float = Field(..., gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "department": "Engineering",
                "salary": 75000.00
            }
        }
    }


class FileCreateInput(BaseModel):
    """Body for creating a new empty file."""
    filename: str = Field(..., min_length=1, max_length=100,
                          description="Name of the file to create (e.g. 'notes.txt')")

    model_config = {"json_schema_extra": {"example": {"filename": "notes.txt"}}}


class FileWriteInput(BaseModel):
    """Body for writing or appending content to a file."""
    filename: str = Field(..., min_length=1, max_length=100,
                          description="Target filename")
    content:  str = Field(..., min_length=0,
                          description="Text content to write or append")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "notes.txt",
                "content": "Hello, this is the first line.\nThis is the second line."
            }
        }
    }


class FileRenameInput(BaseModel):
    """Body for renaming a file."""
    old_filename: str = Field(..., min_length=1, max_length=100)
    new_filename: str = Field(..., min_length=1, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {"old_filename": "notes.txt", "new_filename": "my_notes.txt"}
        }
    }


class FileCopyInput(BaseModel):
    """Body for copying a file."""
    source_filename:      str = Field(..., min_length=1, max_length=100)
    destination_filename: str = Field(..., min_length=1, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "source_filename": "notes.txt",
                "destination_filename": "notes_backup.txt"
            }
        }
    }


# ═══════════════════════════════════════════════════════════════
#  HEALTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Employee Management API is running!"}


@app.get("/test-db", tags=["Health"])
def test_database_connection():
    """Verifies the MySQL connection is working."""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return {"status": "success", "message": "Connected to MySQL!", "result": result[0]}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {str(error)}")


# ═══════════════════════════════════════════════════════════════
#  EMPLOYEE ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.post("/employees", status_code=201, tags=["Employees"])
def add_employee(employee: EmployeeInput):
    """Add a new employee. Returns 201 with the created record."""
    try:
        return eq.add_employee(
            name=employee.name,
            email=employee.email,
            department=employee.department,
            salary=employee.salary
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


@app.get("/employees", tags=["Employees"])
def get_all_employees():
    """Retrieve all employees."""
    try:
        employees = eq.get_all_employees()
        return {"total": len(employees), "employees": employees}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


@app.get("/employees/search/results", tags=["Employees"])
def search_employees(
    keyword: str = Query(..., min_length=1, description="Name or department to search for")
):
    """Search employees by name or department (partial, case-insensitive)."""
    try:
        results = eq.search_employees(keyword)
        return {"keyword": keyword, "total": len(results), "employees": results}
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


@app.get("/employees/{employee_id}", tags=["Employees"])
def get_employee_by_id(employee_id: int):
    """Retrieve a single employee by ID."""
    try:
        return eq.get_employee_by_id(employee_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


@app.put("/employees/{employee_id}", tags=["Employees"])
def update_employee(employee_id: int, employee: EmployeeInput):
    """Update all fields of an existing employee."""
    try:
        return eq.update_employee(
            employee_id=employee_id,
            name=employee.name,
            email=employee.email,
            department=employee.department,
            salary=employee.salary
        )
    except ValueError as error:
        msg = str(error)
        status = 404 if "No employee found" in msg else 409
        raise HTTPException(status_code=status, detail=msg)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


@app.delete("/employees/{employee_id}", tags=["Employees"])
def delete_employee(employee_id: int):
    """Permanently delete an employee by ID."""
    try:
        return eq.delete_employee(employee_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ═══════════════════════════════════════════════════════════════
#  TEXT FILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════

# ── 1. Create a file ─────────────────────────────────────────
@app.post("/files/text/create", status_code=201, tags=["Text Files"])
def create_text_file(body: FileCreateInput):
    """
    Create a new empty text file in the reports/ folder.

    - Fails with **409** if a file with that name already exists.
    - Fails with **403** if the filename tries to escape the safe directory.
    """
    try:
        return fo.create_text_file(body.filename)

    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except PermissionError as error:
        # 403 Forbidden — the path tried to escape the safe directory.
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 2. Write content (overwrite) ──────────────────────────────
@app.post("/files/text/write", tags=["Text Files"])
def write_text_file(body: FileWriteInput):
    """
    Write content to a file, replacing any existing content.
    Creates the file if it does not already exist.
    """
    try:
        return fo.write_text_file(body.filename, body.content)

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 3. Append content ─────────────────────────────────────────
@app.post("/files/text/append", tags=["Text Files"])
def append_text_file(body: FileWriteInput):
    """
    Append content to the end of an existing file without erasing it.
    Returns **404** if the file does not exist.
    """
    try:
        return fo.append_text_file(body.filename, body.content)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 4. Read entire file ───────────────────────────────────────
@app.get("/files/text/read", tags=["Text Files"])
def read_text_file(
    filename: str = Query(..., min_length=1, description="Name of the file to read")
):
    """
    Read and return the entire content of a text file.
    Returns **404** if the file does not exist.
    """
    try:
        return fo.read_text_file(filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 5. Read file line by line ─────────────────────────────────
@app.get("/files/text/read-lines", tags=["Text Files"])
def read_text_file_lines(
    filename: str = Query(..., min_length=1, description="Name of the file to read line by line")
):
    """
    Read a file and return each line as a separate item in a list.
    Blank lines are included. Trailing newline characters are stripped.
    """
    try:
        return fo.read_text_file_lines(filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 6. Check if file exists ───────────────────────────────────
@app.get("/files/text/exists", tags=["Text Files"])
def check_file_exists(
    filename: str = Query(..., min_length=1, description="Filename to check")
):
    """
    Check whether a file exists in the reports/ folder.
    Always returns **200** — the 'exists' field in the body tells you the answer.
    """
    try:
        return fo.check_file_exists(filename)

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 7. Rename a file ──────────────────────────────────────────
@app.post("/files/text/rename", tags=["Text Files"])
def rename_text_file(body: FileRenameInput):
    """
    Rename a file inside the reports/ folder.
    Returns **404** if the source does not exist.
    Returns **409** if the new name is already taken.
    """
    try:
        return fo.rename_text_file(body.old_filename, body.new_filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 7b. Copy a file ───────────────────────────────────────────
@app.post("/files/text/copy", tags=["Text Files"])
def copy_text_file(body: FileCopyInput):
    """
    Copy a file to a new name inside the reports/ folder.
    Returns **404** if the source does not exist.
    Returns **409** if the destination name is already taken.
    """
    try:
        return fo.copy_text_file(body.source_filename, body.destination_filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 8. Delete a file ─────────────────────────────────────────
@app.delete("/files/text/delete", tags=["Text Files"])
def delete_text_file(
    filename: str = Query(..., min_length=1, description="Name of the file to delete")
):
    """
    Delete a file from the reports/ folder.
    Returns **404** if the file does not exist.
    Returns **403** if the filename tries to escape the safe directory.
    """
    try:
        return fo.delete_text_file(filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 9. Get file size ──────────────────────────────────────────
@app.get("/files/text/size", tags=["Text Files"])
def get_file_size(
    filename: str = Query(..., min_length=1, description="Filename to inspect")
):
    """
    Return the size of a file in bytes, KB, and MB.
    Returns **404** if the file does not exist.
    """
    try:
        return fo.get_file_size(filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ═══════════════════════════════════════════════════════════════
#  CSV FILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════

class CsvExportInput(BaseModel):
    """Body for the CSV export endpoint."""
    output_filename: str = Field(
        ..., min_length=1, max_length=100,
        description="Name of the CSV file to create, e.g. 'employees_export.csv'"
    )
    model_config = {
        "json_schema_extra": {"example": {"output_filename": "employees_export.csv"}}
    }


# ── 1. Read a CSV file ────────────────────────────────────────
@app.get("/files/csv/read", tags=["CSV Files"])
def read_csv_file(
    filename: str = Query(..., min_length=1, description="CSV filename inside reports/")
):
    """
    Read a CSV file from the reports/ folder and return its rows as JSON.

    - **filename**: e.g. `sample_employees.csv`
    - Returns headers list, all data rows, and total count.
    - Returns **404** if the file does not exist.
    - Returns **400** if required columns are missing.
    """
    try:
        return fo.read_csv_file(filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        # 400 Bad Request — the CSV structure is wrong.
        raise HTTPException(status_code=400, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 2. Import CSV into MySQL ──────────────────────────────────
@app.post("/files/csv/import", tags=["CSV Files"])
def import_csv_to_mysql(
    filename: str = Query(..., min_length=1, description="CSV filename to import from reports/")
):
    """
    Read a CSV file from reports/, validate each row, and insert valid
    rows into the MySQL employees table.

    - Invalid rows (bad email, missing name, non-numeric salary) are skipped
      and reported in the response — the import continues with valid rows.
    - Duplicate emails are also skipped and reported.
    - Returns a summary of inserted vs skipped rows.
    """
    try:
        return fo.import_csv_to_mysql(filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 3. Export employees to CSV ────────────────────────────────
@app.post("/files/csv/export", tags=["CSV Files"])
def export_employees_to_csv(body: CsvExportInput):
    """
    Export all employees from MySQL to a CSV file in reports/.

    - **output_filename**: name of the CSV to create (e.g. `employees_export.csv`).
    - Returns the filename and total rows exported.
    - The exported file can then be downloaded with the file upload/download
      endpoints added in Stage 7.
    """
    try:
        return fo.export_employees_to_csv(body.output_filename)

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ═══════════════════════════════════════════════════════════════
#  JSON FILE ENDPOINTS
# ═══════════════════════════════════════════════════════════════

class JsonWriteInput(BaseModel):
    """Body for writing arbitrary JSON data to a file."""
    filename: str  = Field(..., min_length=1, max_length=100,
                           description="Target filename, e.g. 'config.json'")
    # The content field accepts any valid JSON value — a dict, a list,
    # a string, etc. Python's type hint for this is `dict`, but we use
    # `dict` as a reasonable default since most JSON files are objects.
    # FastAPI/Pydantic will accept any JSON-serialisable value here.
    content: dict  = Field(..., description="JSON object to write to the file")

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "config.json",
                "content": {
                    "theme": "dark",
                    "language": "en",
                    "notifications": True
                }
            }
        }
    }


class JsonExportInput(BaseModel):
    """Body for the JSON export endpoint."""
    output_filename: str = Field(
        ..., min_length=1, max_length=100,
        description="Name of the JSON file to create, e.g. 'employees_export.json'"
    )
    model_config = {
        "json_schema_extra": {"example": {"output_filename": "employees_export.json"}}
    }


# ── 1. Read a JSON file ───────────────────────────────────────
@app.get("/files/json/read", tags=["JSON Files"])
def read_json_file(
    filename: str = Query(..., min_length=1, description="JSON filename inside reports/")
):
    """
    Read and parse a JSON file from the reports/ folder.

    - Returns the parsed JSON as a nested object in the response body.
    - Returns **404** if the file does not exist.
    - Returns **400** if the file contains invalid/malformed JSON.
    - Returns **403** if the filename tries to escape the safe directory.
    """
    try:
        return fo.read_json_file(filename)

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        # 400 Bad Request — the file exists but the JSON inside is broken.
        raise HTTPException(status_code=400, detail=str(error))

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 2. Write JSON data to a file ──────────────────────────────
@app.post("/files/json/write", tags=["JSON Files"])
def write_json_file(body: JsonWriteInput):
    """
    Write a JSON object to a file in the reports/ folder.
    Overwrites the file if it already exists; creates it if not.

    - **filename**: Target filename (e.g. `config.json`)
    - **content**: Any valid JSON object to write
    """
    try:
        return fo.write_json_file(body.filename, body.content)

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except TypeError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")


# ── 3. Export employees to JSON ───────────────────────────────
@app.post("/files/json/export", tags=["JSON Files"])
def export_employees_to_json(body: JsonExportInput):
    """
    Export all employees from MySQL to a JSON file in reports/.

    The JSON file includes:
    - `exported_at`: ISO timestamp of when the export was run
    - `total_employees`: count of records
    - `employees`: array of employee objects

    The exported file can be downloaded using the upload/download
    endpoints added in Stage 7.
    """
    try:
        return fo.export_employees_to_json(body.output_filename)

    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(error)}")
