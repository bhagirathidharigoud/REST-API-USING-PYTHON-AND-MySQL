# ─────────────────────────────────────────────────────────────
# database.py  –  MySQL connection logic
#
# Responsibility:
#   • Reads database credentials from the .env file.
#   • Provides get_connection() — a function that opens and
#     returns one fresh MySQL connection.
#   • Every other file calls get_connection() when it needs
#     to run a SQL query.
#
# Why not keep the connection open permanently?
#   Opening one connection per request is safe for a beginner
#   project. Each request gets its own connection, uses it,
#   then closes it. This avoids stale-connection bugs.
# ─────────────────────────────────────────────────────────────

import os                          # os lets us read environment variables
import mysql.connector             # the MySQL driver we installed
from dotenv import load_dotenv     # reads the .env file into os.environ

# load_dotenv() looks for a file named .env in the current directory
# and loads every KEY=VALUE pair into the environment.
# After this line, os.getenv("DB_HOST") returns "localhost", etc.
load_dotenv()


def get_connection():
    """
    Opens a new connection to the MySQL database and returns it.

    Returns:
        mysql.connector.connection.MySQLConnection

    Raises:
        mysql.connector.Error — if the credentials are wrong,
        the server is not running, or the database does not exist.
    """

    # os.getenv("KEY") reads the value from the environment.
    # If the key is missing it returns None, so we supply a
    # sensible default for port (3307 is MySQL's standard port).
    connection = mysql.connector.connect(
        host     = os.getenv("DB_HOST", "localhost"),
        port     = int(os.getenv("DB_PORT", 3307)),  # port must be an integer
        user     = os.getenv("DB_USER", "root"),
        password = os.getenv("DB_PASSWORD", ""),
        database = os.getenv("DB_NAME", "employee_db")
    )

    # Return the open connection to whoever called this function.
    # The caller is responsible for closing it when done.
    return connection
