import psycopg2

connection = psycopg2.connect(user="postgres", password="qazedcrfvs1A")
cursor = connection.cursor()


def create_table_users():
    create_table_query = '''CREATE TABLE USERS (ID TEXT, USERNAME TEXT, PASSWORD TEXT)'''
    cursor.execute(create_table_query)
    connection.commit()
    return "Table 'Users' have been created successfully"


def create_table_transports():
    create_table_query = '''CREATE TABLE TRANSPORT 
    (ID TEXT, canBeRented BOOLEAN, transportType TEXT, model TEXT,
    color TEXT, identifier TEXT, description TEXT, latitude real,
    longitude real, minutePrice real, dayPrice real, ownerID TEXT)'''
    cursor.execute(create_table_query)
    connection.commit()

def delete_transport_table():
    cursor.execute("DROP TABLE TRANSPORT")
    connection.commit()
    return "Table TRANSPORT have been deleted successfully"

def create_rents_table():
    cursor.execute('''CREATE TABLE RENTS
    (ID TEXT, transportid TEXT, rentorid TEXT, renttype TEXT, cost real, start real)''')
    connection.commit()
    return "Table RENTS have created successfully"

def delete_rents_table():
    cursor.execute("DROP TABLE RENTS")
    connection.commit()
    return "Table RENTS have been deleted successfully"

def show_rents_table():
    cursor.execute("SELECT * FROM RENTS")
    a = cursor.fetchall()
    print(a)

# create_rents_table()
def show_transport_table():
    cursor.execute("SELECT * FROM TRANSPORT")
    a = cursor.fetchall()
    print(a)

# delete_rents_table()
# create_rents_table()
show_rents_table()

# cursor.execute("UPDATE TRANSPORT SET longitude = 456.0")
# connection.commit()