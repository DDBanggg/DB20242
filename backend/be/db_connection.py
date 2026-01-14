import psycopg2
import psycopg2.extras  # Import extras để dùng RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Database Configuration ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_db_connection():
    """Tạo kết nối đến PostgreSQL."""
    if not all([DB_NAME, DB_USER, DB_PASS]):
        print("Error: Thiếu thông tin DB trong file .env")
        return None

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def close_db_connection(conn):
    """
    Đóng kết nối database.
    (Giữ lại hàm này để tương thích với các module cũ)
    """
    if conn:
        try:
            conn.close()
        except Exception:
            pass

def execute_query(sql, params=None):
    """
    Dùng cho lệnh SELECT.
    Trả về danh sách dictionary (JSON-ready).
    """
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        # Sử dụng RealDictCursor để kết quả trả về là Dictionary {cot: gia_tri}
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            result = cur.fetchall()
            return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return []
    finally:
        close_db_connection(conn)

def execute_non_query(sql, params=None, return_id=False):
    """
    Dùng cho lệnh INSERT, UPDATE, DELETE.
    - return_id=True: Sẽ trả về ID của dòng vừa Insert (Yêu cầu SQL phải có 'RETURNING id')
    """
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            
            # Nếu yêu cầu trả về ID (dành cho Insert lấy ID ngay lập tức)
            if return_id:
                new_id = cur.fetchone()[0]
                conn.commit()
                return new_id
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error executing non-query: {e}")
        conn.rollback()
        return None
    finally:
        close_db_connection(conn)