from typing import Any, NamedTuple

class Column(NamedTuple):
    """Contains the information about a column in a table.
    
    Attributes:
        name (str): The name of the column.
        type (Any): The type of the column.
        nullable (bool): Whether or not the column can be null.
    """
    name: str
    type: Any
    nullable: bool
