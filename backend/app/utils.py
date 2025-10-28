import aiomysql
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from aiomysql import Connection
from typing import AsyncGenerator

# Load development envs
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.local"))

@asynccontextmanager
async def get_aiomysql_connection() -> AsyncGenerator[Connection, None]:
    """
    Provides an asynchronous MySQL connection using aiomysql.
    Uses environment variables for credentials. Automatically closes the connection.
    """

    db_user = os.getenv("DB_USER", "scraper_user")
    db_password = os.getenv("DB_PASSWORD", "youshouldchangethis")
    db_name = os.getenv("DB_NAME", "scraper_db")
    db_host = os.getenv("DB_HOST", "scraper_database")
    db_port = os.getenv("DB_PORT", "3306")

    try:
        conn = await aiomysql.connect(
            user=db_user,
            password=db_password,
            db=db_name,
            host=db_host,
            port=int(db_port)
        )
        yield conn
    finally:
        if 'conn' in locals():
            conn.close()


async def execute_mysql_query(
    conn,
    query: str,
    params: tuple = (),
    use_dictionary: bool = True,
    return_lastrowid: bool = False,
    return_rowcount: bool = False
) -> list | int:
    """
    Executes a MySQL query using aiomysql and returns the result.

    Args:
        conn: An active aiomysql conn object.
        query: The SQL query to execute.
        params: Parameters for the query (optional).
        use_dictionary: Whether to return results as dictionaries (True) or tuples (False).
        return_lastrowid: If True, returns the last inserted row ID.
        return_rowcount: If True, returns the number of rows affected by the query.

    Returns:
        A list of results (if use_dictionary=True), a tuple of results (if use_dictionary=False),
        the last row ID (if return_lastrowid=True), or the row count (if return_rowcount=True).
    """
    cursor_class = aiomysql.DictCursor if use_dictionary else aiomysql.Cursor

    async with conn.cursor(cursor_class) as cursor:
        await cursor.execute(query, params)

        # Commit changes for INSERT/UPDATE/DELETE queries
        if query.strip().lower().startswith(("insert", "update", "delete")):
            await conn.commit()

        if return_lastrowid:
            return cursor.lastrowid
        elif return_rowcount:
            return cursor.rowcount
        else:
            return await cursor.fetchall()
