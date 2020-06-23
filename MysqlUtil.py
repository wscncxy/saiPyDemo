from mysql.connector import (connection)
from mysql.connector import Error
from mysql.connector import errorcode

# pip3 install mysql-connector-python
class MysqlUtil:
    def __init__(self, url, user, pwd, db):
        self.mysql={}
        self.mysql["url"]=url
        self.mysql["user"]=user
        self.mysql["pwd"]=pwd
        self.mysql["db"]=db

    def con(self):
        try:
            cnx = connection.MySQLConnection(user=self.mysql["user"],
                                                    password=self.mysql["pwd"],
                                                    host=self.mysql["url"],
                                                    db=self.mysql["db"],
                                                    port=3307)
            return cnx
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def query(self,sql,params):
        cnx =self.con()
        self.mysql["cnx"] =cnx
        cursor = cnx.cursor()
        cursor.execute(sql, params)
        return cursor

    def close(self):
        self.mysql["cnx"].close()



