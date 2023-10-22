import psycopg2.errors


from main import app


connection = psycopg2.connect(user="ENTER YOU USERNAME HERE", password="ENTER YOU PASSWORD HERE")
cursor = connection.cursor()


def create_table_balances():
    cursor.execute("""CREATE TABLE BALANCES (userid TEXT, balance real)""")
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
    create_table_query = (
        """CREATE TABLE USERS (id TEXT, username TEXT, password TEXT, privilege TEXT)"""
    )
    cursor.execute(create_table_query)
    connection.commit()
    print("Table USERS have been created successfully")


def show_table_users():
    cursor.execute("""SELECT * FROM USERS""")
    a = cursor.fetchall()
    print(a)


def delete_table_users():
    cursor.execute("DROP TABLE USERS")
    connection.commit()
    print("Table USERS have been deleted successfully")


def create_table_transport():
    cursor.execute("""CREATE TABLE TRANSPORT 
    (id TEXT, canberented BOOLEAN, transporttype TEXT, model TEXT,
    color TEXT, identifier TEXT, description TEXT, latitude TEXT,
    longitude TEXT, minuteprice TEXT, dayprice TEXT, ownerid TEXT)""")
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
    cursor.execute(
        """CREATE TABLE RENTS
    (rentid TEXT, transportid TEXT, rentorid TEXT, start TEXT, ending TEXT, unitprice real,
     renttype TEXT, finalprice real)"""
    )
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
    cursor.execute(
        "INSERT INTO USERS (id, username, password) VALUES (%s, %s, %s)",
        ("test_id", "test", "test"),
    )
    connection.commit()


def create_table_tokens():
    cursor.execute(
        """CREATE TABLE TOKENS
        (token TEXT, status BOOLEAN)"""
    )
    connection.commit()
    print("Table TOKENS have created successfully")

def show_table_tokens():
    cursor.execute("SELECT * FROM TOKENS")
    a = cursor.fetchall()
    print(a)

def delete_table_tokens():
    cursor.execute("DROP TABLE TOKENS")
    connection.commit()
    print("Table TOKENS have been deleted successfully")


def create_admin():
    cursor.execute('''INSERT INTO USERS (id, username, password, privilege) VALUES (%s, %s, %s, %s)''',
                   ("0", "admin", "1234", "admin"))
    connection.commit()


def show_column_names():
    cursor.execute("SELECT * FROM TRANSPORT LIMIT 0")
    colnames = [desc[0] for desc in cursor.description]
    print(colnames)

delete_table_tokens()

try:
    create_table_users()
except psycopg2.errors.DuplicateTable:
    connection.commit()


try:
    create_table_balances()
except psycopg2.errors.DuplicateTable:
    connection.commit()

try:
    create_table_rents()
except psycopg2.errors.DuplicateTable:
    connection.commit()


try:
    create_table_transport()
except psycopg2.errors.DuplicateTable:
    connection.commit()


try:
    create_table_tokens()
except psycopg2.errors.DuplicateTable:
    connection.commit()

if __name__ == "__main__":
    app.run(port=5000)
