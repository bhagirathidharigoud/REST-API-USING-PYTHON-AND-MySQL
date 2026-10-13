# ─────────────────────────────────────────────────────────────
# employee_queries.py  –  All SQL operations for the employees table
#
# Responsibility:
#   • One function per operation (add, get all, get one, update,
#     delete, search).
#   • Each function opens a connection, runs SQL, closes the
#     connection, and returns plain Python data (dict or list).
#   • main.py calls these functions and converts the result to JSON.
#
# Rule: No HTTP logic here. No FastAPI imports. Pure data logic.
# ─────────────────────────────────────────────────────────────

from database import get_connection   # our connection helper from database.py


# ── 1. ADD AN EMPLOYEE ───────────────────────────────────────
def add_employee(name: str, email: str, department: str, salary: float) -> dict:
    """
    Inserts one new employee into the database.

    Args:
        name       – employee's full name
        email      – must be unique across all employees
        department – team or department name
        salary     – monthly salary as a decimal number

    Returns:
        dict with the new employee's auto-generated id and all fields.

    Raises:
        ValueError  – if the email already exists in the database.
        Exception   – for any unexpected database error.
    """

    # Open a fresh connection for this operation.
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # The INSERT SQL statement.
        # %s is a placeholder — mysql-connector replaces each %s
        # with the matching value from the tuple below.
        # We NEVER use f-strings or string concatenation with SQL
        # because that opens the door to SQL injection attacks.
        insert_sql = """
            INSERT INTO employees (name, email, department, salary)
            VALUES (%s, %s, %s, %s)
        """

        # The tuple of values. The order must match the column order above.
        values = (name, email, department, salary)

        cursor.execute(insert_sql, values)

        # commit() saves the INSERT permanently.
        # Without commit(), the row is visible only in this session
        # and disappears when the connection closes.
        connection.commit()

        # cursor.lastrowid is the AUTO_INCREMENT id MySQL assigned
        # to the row we just inserted. Very useful to return to the client.
        new_id = cursor.lastrowid

        return {
            "id": new_id,
            "name": name,
            "email": email,
            "department": department,
            "salary": salary
        }

    except Exception as error:
        # If anything went wrong, undo any partial changes.
        connection.rollback()

        # Error 1062 is MySQL's code for "Duplicate entry" (UNIQUE constraint).
        # We check the error message to give a clear, specific message.
        if "1062" in str(error):
            raise ValueError(f"Email '{email}' is already registered.")

        # For any other error, re-raise it so main.py can handle it.
        raise error

    finally:
        # finally always runs — even if an exception occurred.
        # Always close the cursor and connection to free resources.
        cursor.close()
        connection.close()


# ── 2. GET ALL EMPLOYEES ─────────────────────────────────────
def get_all_employees() -> list:
    """
    Retrieves every employee from the database.

    Returns:
        List of dicts, one per employee. Empty list if table is empty.
    """

    connection = get_connection()

    try:
        # dictionary=True tells the cursor to return each row as a
        # dict {"id": 1, "name": "Alice"} instead of a plain tuple (1, "Alice").
        # Dicts are much easier to work with and to convert to JSON.
        cursor = connection.cursor(dictionary=True)

        select_sql = "SELECT id, name, email, department, salary FROM employees"

        cursor.execute(select_sql)

        # fetchall() returns a list of all matching rows.
        # If the table is empty, it returns an empty list [].
        employees = cursor.fetchall()

        return employees

    finally:
        cursor.close()
        connection.close()


# ── 3. GET ONE EMPLOYEE BY ID ────────────────────────────────
def get_employee_by_id(employee_id: int) -> dict:
    """
    Retrieves a single employee by their primary key.

    Args:
        employee_id – the integer id from the URL path.

    Returns:
        A dict with the employee's data.

    Raises:
        ValueError – if no employee with that id exists.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        select_sql = """
            SELECT id, name, email, department, salary
            FROM employees
            WHERE id = %s
        """

        # Note: always pass the value as a tuple, even for a single value.
        # Writing (%s, employee_id) would be a string format, not SQL params.
        # The correct syntax is (employee_id,) — the trailing comma makes it a tuple.
        cursor.execute(select_sql, (employee_id,))

        # fetchone() returns one row dict, or None if no row matched.
        employee = cursor.fetchone()

        if employee is None:
            raise ValueError(f"No employee found with id {employee_id}.")

        return employee

    finally:
        cursor.close()
        connection.close()


# ── 4. UPDATE AN EMPLOYEE ────────────────────────────────────
def update_employee(
    employee_id: int,
    name: str,
    email: str,
    department: str,
    salary: float
) -> dict:
    """
    Updates all fields for an existing employee.

    Args:
        employee_id – the id of the employee to update.
        name, email, department, salary – new values.

    Returns:
        A dict with the updated employee data.

    Raises:
        ValueError – if the employee does not exist, or the new
                     email is already used by a different employee.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # First, verify the employee exists.
        # If not, raise an error before attempting the UPDATE.
        cursor.execute("SELECT id FROM employees WHERE id = %s", (employee_id,))
        if cursor.fetchone() is None:
            raise ValueError(f"No employee found with id {employee_id}.")

        update_sql = """
            UPDATE employees
            SET name       = %s,
                email      = %s,
                department = %s,
                salary     = %s
            WHERE id = %s
        """

        # Values tuple: the order must match the SET clause above,
        # with employee_id at the end for the WHERE clause.
        cursor.execute(update_sql, (name, email, department, salary, employee_id))
        connection.commit()

        # Return the updated data so the client can confirm the changes.
        return {
            "id": employee_id,
            "name": name,
            "email": email,
            "department": department,
            "salary": salary
        }

    except Exception as error:
        connection.rollback()

        if "1062" in str(error):
            raise ValueError(f"Email '{email}' is already used by another employee.")

        raise error

    finally:
        cursor.close()
        connection.close()


# ── 5. DELETE AN EMPLOYEE ────────────────────────────────────
def delete_employee(employee_id: int) -> dict:
    """
    Permanently removes an employee from the database.

    Args:
        employee_id – the id of the employee to remove.

    Returns:
        A dict confirming which employee was deleted.

    Raises:
        ValueError – if no employee with that id exists.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        # Fetch the employee first so we can include their name in the
        # confirmation message. Also lets us detect "not found" early.
        cursor.execute(
            "SELECT id, name FROM employees WHERE id = %s",
            (employee_id,)
        )
        employee = cursor.fetchone()

        if employee is None:
            raise ValueError(f"No employee found with id {employee_id}.")

        # Now delete the row.
        cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        connection.commit()

        return {
            "message": f"Employee '{employee['name']}' (id={employee_id}) deleted successfully."
        }

    except Exception as error:
        connection.rollback()
        raise error

    finally:
        cursor.close()
        connection.close()


# ── 6. SEARCH EMPLOYEES ──────────────────────────────────────
def search_employees(keyword: str) -> list:
    """
    Searches employees whose name OR department contains the keyword.
    The search is case-insensitive.

    Args:
        keyword – a partial string to search for.
                  Example: "eng" matches "Engineering", "Engel", etc.

    Returns:
        List of matching employee dicts. Empty list if none match.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        # LIKE with % wildcards means "contains this text anywhere".
        # %keyword% matches "Engineering", "Senior Engineer", etc.
        # LOWER() converts both the column and keyword to lowercase
        # so the search is case-insensitive.
        search_sql = """
            SELECT id, name, email, department, salary
            FROM employees
            WHERE LOWER(name)       LIKE LOWER(%s)
               OR LOWER(department) LIKE LOWER(%s)
        """

        # We need to wrap the keyword in % wildcards before passing it.
        # We build the pattern in Python, not in the SQL string itself,
        # so it is still a safe parameterised query.
        like_pattern = f"%{keyword}%"

        # The same pattern is used twice — once for name, once for department.
        cursor.execute(search_sql, (like_pattern, like_pattern))

        results = cursor.fetchall()
        return results

    finally:
        cursor.close()
        connection.close()
