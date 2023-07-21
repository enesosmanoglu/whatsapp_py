
from typing import Any, NamedTuple
from pyodbc import Row

from column import Column

class SqlResult(NamedTuple):
    """Contains the information about a SQL query result.

    Attributes:
        rows (list[Row]): The rows of the result.
        rows_dict (list[dict[str, Any]]): The rows of the result as a list of dictionaries.
        affected_rows (int): The number of rows affected by the query.
        messages (list[str]): The messages returned by the query.
        columns (dict[str, Column]): The columns of the result.
    """
    rows: list[Row]
    rows_dict: list[dict[str, Any]]
    affected_rows: int
    messages: list[str]
    columns: dict[str, Column]