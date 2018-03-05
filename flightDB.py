import mysql.connector
from mysql.connector import errorcode
from dbconfig import config
from datetime import datetime

try:
    print('Connecting to database...')
    conn = mysql.connector.connect(**config)
    print('Connection to MySQl successful')
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print('MySQL access denied: Invalid credentials')
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print('MySQL Database does not exist')
    else:
        print(err)

def closeConnection():
    global conn

    print('Terminating database connection')
    conn.close();

def addFlights(flights):
    global conn
    print('Inserting flights...')

    for flight in flights:
        cursor = conn.cursor()
        statement = ("""INSERT INTO flights
                (price, departFlightNo, departDate, departTime, departRoute, departConnection, returnFlightNo,
                returnDate, returnTime, returnRoute, returnConnection, createDate)
                VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"""
                     .format(flight['price'],flight['departFlightNum'],flight['departFlightDate'],flight['departFlightTime'],
                             flight['departRoute'],flight['connectingFlightOut'],flight['returnFlightNum'],flight['returnFlightDate'],
                             flight['returnFlightTime'],flight['returnRoute'],flight['connectingFlightIn'],str(datetime.now())))

        cursor.execute(statement)
        cursor.close()
        conn.commit()