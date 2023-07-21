from typing import Any, Self
import pyodbc
from column import Column
from sql_result import SqlResult
from connection_config import ConnectionConfig

class SQL:
    """A class that represents a connection to a SQL Server database. 
    
    Info:
        **Connects to the database during initialization and closes the connection during destruction.**

    * Uses [pyodbc module](https://github.com/mkleehammer/pyodbc) to connect to the database.
    * Uses [ConnectionConfig](connection_config.md) to configure the connection.
    * Uses [SqlResult](sql_result.md) to represent the result of a SQL query.
    * Uses [Column](column.md) to represent a column in a table.
    * Uses [Row (from pyodbc)](https://github.com/mkleehammer/pyodbc/wiki/Row) to represent a row in a table.

    Args:
        connection_config (ConnectionConfig): The configuration of the connection.
        autocommit (bool, optional): Whether or not to automatically commit changes. Defaults to False.
        debug (bool, optional): Whether or not to print debug information. Defaults to False.
    """
    def __init__(
        self,
        connection_config: ConnectionConfig,
        autocommit: bool = False,
        debug: bool = False,
    ):
        self.debug: bool = debug
        """Whether or not to print debug information."""

        if self.debug:
            print(f"Connecting to SQL Server with:")
            for key, value in connection_config._asdict().items():
                print(f" └─╴ {key}={value}")

        self.__cnxn = pyodbc.connect(str(connection_config), autocommit=autocommit)
        self.__cursor = self.__cnxn.cursor()

    def execute(self, sql: str, *params: Any) -> SqlResult:
        """Executes a SQL query.

        Args:
            sql (str): The SQL query to execute.
            *params (Any): The parameters to replace the question marks in the SQL query with.

        Returns:
            SqlResult: The result of the SQL query.
        """
        self.__cursor.execute(sql, *params)

        # replace ? with args
        sql = sql.replace("?", "{}").format(*params)

        try:
            result = self.__cursor.fetchall()
        except pyodbc.ProgrammingError:
            # No result
            result = []

        rows_dict = [
            dict(zip([column[0] for column in self.__cursor.description], row))
            for row in result
        ]
        desc_dict = None
        if self.debug:
            print("-" * 100)
            splitter = "\n└─╴ "
            splitter2 = "\n  └─╴ "
            splitter3 = "\n─╴"
            print(f"SQL:{splitter}{splitter.join(sql.splitlines())}")
            if self.__cursor.description is not None:
                """
                column name (or alias, if specified in the SQL)
                type code
                display size (pyodbc does not set this value)
                internal size (in bytes)
                precision
                scale
                nullable (True/False)
                """
                # create dict from the description using keys 0, 1, 6
                # 0: column name
                # 1: type code
                # 6: nullable
                # desc_dict = dict(zip([column[0] for column in self.__cursor.description], [(column[1], column[6]) for column in self.__cursor.description]))
                desc_dict = dict(
                    zip(
                        [column[0] for column in self.__cursor.description],
                        [
                            Column(column[0], column[1], column[6])
                            for column in self.__cursor.description
                        ],
                    )
                )
                print(
                    f"Description:{splitter}{splitter.join([desc_key+' '+str(desc_val) for desc_key, desc_val in desc_dict.items()])}"
                )
            if len(result) > 0:
                # print(f"Result:{splitter}{splitter.join([str(row) for row in result])}")
                print(
                    f"Result:{splitter3}{splitter3.join((splitter2).join([f'{key} = {value}' for key, value in row.items()]) for row in rows_dict)}"
                )
            if self.__cursor.rowcount != -1:
                print(f"Affected Rows:{splitter}{self.__cursor.rowcount}")

            if len(self.__cursor.messages) > 0:
                print(
                    f"Messages:{splitter}{splitter.join([str(msg) for msg in self.__cursor.messages])}"
                )
            print("-" * 100)

        # if len(result) == 0:
        #     return {}

        # return data

        res = {
            "rows": result,
            "rows_dict": rows_dict,
            "affected_rows": self.__cursor.rowcount,
            "messages": self.__cursor.messages,
            "columns": desc_dict,
        }
        return SqlResult(**res)

    # def execute_many(self, sql: str, values: list) -> list(Row):
    #     self.__cursor.executemany(sql, values)

    #     result = self.__cursor.fetchall()
    #     return result

    def commit(self) -> Self:
        """Commit all SQL statements executed on the connection since the last commit/rollback.

        Warning: If you don't enable `autocommit`:
            Make sure to call this method after making changes to the database. Otherwise, the changes will not be saved.

        Returns:
            sql (SQL): The current SQL instance.
        """
        self.__cnxn.commit()
        return self

    def rollback(self) -> Self:
        """Rollback all SQL statements executed on the connection since the last commit/rollback.

        Returns:
            sql (SQL): The current SQL instance.
        """
        self.__cnxn.rollback()
        return self
    
    def close(self) -> Self:
        """Close the connection.  Any uncommitted SQL statements will be rolled back.
        
        Returns:
            sql (SQL): The current SQL instance.
        """
        self.__cnxn.close()
        return self


if __name__ == "__main__":
    print(pyodbc.drivers())

    sql = SQL(
        ConnectionConfig(
            # https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-databases
            Driver="ODBC Driver 17 for SQL Server",
            Server="localhost",
            Database="DbWhatsApp",
            Trusted_Connection=True,
            Encrypt=False,
            LongAsMax=True,
            APP="Python App Test",
        ),
        # autocommit=True,
        debug=True,
    )

    result = sql.execute("SELECT * FROM Tasks")

    import json

    print(json.dumps(result._asdict(), indent=2, default=str))
