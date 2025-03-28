#utf-8
import mysql.connector
from datetime import datetime 
from mysql.connector import Error
class Main:
    def __init__(self):
        self.__init__=self

    def conn(self):
            conn_1 = mysql.connector.connect(
                host='110.41.57.192',
                user='root',
                password='Zzm8023.',
                database='ZGWL_db',
                port=3306
            )
            cursor = conn_1.cursor()
            cursor.execute('SELECT user,password FROM USERS;')
            a=cursor.fetchall()
            for i in a:
                 
                print(i[0],i[1])
