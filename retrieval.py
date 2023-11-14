import json
import os
import sqlite3

"""
For querying and inserting data
"""



#JSON
class NotAFile(Exception):

    """
    When inserted file is not a file
    """

    pass


class NotJson(Exception):

    """
    When not a json file
    """

    pass

#SQL
conn = sqlite3.connect("sqlite_databases")
c = conn.cursor()
# For deleting
# c.execute("""
#      DROP TABLE messages;
# """)
c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
    dm_bool INTEGER,
    channel_id INTEGER,
    dm_user INTEGER,
    date_seconds INTEGER,
    repeat INTEGER,
    msg TEXT
    );
    """)


class Retrieval:

    """
    Retrieve from json file
    """

    sqlData: list
    # #Json
    # jsonData: dict

    # #Static because no instanciated objects
    # @staticmethod
    # def retrieve(fName: str) -> dict:
    #     """
    #     Query from json file
    #     """

    #     if not os.path.isfile(fName):
    #         raise NotAFile
        
    #     if fName[-5:] != ".json":
    #         raise NotJson
        
    #     with open(fName) as f:
    #         Retrieval.jsonData = json.load(f)

    #     return Retrieval.jsonData


    # @staticmethod
    # def send(fName: str, jsonData: dict) -> None:
    #     """
    #     Insert to data
    #     """
        
    #     if fName[-5:] != ".json":
    #         raise NotJson
        
    #     with open(fName, 'w') as f:
    #         Retrieval.jsonData = json.dump(jsonData, f, indent=2)

    #     Retrieval.jsonData = jsonData




    #SQLite
    @staticmethod
    def insert(msg:list) -> None:
        """
        Insert tuple/tuple list into the sql database
        """
        if isinstance(msg,tuple):
            msg = [msg]
        c.executemany("INSERT INTO messages VALUES (?,?,?,?,?,?);",msg)
        conn.commit()
        


    @staticmethod
    def queryAllDate() -> list:
        """
        Query from database
        """

        c.execute("""
        SELECT rowid,*
        FROM messages
        WHERE dm_bool = 0
        ORDER BY date_seconds;
        """)

        Retrieval.sqlData = c.fetchall()
        return Retrieval.sqlData
    
    @staticmethod
    def queryAllDate() -> list:
        """
        Query from database
        """

        c.execute("""
        SELECT rowid,*
        FROM messages
        WHERE dm_bool = 0
        ORDER BY date_seconds;
        """)

        Retrieval.sqlData = c.fetchall()
        return Retrieval.sqlData
    
    @staticmethod
    def queryAllDateDM(user_id: int) -> list:
        """
        Query from database
        """

        c.execute("""
        SELECT rowid,*
        FROM messages
        WHERE dm_bool = 1 AND dm_user = ?
        ORDER BY date_seconds;
        """,(user_id,))

        Retrieval.sqlData = c.fetchall()
        return Retrieval.sqlData
    
    
    @staticmethod
    def querySoon() -> list:
        """
        Query for earliest date
        """

        c.execute("""
        SELECT messages.rowid,*
        FROM messages
        JOIN (SELECT MIN(date_seconds) AS max_sec FROM messages)
        ON max_sec = date_seconds;
        
        """)
        Retrieval.sqlData = c.fetchall()
        return Retrieval.sqlData
    

    @staticmethod
    def delete(row:int) -> None:
        c.execute("DELETE FROM messages WHERE rowid = ?",(row,))
        conn.commit()
    

    






        

        