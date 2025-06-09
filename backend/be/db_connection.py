import psycopg2
import psycopg2.extras  # For dictionary cursors
import os  # Import the os module
from dotenv import load_dotenv  # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Database Configuration ---
# Read credentials from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")  # Default to "localhost" if not found
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


def get_db_connection():
    """
    Establishes a connection to the PostgreSQL database using credentials
    loaded from environment variables.
    Returns a connection object.
    """
    # Check if essential database credentials are loaded
    if not all([DB_NAME, DB_USER, DB_PASS]):
        print("Error: Database credentials (DB_NAME, DB_USER, DB_PASS) are not fully set.")
        print("Please ensure they are defined in your .env file or environment variables.")
        return None

    try:
        conn = psycopg2.connect(host=DB_HOST,
                                database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS)
        print("Database connection established successfully using .env configuration.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None


def close_db_connection(conn):
    """
    Closes the database connection.
    """
    if conn:
        conn.close()
        print("Database connection closed.")

# --- Example Usage (optional, for testing this file directly) ---
# if __name__ == '__main__':
#     print("Attempting to connect to database using .env configuration...")
#     connection = get_db_connection()
#     if connection:
#         try:
#             with connection.cursor() as cur:
#                 cur.execute("SELECT version();")
#                 db_version = cur.fetchone()
#                 if db_version:
#                     print(f"PostgreSQL version: {db_version[0]}")
#                 else:
#                     print("Could not fetch PostgreSQL version.")
#         except psycopg2.Error as e:
#             print(f"Error during query execution: {e}")
#         finally:
#             close_db_connection(connection)
#     else:
#         print("Failed to establish database connection. Check your .env file and database server.")