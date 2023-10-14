import psycopg2

connection = psycopg2.connect(user="postgres", password="qazedcrfvs1A")
cursor = connection.cursor()


def create_table_balances():
    create_table_query = '''CREATE TABLE BALANCES (userid TEXT, balance real)'''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table 'Balance' have been created successfully")

def delete_table_balances():
    cursor.execute("DROP TABLE BALANCES")
    connection.commit()
    print("Table BALANCES have been deleted successfully")

def show_balances_table():
    cursor.execute("SELECT * FROM BALANCES")
    a = cursor.fetchall()
    print(a)

def create_table_users():
    create_table_query = '''CREATE TABLE USERS (id TEXT, username TEXT, password TEXT, privilege TEXT)'''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table 'Users' have been created successfully")

def delete_table_users():
    cursor.execute("DROP TABLE USERS")
    connection.commit()
    print("Table USERS have been deleted successfully")

def show_table_users():
    cursor.execute('''SELECT * FROM USERS''')
    a = cursor.fetchall()
    print(a)


def create_transport_table():
    create_table_query = '''CREATE TABLE TRANSPORT 
    (id TEXT, canberented BOOLEAN, transporttype TEXT, model TEXT,
    color TEXT, identifier TEXT, description TEXT, latitude TEXT,
    longitude TEXT, minuteprice TEXT, dayprice TEXT, ownerid TEXT)'''
    cursor.execute(create_table_query)
    connection.commit()
    print("Table 'Transport' have been created successfully")

def delete_transport_table():
    cursor.execute("DROP TABLE TRANSPORT")
    connection.commit()
    print("Table TRANSPORT have been deleted successfully")

def create_rents_table():
    cursor.execute('''CREATE TABLE RENTS
    (rentid TEXT, transportid TEXT, rentorid TEXT, renttype TEXT, cost real, start TEXT)''')
    connection.commit()
    print("Table RENTS have created successfully")

def delete_rents_table():
    cursor.execute("DROP TABLE RENTS")
    connection.commit()
    print("Table RENTS have been deleted successfully")

def show_rents_table():
    cursor.execute("SELECT * FROM RENTS")
    a = cursor.fetchall()
    print(a)

# create_rents_table()
def show_transport_table():
    cursor.execute("SELECT * FROM TRANSPORT")
    a = cursor.fetchall()
    print(a)


create_table_users()

# cursor.execute("SELECT * FROM TRANSPORT LIMIT 0")
# colnames = [desc[0] for desc in cursor.description]
# print(colnames)

# cursor.execute("UPDATE TRANSPORT SET longitude = 456.0")
# connection.commit()