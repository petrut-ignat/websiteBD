import mysql.connector

try:
    connection = mysql.connector.connect(host='127.0.0.1',
                                         database='modellingagency',
                                         user='root',
                                         password='petrut123#')

    mySql_Create_Table_Query = ("select * from fotomodel")

    cursor = connection.cursor()
    cursor.execute(mySql_Create_Table_Query)
    for i in cursor:
        print(type(i))

except mysql.connector.Error as error:
    print("Failed to create table in MySQL: {}".format(error))
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")