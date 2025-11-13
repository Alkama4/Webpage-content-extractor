from fastapi import APIRouter, HTTPException
from typing import Any, List, Optional, Tuple
from aiomysql import Connection

# Pydantic models
from app.models.element import ElementCreate, ElementInDB, ElementOut, ElementPatch
from app.models.element_data import ElementData

# Project utils
from app.utils import get_aiomysql_connection, execute_mysql_query

router = APIRouter(prefix="/elements", tags=["elements"])


#######################  Helper functions  #######################

async def _fetch_all_elements(conn: Connection) -> List[dict]:
    query = """
        SELECT element_id, locator, metric_name, webpage_id
        FROM elements
        ORDER BY element_id;
    """
    return await execute_mysql_query(conn, query)


async def _fetch_element_by_id(conn: Connection, element_id: int) -> Optional[dict]:
    query = """
        SELECT element_id, locator, metric_name, webpage_id
        FROM elements
        WHERE element_id = %s;
    """
    rows = await execute_mysql_query(conn, query, (element_id,))
    return rows[0] if rows else None


async def _create_element(conn: Connection, data: ElementCreate, webpage_id: int) -> int:
    query = """
        INSERT INTO elements (locator, metric_name, webpage_id)
        VALUES (%s, %s, %s);
    """
    try:
        last_id = await execute_mysql_query(
            conn,
            query,
            params=(data.locator, data.metric_name, webpage_id),
            return_lastrowid=True
        )
        return last_id
    except Exception as exc:
        # Duplicate key (e.g., same locator on the same webpage)
        if hasattr(exc, "args") and len(exc.args) > 0 and "1062" in str(exc.args[0]):
            raise HTTPException(
                status_code=409, 
                detail={
                    "detail": "Locator must be unique per webpage",
                    "field": "locator",
                    "value": data.locator
                }
            )
        raise


async def _update_element_helper(
    conn: Connection,
    element_id: int,
    fields: List[Tuple[str, Any]]
) -> Tuple[int, Optional[dict]]:
    """
    Update a element with the supplied list of (column, value) tuples.
    Raises:
        HTTPException 404 if the record does not exist.
        HTTPException 409 if the new locator already exists for another
            element on the same webpage.
    Returns:
        rowcount, updated record (or None if not found)
    """
    # Get current webpage_id for this element
    curr_webpage_q = "SELECT webpage_id FROM elements WHERE element_id = %s"
    curr_res = await execute_mysql_query(conn, curr_webpage_q, params=[element_id])
    if not curr_res:
        return 0, None
    current_webpage_id = curr_res[0]["webpage_id"]

    # Determine new locator and webpage_id values from fields
    locator_field = next((val for col, val in fields if col == "locator"), None)
    webpage_id_field = next(
        (val for col, val in fields if col == "webpage_id"), current_webpage_id
    )

    # Check for duplicate locator on same webpage
    if locator_field is not None:
        dup_q = """
            SELECT 1 FROM elements
            WHERE webpage_id = %s AND locator = %s AND element_id <> %s
            LIMIT 1;
        """
        dup_res = await execute_mysql_query(
            conn,
            dup_q,
            params=[webpage_id_field, locator_field, element_id]
        )
        if dup_res:
            raise HTTPException(
                status_code=409, 
                detail={
                    "detail": "Locator must be unique per webpage",
                    "field": "locator",
                    "value": locator_field
                }
            )

    # Build UPDATE statement
    updates = [f"{col} = %s" for col, _ in fields]
    params = [val for _, val in fields]
    params.append(element_id)

    query = f"""
        UPDATE elements
        SET {', '.join(updates)}
        WHERE element_id = %s;
    """

    # Execute update and get affected rows count
    rowcount = await execute_mysql_query(
        conn,
        query,
        params=params,
        return_rowcount=True
    )

    # If no rows updated, verify existence again
    if rowcount == 0:
        exists_q = "SELECT 1 FROM elements WHERE element_id = %s"
        result = await execute_mysql_query(
            conn,
            exists_q,
            params=[element_id]
        )
        if not result:      # record truly missing
            return 0, None

    # Fetch and return updated record
    updated_record = await _fetch_element_by_id(conn, element_id)
    return rowcount, updated_record


async def _delete_element(conn: Connection, element_id: int) -> bool:
    query = """
        DELETE FROM elements WHERE element_id = %s;
    """
    rowcount = await execute_mysql_query(
        conn,
        query,
        params=(element_id,),
        return_rowcount=True
    )
    return rowcount > 0


async def _fetch_element_data_by_element(conn: Connection, element_id: int) -> List[dict]:
    query = """
        SELECT data_id, element_id, value, created_at
        FROM element_data
        WHERE element_id = %s
        ORDER BY created_at;
    """
    return await execute_mysql_query(conn, query, (element_id,))


async def _fetch_element_logs(conn: Connection, element_id: int) -> List[dict]:
    query = """
        SELECT 
            el.element_log_id,
            el.webpage_log_id,
            el.element_id,
            e.metric_name,
            el.attempted_at,
            el.status,
            el.message
        FROM element_logs el
        JOIN elements e ON el.element_id = e.element_id
        WHERE el.element_id = %s
        ORDER BY el.attempted_at;
    """
    return await execute_mysql_query(conn, query, (element_id,))


########################  Endpoints  ########################

@router.get("/", response_model=List[ElementInDB])
async def get_elementss():
    """Return an array of all elements jobs."""
    async with get_aiomysql_connection() as conn:
        rows = await _fetch_all_elements(conn)
        return rows


@router.post("/{webpage_id}", status_code=201, response_model=ElementInDB)
async def create_element(webpage_id: int, element: ElementCreate):
    """
    Create a new element job for the given webpage.
    The `webpage_id` must exist - MySQL will raise an FK error otherwise.
    """
    async with get_aiomysql_connection() as conn:
        last_id = await _create_element(conn, element, webpage_id)

        new_record = await _fetch_element_by_id(conn, last_id)
        return new_record


@router.get("/{element_id}", response_model=ElementInDB)
async def get_element(element_id: int):
    """Return the single element with that ID."""
    async with get_aiomysql_connection() as conn:
        row = await _fetch_element_by_id(conn, element_id)
        if not row:
            raise HTTPException(status_code=404, detail="Element not found")
        return row


@router.put("/{element_id}", response_model=ElementOut)
async def replace_element(element_id: int, element: ElementCreate):
    """
    Full replacement of a element. All fields are required.
    """
    async with get_aiomysql_connection() as conn:
        # build the list of columns to update
        fields = [("locator", element.locator), ("metric_name", element.metric_name)]
        rowcount, updated_record = await _update_element_helper(conn, element_id, fields)

        if not updated_record:
            raise HTTPException(status_code=404, detail="Element not found")

        # flag is true only if a row was actually changed
        updated_record["updated"] = rowcount > 0
        return updated_record


@router.patch("/{element_id}", response_model=ElementOut)
async def patch_element(element_id: int, element: ElementPatch):
    """
    Patch an existing element - only the fields you send will be updated.
    """
    async with get_aiomysql_connection() as conn:
        fields = []
        if element.locator is not None:
            fields.append(("locator", element.locator))
        if element.metric_name is not None:
            fields.append(("metric_name", element.metric_name))

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        rowcount, updated_record = await _update_element_helper(conn, element_id, fields)

        if not updated_record:
            raise HTTPException(status_code=404, detail="element not found")

        updated_record["updated"] = rowcount > 0
        return updated_record


@router.delete("/{element_id}")
async def delete_element(element_id: int):
    """Delete the element - its data is removed via FK cascade."""
    async with get_aiomysql_connection() as conn:
        success = await _delete_element(conn, element_id)
        if not success:
            raise HTTPException(status_code=404, detail="Element not found")
        return {"msg": "Element deleted"}


@router.get("/{element_id}/logs")
async def get_element_logs(element_id: int):
    """
    Get the logs for a element using its `element_id`.
    """
    async with get_aiomysql_connection() as conn:
        rows = await _fetch_element_logs(conn, element_id)
        return rows
    

@router.get("/{element_id}/data", response_model=List[ElementData])
async def get_element_data(element_id: int):
    """Retrieve all data points for a particular element."""
    async with get_aiomysql_connection() as conn:
        # Ensure the element exists first
        if not await _fetch_element_by_id(conn, element_id):
            raise HTTPException(status_code=404, detail="element not found")

        rows = await _fetch_element_data_by_element(conn, element_id)
        return rows
