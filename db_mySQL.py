import mysql.connector
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.sql import text


# This class deals with logging into the sql server and inserting new jobs into it
# Planning on adding additional functionality to work with a constructed api to pull data from the server
class mySQL:

    def __init__(self):
        self.pw, self.db_name, self.db_connection = '', '', ''

    # Logs into the mySQL server using details from the provided text file
    # Then logs into the proper database (will be used for the api)
    def login(self):
        with open('login.txt', 'r') as f:
            splitText = []
            for item in f:
                line = item.split(',')
                for piece in line:
                    splitText.append(piece.strip())
            self.pw, self.db_name = splitText[0], splitText[1]
        f.close()
        server_connection = self.server_connect()
        self.db_creation(
            server_connection, "CREATE DATABASE IF NOT EXISTS jobs")
        self.db_connection = self.db_connect()

    # Connects to the mySQL server
    def server_connect(self):
        connection = None
        currentTime = str(datetime.now())
        try:
            connection = mysql.connector.connect(
                host='localhost', user='root', passwd=self.pw)
            with open('Server Log.txt', 'a') as file:
                file.write('Connected to ' + 'localhost' +
                           ' on ' + currentTime + '\n')
        except Exception as err:
            with open('Server Log.txt', 'a') as file:
                file.write('Failed to connect to ' +
                           'localhost ' + 'due to ' + str(err) + ' on ' + currentTime + '\n')
        return connection

    # Realistically only does this on first-time setup
    def db_creation(self, connection, query):
        currentTime = str(datetime.now())
        try:
            connection.cursor().execute(query)
        except Exception as err:
            with open('Server Log.txt', 'a') as file:
                file.write('Failed to create database (jobs) due to ' +
                           str(err) + ' on ' + currentTime + '\n')

    # Connects to the respective database
    def db_connect(self):
        connection = ''
        currentTime = str(datetime.now())
        try:
            connection = create_engine("mysql+pymysql://root:"
                                       + self.pw + "@" + 'localhost' + "/" + self.db_name)
            with open('Server Log.txt', 'a') as file:
                file.write('Connected to database (' +
                           str(self.db_name) + ') on ' + currentTime + '\n')
        except Exception as err:
            with open('Server Log.txt', 'a') as file:
                file.write('Failed to connect to database (' + str(self.db_name) + ') due to ' +
                           str(err) + ' on ' + currentTime + '\n')
        return connection

    # Inserts the data to the indicated table using an sqlalchemy engine
    def sql_insert_jobs(self, dataFrame, tableTitle):

        dataFrame.to_sql(con=self.db_connection, name=str(
            tableTitle), if_exists='append')
        try:
            query = text("ALTER TABLE " + tableTitle +
                         " ADD job_id int AUTO_INCREMENT PRIMARY KEY")
            with self.db_connection.connect() as con:
                con.execute(query)
        except Exception as err:
            with open('Operation Log.txt', 'a') as f:
                f.write(
                    'Exception occurred when trying to add primary key ' + str(err) + '\n')
        with open('Operation Log.txt', 'a') as f:
            f.write('Recorded new jobs in mySQL @' +
                    str(datetime.now()) + '\n')
