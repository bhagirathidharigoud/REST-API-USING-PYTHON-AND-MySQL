# ─────────────────────────────────────────────────────────────
# file_operations.py  –  All file handling functions
#
# Responsibility:
#   • Text file operations  (create, read, write, append, delete …)
#   • CSV file operations   (Stage 5)
#   • JSON file operations  (Stage 6)
#   • Upload / download     (Stage 7)
#
# Security rule:
#   ALL file operations are restricted to the REPORTS_DIR folder.
#   The safe_path() helper function enforces this — it raises an
#   error if a filename tries to escape outside the allowed folder
#   using tricks like "../../../etc/passwd".
# ─────────────────────────────────────────────────────────────

import os       # os.path helpers: exists, getsize, rename, join, abspath
import shutil   # shutil.copy2 copies a file with its metadata

# ── Allowed directory ─────────────────────────────────────────
# All text/CSV/JSON files live here.
# os.path.dirname(__file__) = the folder this Python file lives in.
# os.path.join then builds the full path to employee_api/reports/
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")

# Make sure the reports/ folder exists when this module loads.
# exist_ok=True means "don't raise an error if it already exists".
os.makedirs(REPORTS_DIR, exist_ok=True)


# ── Security helper ───────────────────────────────────────────
def safe_path(filename: str) -> str:
    """
    Builds the full path to a file inside REPORTS_DIR and
    verifies the path does not escape outside that directory.

    Args:
        filename – e.g. "notes.txt" or "report.csv"

    Returns:
        The full absolute path, e.g. "/project/reports/notes.txt"

    Raises:
        PermissionError – if the path tries to escape REPORTS_DIR
                          (e.g. filename = "../../etc/passwd")
    """

    # os.path.join combines the safe directory and the filename.
    # os.path.abspath resolves any ".." or "." segments.
    full_path = os.path.abspath(os.path.join(REPORTS_DIR, filename))

    # After resolving "..", check the path still starts with REPORTS_DIR.
    # os.path.abspath(REPORTS_DIR) normalises the directory path too.
    allowed_base = os.path.abspath(REPORTS_DIR)

    if not full_path.startswith(allowed_base + os.sep) and full_path != allowed_base:
        raise PermissionError(
            f"Access denied: '{filename}' resolves outside the allowed directory."
        )

    return full_path


# ═══════════════════════════════════════════════════════════════
#  TEXT FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════

# ── 1. Create a file ─────────────────────────────────────────
def create_text_file(filename: str) -> dict:
    """
    Creates a new empty text file in REPORTS_DIR.
    Fails if the file already exists (uses mode "x").

    Args:
        filename – e.g. "notes.txt"

    Returns:
        dict with a success message and the file path.

    Raises:
        FileExistsError – if a file with that name already exists.
        PermissionError – if the filename tries to escape REPORTS_DIR.
    """

    # Validate and build the full safe path.
    file_path = safe_path(filename)

    # Mode "x" = exclusive creation.
    # Python raises FileExistsError automatically if the file exists.
    # "with" = context manager: closes the file automatically when done.
    # encoding="utf-8" is best practice — always specify the encoding
    # so your files are readable on all operating systems.
    with open(file_path, "x", encoding="utf-8") as new_file:
        # We just created the file. Nothing to write yet.
        # The "with" block closes it immediately after this.
        pass  # "pass" means "do nothing — just open and close"

    return {
        "message": f"File '{filename}' created successfully.",
        "path": file_path
    }


# ── 2. Write content (overwrite) ──────────────────────────────
def write_text_file(filename: str, content: str) -> dict:
    """
    Writes content to a file, overwriting any existing content.
    Creates the file if it does not exist.

    Args:
        filename – the file to write to.
        content  – the text to write.

    Returns:
        dict with a success message and the number of characters written.
    """

    file_path = safe_path(filename)

    # Mode "w" = write mode.
    # If the file exists, its old content is deleted first.
    # If the file does not exist, it is created.
    with open(file_path, "w", encoding="utf-8") as text_file:
        # write() returns the number of characters written.
        chars_written = text_file.write(content)

    return {
        "message": f"Content written to '{filename}' successfully.",
        "characters_written": chars_written
    }


# ── 3. Append content ─────────────────────────────────────────
def append_text_file(filename: str, content: str) -> dict:
    """
    Appends content to the END of a file without deleting existing content.
    Creates the file if it does not exist.

    Args:
        filename – the file to append to.
        content  – the text to add at the end.

    Returns:
        dict with a success message.

    Raises:
        FileNotFoundError – we require the file to already exist for append.
    """

    file_path = safe_path(filename)

    # Check the file exists before appending.
    # Appending to a non-existent file would silently create it,
    # which might confuse the user. We make it explicit.
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' does not exist. Create it first.")

    # Mode "a" = append mode.
    # The write position starts at the END of the file.
    # Existing content is never touched.
    with open(file_path, "a", encoding="utf-8") as text_file:
        text_file.write(content)

    return {
        "message": f"Content appended to '{filename}' successfully."
    }


# ── 4. Read entire file ───────────────────────────────────────
def read_text_file(filename: str) -> dict:
    """
    Reads and returns the entire content of a text file as one string.

    Args:
        filename – the file to read.

    Returns:
        dict with the full file content and the character count.

    Raises:
        FileNotFoundError – if the file does not exist.
    """

    file_path = safe_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    # Mode "r" = read mode (this is the default, but we write it
    # explicitly so the code is self-documenting).
    with open(file_path, "r", encoding="utf-8") as text_file:
        # read() loads the entire file into a single string.
        # For very large files this uses a lot of memory.
        # For large files, use read_text_file_lines() instead.
        content = text_file.read()

    return {
        "filename": filename,
        "content": content,
        "total_characters": len(content)
    }


# ── 5. Read file line by line ─────────────────────────────────
def read_text_file_lines(filename: str) -> dict:
    """
    Reads a text file and returns each line as a separate list item.
    Leading/trailing whitespace and newline characters are stripped.

    Args:
        filename – the file to read.

    Returns:
        dict with a list of lines and the total line count.

    Raises:
        FileNotFoundError – if the file does not exist.
    """

    file_path = safe_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    lines = []

    with open(file_path, "r", encoding="utf-8") as text_file:
        # Iterating over the file object gives one line at a time.
        # This is memory-efficient — Python reads one line, processes it,
        # then reads the next. The entire file is never loaded at once.
        for line in text_file:
            # strip() removes the trailing "\n" and any surrounding spaces.
            cleaned_line = line.strip()
            lines.append(cleaned_line)

    return {
        "filename": filename,
        "total_lines": len(lines),
        "lines": lines
    }


# ── 6. Check if file exists ───────────────────────────────────
def check_file_exists(filename: str) -> dict:
    """
    Checks whether a file exists in REPORTS_DIR.

    Args:
        filename – the file to check.

    Returns:
        dict with a boolean "exists" and the full path.
    """

    file_path = safe_path(filename)

    # os.path.exists() returns True if the path exists (file or directory).
    # os.path.isfile() additionally checks it is a file, not a folder.
    file_exists = os.path.isfile(file_path)

    return {
        "filename": filename,
        "exists": file_exists,
        "path": file_path if file_exists else None
    }


# ── 7. Rename a file ──────────────────────────────────────────
def rename_text_file(old_filename: str, new_filename: str) -> dict:
    """
    Renames a file inside REPORTS_DIR.

    Args:
        old_filename – current name of the file.
        new_filename – desired new name.

    Returns:
        dict confirming the rename.

    Raises:
        FileNotFoundError – if the source file does not exist.
        FileExistsError   – if a file with the new name already exists.
        PermissionError   – if either name tries to escape REPORTS_DIR.
    """

    old_path = safe_path(old_filename)
    new_path = safe_path(new_filename)  # also validates the new name

    if not os.path.exists(old_path):
        raise FileNotFoundError(f"File '{old_filename}' does not exist.")

    if os.path.exists(new_path):
        raise FileExistsError(
            f"Cannot rename: a file named '{new_filename}' already exists."
        )

    # os.rename() moves/renames the file atomically on most systems.
    os.rename(old_path, new_path)

    return {
        "message": f"File renamed from '{old_filename}' to '{new_filename}'.",
        "new_path": new_path
    }


# ── 7b. Copy a file ───────────────────────────────────────────
def copy_text_file(source_filename: str, destination_filename: str) -> dict:
    """
    Copies a file to a new name inside REPORTS_DIR.

    Args:
        source_filename      – the file to copy.
        destination_filename – the name for the copy.

    Returns:
        dict confirming the copy.

    Raises:
        FileNotFoundError – if the source does not exist.
        FileExistsError   – if the destination already exists.
    """

    source_path = safe_path(source_filename)
    destination_path = safe_path(destination_filename)

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Source file '{source_filename}' does not exist.")

    if os.path.exists(destination_path):
        raise FileExistsError(
            f"Destination file '{destination_filename}' already exists."
        )

    # shutil.copy2 copies the file content AND its metadata
    # (timestamps, permissions). Better than shutil.copy for backups.
    shutil.copy2(source_path, destination_path)

    return {
        "message": f"File '{source_filename}' copied to '{destination_filename}'.",
        "destination_path": destination_path
    }


# ── 8. Delete a file safely ───────────────────────────────────
def delete_text_file(filename: str) -> dict:
    """
    Deletes a file from REPORTS_DIR safely.
    The file must exist; trying to delete a missing file raises an error.

    Args:
        filename – the file to delete.

    Returns:
        dict with a confirmation message.

    Raises:
        FileNotFoundError – if the file does not exist.
        PermissionError   – if the filename tries to escape REPORTS_DIR.
    """

    file_path = safe_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    # os.remove() deletes a single file.
    # It does NOT delete directories — use shutil.rmtree for that.
    os.remove(file_path)

    return {
        "message": f"File '{filename}' deleted successfully."
    }


# ── 9. Get file size ──────────────────────────────────────────
def get_file_size(filename: str) -> dict:
    """
    Returns the size of a file in bytes and in a human-readable format.

    Args:
        filename – the file to inspect.

    Returns:
        dict with size in bytes and a human-readable string (KB, MB).

    Raises:
        FileNotFoundError – if the file does not exist.
    """

    file_path = safe_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    # os.path.getsize() returns the file size in bytes as an integer.
    size_bytes = os.path.getsize(file_path)

    # Convert to KB and MB for readability.
    # We use round() to limit decimal places.
    size_kb = round(size_bytes / 1024, 2)
    size_mb = round(size_bytes / (1024 * 1024), 4)

    return {
        "filename": filename,
        "size_bytes": size_bytes,
        "size_kb": size_kb,
        "size_mb": size_mb
    }


# ═══════════════════════════════════════════════════════════════
#  CSV FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════

import csv      # Python's built-in CSV reader/writer
import re       # regular expressions — used to validate email format

# The expected column names in the CSV header row.
# If the CSV header doesn't contain all four, we reject the file.
REQUIRED_CSV_COLUMNS = {"name", "email", "department", "salary"}


# ── Helper: validate one CSV row ──────────────────────────────
def validate_csv_row(row: dict, row_number: int) -> tuple:
    """
    Validates a single CSV row (already parsed as a dict by csv.DictReader).

    Args:
        row        – dict like {"name": "Alice", "email": "...", ...}
        row_number – the row index (1-based) for error reporting.

    Returns:
        A tuple (is_valid: bool, error_message: str, cleaned_data: dict | None)

        If valid:   (True,  "",      {"name": ..., "salary": float(...)})
        If invalid: (False, "reason", None)
    """

    # ── Check 1: name must not be blank ──────────────────────
    name = row.get("name", "").strip()
    if not name:
        return False, f"Row {row_number}: 'name' is empty.", None

    # ── Check 2: email must contain @ and a dot after @ ──────
    email = row.get("email", "").strip()
    # A minimal regex: something @ something . something
    # We don't use a super-complex regex — just catch obvious errors.
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(email_pattern, email):
        return False, f"Row {row_number}: Invalid email '{email}'.", None

    # ── Check 3: department must not be blank ─────────────────
    department = row.get("department", "").strip()
    if not department:
        return False, f"Row {row_number}: 'department' is empty.", None

    # ── Check 4: salary must be a positive number ─────────────
    salary_raw = row.get("salary", "").strip()
    try:
        # float() converts a string like "75000" to 75000.0
        # It raises ValueError if the string is not a valid number.
        salary = float(salary_raw)
    except ValueError:
        return False, f"Row {row_number}: Salary '{salary_raw}' is not a number.", None

    if salary <= 0:
        return False, f"Row {row_number}: Salary must be greater than 0.", None

    # ── All checks passed — return cleaned data ───────────────
    cleaned = {
        "name": name,
        "email": email,
        "department": department,
        "salary": salary   # now a Python float, not a string
    }
    return True, "", cleaned


# ── 1. Read a CSV file ────────────────────────────────────────
def read_csv_file(filename: str) -> dict:
    """
    Reads a CSV file from REPORTS_DIR and returns its rows as a list of dicts.

    Args:
        filename – the CSV filename, e.g. "sample_employees.csv"

    Returns:
        dict with headers list, rows list, and total row count.

    Raises:
        FileNotFoundError – if the file does not exist.
        ValueError        – if the CSV is missing required columns.
    """

    file_path = safe_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file '{filename}' does not exist.")

    rows = []
    headers = []

    # newline="" is required when reading CSV files in Python.
    # Without it, the csv module may mishandle rows that contain
    # embedded newlines inside quoted fields.
    with open(file_path, "r", encoding="utf-8", newline="") as csv_file:

        # csv.DictReader reads the first row as column headers
        # and returns each subsequent row as a dict
        # {"name": "Alice", "email": "alice@example.com", ...}
        reader = csv.DictReader(csv_file)

        # reader.fieldnames is a list of the header column names.
        # It is populated after the first row is read.
        # We convert to a list so it's JSON-serialisable.
        headers = list(reader.fieldnames) if reader.fieldnames else []

        # Check that the CSV contains the columns we expect.
        missing = REQUIRED_CSV_COLUMNS - set(col.strip() for col in headers)
        if missing:
            raise ValueError(
                f"CSV is missing required columns: {', '.join(sorted(missing))}"
            )

        # Iterate over every data row (skipping the header, which DictReader
        # already consumed). Each `row` is an OrderedDict / dict.
        for row in reader:
            rows.append(dict(row))  # convert OrderedDict to plain dict

    return {
        "filename": filename,
        "headers": headers,
        "total_rows": len(rows),
        "rows": rows
    }


# ── 2. Import CSV into MySQL ──────────────────────────────────
def import_csv_to_mysql(filename: str) -> dict:
    """
    Reads a CSV file from REPORTS_DIR and inserts valid rows into MySQL.
    Invalid rows are collected and reported, not inserted.

    Args:
        filename – the CSV filename to import.

    Returns:
        dict summarising how many rows were inserted vs skipped.

    Raises:
        FileNotFoundError – if the CSV file does not exist.
        ValueError        – if the CSV is missing required columns.
    """

    # We import get_connection here (inside the function) to avoid
    # a circular import — file_operations.py doesn't need the DB
    # unless this specific function is called.
    from database import get_connection

    file_path = safe_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file '{filename}' does not exist.")

    inserted_rows = []    # rows that were successfully inserted
    skipped_rows  = []    # rows that failed validation or had a duplicate email

    with open(file_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        # Validate the header before touching any rows.
        headers = list(reader.fieldnames) if reader.fieldnames else []
        missing = REQUIRED_CSV_COLUMNS - set(col.strip() for col in headers)
        if missing:
            raise ValueError(
                f"CSV is missing required columns: {', '.join(sorted(missing))}"
            )

        # row_number tracks the line in the file for error messages.
        # We start at 2 because row 1 is the header.
        row_number = 2

        for row in reader:
            # ── Validate the row ──────────────────────────────
            is_valid, error_message, cleaned = validate_csv_row(row, row_number)

            if not is_valid:
                # Row failed validation — record it and move on.
                skipped_rows.append({
                    "row_number": row_number,
                    "data": dict(row),
                    "reason": error_message
                })
                row_number += 1
                continue   # skip to the next row

            # ── Try to insert the valid row into MySQL ────────
            try:
                connection = get_connection()
                cursor = connection.cursor()

                insert_sql = """
                    INSERT INTO employees (name, email, department, salary)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (
                    cleaned["name"],
                    cleaned["email"],
                    cleaned["department"],
                    cleaned["salary"]
                ))
                connection.commit()

                # cursor.lastrowid gives the auto-assigned id.
                new_id = cursor.lastrowid
                cursor.close()
                connection.close()

                inserted_rows.append({
                    "row_number": row_number,
                    "id": new_id,
                    "name": cleaned["name"],
                    "email": cleaned["email"]
                })

            except Exception as db_error:
                # Most likely a duplicate email (MySQL error 1062).
                if connection:
                    connection.rollback()
                    cursor.close()
                    connection.close()

                reason = "Duplicate email" if "1062" in str(db_error) else str(db_error)
                skipped_rows.append({
                    "row_number": row_number,
                    "data": dict(row),
                    "reason": reason
                })

            row_number += 1

    return {
        "filename": filename,
        "total_rows_processed": len(inserted_rows) + len(skipped_rows),
        "inserted": len(inserted_rows),
        "skipped": len(skipped_rows),
        "inserted_rows": inserted_rows,
        "skipped_rows": skipped_rows
    }


# ── 3. Export MySQL employees to CSV ─────────────────────────
def export_employees_to_csv(output_filename: str) -> dict:
    """
    Queries all employees from MySQL and writes them to a CSV file
    in REPORTS_DIR.

    Args:
        output_filename – the name for the exported CSV, e.g. "export.csv"

    Returns:
        dict with the output filename and the number of rows exported.
    """

    from database import get_connection

    file_path = safe_path(output_filename)

    # ── Fetch employees from MySQL ────────────────────────────
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, department, salary FROM employees")
        employees = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    # ── Write to CSV ──────────────────────────────────────────
    # newline="" prevents the csv module from writing double newlines
    # on Windows (which would give you a blank row between each data row).
    with open(file_path, "w", encoding="utf-8", newline="") as csv_file:

        # csv.DictWriter takes a list of fieldnames (the column headers).
        # It writes one dict per row, matching keys to column positions.
        fieldnames = ["id", "name", "email", "department", "salary"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # writeheader() writes the fieldnames as the first row.
        # Without this the CSV would have no column headers.
        writer.writeheader()

        # writerows() writes a list of dicts, one dict per row.
        writer.writerows(employees)

    return {
        "message": f"Exported {len(employees)} employees to '{output_filename}'.",
        "filename": output_filename,
        "path": file_path,
        "total_exported": len(employees)
    }


# ═══════════════════════════════════════════════════════════════
#  JSON FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════

import json     # Python's built-in JSON encoder/decoder


# ── 1. Read a JSON file ───────────────────────────────────────
def read_json_file(filename: str) -> dict:
    """
    Reads a JSON file from REPORTS_DIR and returns its content
    as a Python dict or list (whatever the JSON contains at the top level).

    Args:
        filename – the JSON filename, e.g. "sample_data.json"

    Returns:
        dict with the filename and the parsed JSON content.

    Raises:
        FileNotFoundError – if the file does not exist.
        ValueError        – if the file contains invalid JSON.
        PermissionError   – if the filename tries to escape REPORTS_DIR.
    """

    file_path = safe_path(filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file '{filename}' does not exist.")

    # open() + json.load() — read and parse in one step.
    # json.load() reads from a file object (not a string).
    # It raises json.JSONDecodeError if the content is not valid JSON.
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            # json.load() parses the file content into a Python object.
            # A JSON object  {} becomes a Python dict.
            # A JSON array   [] becomes a Python list.
            # JSON strings   become Python str.
            # JSON numbers   become Python int or float.
            # JSON true/false become Python True/False.
            # JSON null       becomes Python None.
            data = json.load(json_file)

    except json.JSONDecodeError as error:
        # json.JSONDecodeError tells you exactly where the JSON broke.
        # error.lineno  = line number of the problem
        # error.colno   = column number of the problem
        # error.msg     = description of what went wrong
        raise ValueError(
            f"Invalid JSON in '{filename}': {error.msg} "
            f"(line {error.lineno}, column {error.colno})"
        )

    return {
        "filename": filename,
        "content": data
    }


# ── 2. Write JSON data to a file ──────────────────────────────
def write_json_file(filename: str, data: dict) -> dict:
    """
    Writes a Python dict (or list) to a JSON file in REPORTS_DIR.
    Overwrites the file if it already exists.

    Args:
        filename – the target filename, e.g. "config.json"
        data     – a Python dict or list to serialise as JSON.

    Returns:
        dict with a success message and the file path.

    Raises:
        PermissionError – if the filename tries to escape REPORTS_DIR.
        TypeError       – if data contains values that cannot be
                          converted to JSON (e.g. a datetime object).
    """

    file_path = safe_path(filename)

    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            # json.dump() converts the Python object to JSON text
            # and writes it directly to the file.
            #
            # indent=4 means the output is "pretty-printed" — each
            # nested level is indented by 4 spaces. Without indent,
            # everything would be on one line, which is hard to read.
            #
            # ensure_ascii=False means non-ASCII characters (like é, ñ, 中)
            # are written as-is instead of being escaped as \u00e9 etc.
            json.dump(data, json_file, indent=4, ensure_ascii=False)

    except TypeError as error:
        # TypeError happens if data contains something json can't handle —
        # for example a datetime object, a set, or a custom class.
        raise TypeError(
            f"Data contains a value that cannot be converted to JSON: {str(error)}"
        )

    return {
        "message": f"JSON data written to '{filename}' successfully.",
        "path": file_path
    }


# ── 3. Export employees to JSON ───────────────────────────────
def export_employees_to_json(output_filename: str) -> dict:
    """
    Queries all employees from MySQL and writes them to a JSON file
    in REPORTS_DIR.

    The output format is:
    {
        "exported_at": "...",
        "total_employees": N,
        "employees": [{"id": 1, "name": "..."}, ...]
    }

    Args:
        output_filename – the name for the exported JSON file.

    Returns:
        dict with the filename and number of employees exported.

    Raises:
        PermissionError – if the filename tries to escape REPORTS_DIR.
    """

    from database import get_connection
    import datetime  # used to record the export timestamp

    file_path = safe_path(output_filename)

    # ── Fetch all employees from MySQL ────────────────────────
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, department, salary FROM employees")
        employees = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()

    # mysql-connector returns DECIMAL columns as Python Decimal objects.
    # The json module cannot serialise Decimal — we must convert to float.
    # We loop through each employee and convert salary explicitly.
    employees_clean = []
    for emp in employees:
        employees_clean.append({
            "id":         emp["id"],
            "name":       emp["name"],
            "email":      emp["email"],
            "department": emp["department"],
            "salary":     float(emp["salary"])  # Decimal → float for JSON
        })

    # Build the final data structure to export.
    export_data = {
        # isoformat() gives a string like "2026-10-13T14:30:00.123456"
        # This is the standard way to represent dates/times in JSON.
        "exported_at":      datetime.datetime.now().isoformat(),
        "total_employees":  len(employees_clean),
        "employees":        employees_clean
    }

    # Write to file using our existing write_json_file function.
    # This avoids duplicating the open/dump logic.
    write_json_file(output_filename, export_data)

    return {
        "message": f"Exported {len(employees_clean)} employees to '{output_filename}'.",
        "filename": output_filename,
        "path": file_path,
        "total_exported": len(employees_clean)
    }
