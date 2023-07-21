from typing import Any, NamedTuple

class ConnectionConfig(NamedTuple):
    """
        See [pyodbc wiki](https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-databases) for more information.
    """
    Driver: str
    """The name of the driver to be used to connect to the database. This is optional and if not specified, the connection will be made using the default SQL Server driver."""

    Server: str
    """The name of the server to which a connection is established."""

    Database: str
    """The name of the database on the server."""

    Trusted_Connection: bool = None
    """If yes, the connection will be established using Windows Authentication. If no, the connection will be established using SQL Server Authentication and the user name and password specified."""

    UID: str = None
    """The user name used to authenticate."""

    PWD: str = None
    """The password for the user name."""

    Encrypt: bool = None
    """If yes, the connection will be encrypted. If no, the connection will not be encrypted."""

    LongAsMax: bool = None
    """If yes, the SQL_LONGVARCHAR and SQL_LONGVARBINARY data types will be treated as SQL_VARCHAR and SQL_VARBINARY. If no, the SQL_LONGVARCHAR and SQL_LONGVARBINARY data types will be treated as SQL_LONGVARCHAR and SQL_LONGVARBINARY."""

    APP: str = None
    """The name of the application associated with the connection."""

    def __value(self, value: Any) -> str:
        if type(value) is bool:
            return "yes" if value else "no"
        return str(value)

    def __str__(self) -> str:
        return ";".join(
            [
                f"{key}={self.__value(value)}"
                for key, value in self._asdict().items()
                if value is not None
            ]
        )
