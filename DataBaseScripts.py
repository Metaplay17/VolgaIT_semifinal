import psycopg2

connection = psycopg2.connect(user="postgres", password="qazedcrfvs1A")
cursor = connection.cursor()


def create_table_balances():
    create_table_query = '''CREATE TABLE BALANCES (userid TEXT, balance real)'''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table BALANCES have been created successfully")


def delete_table_balances():
    cursor.execute("DROP TABLE BALANCES")
    connection.commit()
    print("Table BALANCES have been deleted successfully")


def show_table_balances():
    cursor.execute("SELECT * FROM BALANCES")
    a = cursor.fetchall()
    print(a)


def create_table_users():
    create_table_query = '''CREATE TABLE USERS (id TEXT, username TEXT, password TEXT, privilege TEXT)'''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table USERS have been created successfully")


def show_table_users():
    cursor.execute('''SELECT * FROM USERS''')
    a = cursor.fetchall()
    print(a)


def delete_table_users():
    cursor.execute("DROP TABLE USERS")
    connection.commit()
    print("Table USERS have been deleted successfully")


def create_table_transport():
    create_table_query = '''CREATE TABLE TRANSPORT 
    (id TEXT, canBeRented BOOLEAN, transportType TEXT, model TEXT,
    color TEXT, identifier TEXT, description TEXT, latitude TEXT,
    longitude TEXT, minutePrice TEXT, dayPrice TEXT, ownerid TEXT)'''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table TRANSPORT have been created successfully")


def show_table_transport():
    cursor.execute("SELECT * FROM TRANSPORT")
    a = cursor.fetchall()
    print(a)


def delete_table_transport():
    cursor.execute("DROP TABLE TRANSPORT")
    connection.commit()
    print("Table TRANSPORT have been deleted successfully")


def create_table_rents():
    cursor.execute('''CREATE TABLE RENTS
    (rentid TEXT, transportid TEXT, rentorid TEXT, start TEXT, end TEXT unitprice real, 
    pricetype TEXT finalprice real)''')
    connection.commit()
    print("Table RENTS have created successfully")


def show_table_rents():
    cursor.execute("SELECT * FROM RENTS")
    a = cursor.fetchall()
    print(a)


def delete_table_rents():
    cursor.execute("DROP TABLE RENTS")
    connection.commit()
    print("Table RENTS have been deleted successfully")

def create_user():
    cursor.execute("INSERT INTO USERS (id, username, password) VALUES (%s, %s, %s)", ("test_id", "test", "test"))
    connection.commit()

def create_table_tokens():
    cursor.execute('''CREATE TABLE TOKENS
        (token TEXT)''')
    connection.commit()
    print("Table TOKENS have created successfully")


# delete_table_transport()
# create_table_transport()

