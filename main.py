from flask import Flask, request, Response
import json
import uuid
import psycopg2
from http import HTTPStatus
from datetime import time, datetime

app = Flask(__name__)

authorize_data = {
    "user_id": "admin2",
    "privilege": "admin"
}
transport_columns_names = ["ID", "canberented", "transporttype", "model", "color", "identifier", "description",
                           "latitude", "longitude", "minuteprice", "dayprice", "ownerID"]

connection = psycopg2.connect(user="postgres", password="qazedcrfvs1A")
cursor = connection.cursor()


def get_set_of_usernames():
    cursor.execute("SELECT USERNAME FROM USERS")
    usernames = set([name[0] for name in cursor.fetchall()])
    return usernames

def is_admin(userid):
    cursor.execute("SELECT privileges FROM USERS WHERE id = %s", (userid, ))
    curr_user_data = cursor.fetchall()
    if curr_user_data[0][0] == "admin":
        return True
    return False
def add_250000_to_balance(user_id):
    cursor.execute('''SELECT * FROM BALANCES WHERE userid = %s''', (user_id,))
    curr_balance_data = cursor.fetchall()
    cursor.execute('''UPDATE BALANCES SET balance = %s WHERE userid = %s''',
                   (curr_balance_data[0][1] + 250000), user_id)
    connection.commit()

def get_balance_by_id(user_id):
    cursor.execute('''SELECT balance FROM BALANCES WHERE userid = %s''', (user_id, ))
    curr_data = cursor.fetchall()
    return curr_data[0][1]

def get_rent_price_by_id(transport_id, rent_type):
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (transport_id, ))
    curr_data = cursor.fetchall()
    if rent_type == "Minutes":
        print(curr_data)
        return curr_data[0][9]
    elif rent_type == "Days":
        return curr_data[0][10]
    else:
        return False

def cancel_money_for_rent(user_id, total):
    cursor.execute('''SELECT balance FROM BALANCES WHERE userid = %s''', (user_id, ))
    curr_balace = cursor.fetchall()
    curr_balace = curr_balace[0][0]
    curr_balace -= total
    cursor.execute('''UPDATE BALANCES SET balance = %s WHERE userid = %s''', (curr_balace, user_id))

def get_minutes_from_str(string):
    return datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


def get_days_from_str(string):
    return datetime.strptime(string, "%Y-%m-%d").day


def get_onwerid_by_transport_id(transport_id):
    cursor.execute("SELECT ownerID FROM TRANSPORT WHERE ID = %s", (transport_id,))
    owner_id = cursor.fetchall()
    owner_id = owner_id[0][0]
    return owner_id


@app.get("/api/Account/Me")
def index_account_me(data=authorize_data):
    if data["user_id"]:
        return {
            "user id": data["user_id"],
            "privilege": data["privilege"],
            "balance": get_balance_by_id(data["user_id"])
        }

@app.get("/api/Admin/Account")
def admin_get_all_accounts(data=authorize_data):
    if is_admin(data["user_id"]):
        cursor.execute('''SELECT * FROM USERS''')
        return cursor.fetchall()
    else:
        return "Access denied", 403

@app.get("/api/Admin/Account/<user_id>")
def admin_get_account_data(user_id, data=authorize_data):
    if not is_admin(data["user_id"]):
        return "Access denied", 403
    cursor.execute('''SELECT * FROM USERS WHERE userid = %s''', (user_id, ))
    return cursor.fetchall()

@app.post("/api/Admin/Account")
def admin_create_account(data=authorize_data):
    if not is_admin(data["privilege"]):
        return "Access denied", 403
    curr_json = request.get_json()
    username = curr_json["username"]
    if username in get_set_of_usernames():
        return "This username is already used", 409
    user_id = uuid.uuid4()
    password = curr_json["password"]
    isadmin = "admin" if curr_json["isAdmin"] else "user"
    balance = curr_json["balance"]
    cursor.execute("INSERT INTO USERS (id, username, password, privilege) VALUES (%s, %s, %s, %s)",
                   (user_id, username, password, isadmin))
    cursor.execute("INSERT INTO BALANCES (userid, balance) VALUES (%s, %s)", (user_id, balance))
    connection.commit()

@app.put("/api/Admin/Account/<user_id>")
def admin_change_account(user_id, data=authorize_data):
    if not is_admin(data["user_id"]):
        return "Access denied", 403
    cursor.execute('''UPDATE USERS ''')
    cursor.execute('''UPDATE BALANCES''')


@app.post("/api/Account/SignIn")
def index_sign_in():
    curr_json = request.get_json()
    curr_username = curr_json["username"]
    curr_password = curr_json["password"]
    cursor.execute("SELECT password, id FROM USERS WHERE username = %s", (curr_username,))
    row = cursor.fetchall()
    if row[0][0] == curr_password:
        cursor.execute("SELECT id FROM USERS WHERE username = %s", (curr_username,))
        user_id = row[0][1]
        user_privilege = row[0][3]
        authorize_data["user_id"] = user_id
        authorize_data["privilege"] = user_privilege
        return 200
    return "Incorrect username/password", 409


@app.post("/api/Account/SignUp")
def index_sign_up():
    curr_json = request.get_json()
    curr_username = curr_json["username"]
    curr_password = curr_json["password"]
    curr_id = str(uuid.uuid4())
    cursor.execute("SELECT USERNAME FROM USERS")
    usernames = get_set_of_usernames()
    if curr_username not in usernames:
        cursor.execute("INSERT INTO USERS (id, username, password, privilege) VALUES (%s, %s, %s, %s)",
                       (curr_id, curr_username, curr_password, "user"))
        cursor.execute("INSERT INTO BALANCES (userid, balance) VALUES (%s, %s)",
                       (curr_id, 0))
        connection.commit()
        return 200
    return f"Username {curr_username} is already used", 409


@app.post("/api/Account/SignOut")
def index_sign_out(data=authorize_data):
    data["user_id"] = False
    data["privilege"] = False
    return 200


@app.put("/api/Account/Update")
def index_update_account(data=authorize_data):
    if data["user_id"]:
        curr_json = request.get_json()
        new_username = curr_json["username"]
        new_password = curr_json["password"]
        usernames = get_set_of_usernames()
        if new_username not in usernames:
            cursor.execute("UPDATE USERS SET username = %s WHERE id = %s", (new_username, data["user_id"]))
            cursor.execute("UPDATE USERS SET password = %s WHERE id = %s", (new_password, data["user_id"]))
            return "", 200
        return


@app.get("/api/Transport/<transport_id>")
def index_get_transport_data_by_id(transport_id):
    global transport_columns_names
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (str(transport_id),))
    curr_transport_data = cursor.fetchall()
    print(curr_transport_data)
    if len(curr_transport_data) != 0:
        output = dict()
        for i in range(1, 12):
            output[transport_columns_names[i]] = curr_transport_data[0][i]
        print(output)
        return output
    return "There is no this transport's in database", 404


@app.post("/api/Transport")
def index_add_transport(data=authorize_data):
    global transport_columns_names
    # if data["user_id"]:
    curr_json = request.get_json()
    curr_car_parameters = [str(uuid.uuid4()), curr_json["canberented"]]
    for parameter in transport_columns_names[2:11]:
        curr_car_parameters.append(curr_json[str(parameter)])
    curr_car_parameters.append(str(data["user_id"]))
    print(curr_car_parameters)
    cursor.execute('''INSERT INTO TRANSPORT ("id", "canberented", "transporttype", "model", "color", "identifier", 
    "description", "latitude", "longitude", "minuteprice", "dayprice", "ownerid")
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', tuple(curr_car_parameters))
    connection.commit()
    return curr_car_parameters


@app.put("/api/Transport/<transport_id>")
def index_update_transport(transport_id, data=authorize_data):
    global transport_columns_names
    owner_id = get_onwerid_by_transport_id(transport_id)
    if str(owner_id) == str(data["user_id"]):
        curr_json = request.get_json()
        curr_car_parameters = [str(transport_id)]
        for parameter in transport_columns_names[1:11]:
            curr_car_parameters.append(curr_json[str(parameter)])
        curr_car_parameters.append(str(data["user_id"]))
        print(curr_car_parameters[1:10])
        cursor.execute('''UPDATE TRANSPORT SET "canberented" = %s, "transporttype" = %s, "model" = %s, "color" = %s, 
        "identifier" = %s, "description" = %s, "latitude" = %s, "minuteprice" = %s, "dayprice" = %s''',
                       tuple(curr_car_parameters[1:10]))
        connection.commit()
        return "", 200
    return "", 403


@app.delete("/api/Transport/<transport_id>")
def index_delete_transport(transport_id, data=authorize_data):
    owner_id = get_onwerid_by_transport_id(transport_id)
    if str(owner_id) == str(data["user_id"]):
        cursor.execute("DELETE FROM TRANSPORT WHERE id = %s", (transport_id,))
        return "Deleted successfully", 200
    return "Access denied", 403


@app.get("/api/Rent/Transport")
def index_get_available_transport():
    curr_json = request.get_json()
    transport_type = curr_json["type"]
    x_circle = float(curr_json["lat"])
    y_circle = float(curr_json["long"])
    radius = float(curr_json["radius"])

    def check_availability(x, y, x_circle=x_circle, y_circle=y_circle, radius=radius):
        if (x - x_circle) ** 2 + (y - y_circle) ** 2 <= radius ** 2:
            return True
        return False

    cursor.execute("SELECT * FROM TRANSPORT")
    all_transport = cursor.fetchall()
    available_transport = [x[0] for x in all_transport if
                           check_availability(int(x[7]), int(x[8])) and x[2] == transport_type]
    return available_transport


# @app.get("/api/Rent/<rentid>")
# def index_get_rent_data_by_id(rentid):
#     # TODO Обращение к бд и вывод данных по аренде

@app.get("/api/Rent/MyHistory")
def index_get_my_rent_history(data=authorize_data):
    # if data["user_id"]:
    user_id = authorize_data["user_id"]
    cursor.execute("SELECT * FROM RENTS WHERE rentorid = %s", (user_id,))
    rents = cursor.fetchall()
    return rents, 200


@app.get("/api/Rent/TransportHistory/<transport_id>")
def index_get_transport_history_by_id(transport_id, data=authorize_data):
    user_id = data["user_id"]
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (transport_id,))
    curr_transport_data = cursor.fetchall()
    if curr_transport_data[11] == user_id:
        cursor.execute("SELECT * FROM RENTS WHERE transportid = %s", (transport_id,))
        rents_history = cursor.fetchall()
        return rents_history
    else:
        return "Access denied", 403


@app.post("/api/Rent/New/<transport_id>")
def index_rent_transport(transport_id, data=authorize_data):
    user_id = data["user_id"]
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (transport_id,))
    curr_transport_data = cursor.fetchall()
    if not curr_transport_data:
        return "This transport not found", 404
    if not curr_transport_data[0][1]:
        return "This transport can't be rented", 403
    elif curr_transport_data[0][11] != user_id and user_id:
        curr_json = request.get_json()
        rent_type = curr_json["renttype"]
        rent_id = str(uuid.uuid4())
        print(rent_type)
        if rent_type == "Minutes":
            start = str(datetime.today().now())
        elif rent_type == "Days":
            start = str(datetime.today().date())
        else:
            return "Wrong Rent Type", 400
        curr_rent_parameters = [rent_id, transport_id, user_id, rent_type, 0, start]
        cursor.execute('''INSERT INTO RENTS ("rentid", "transportid", "rentorid", "renttype", "cost", "start")
            VALUES (%s, %s, %s, %s, %s, %s)''', tuple(curr_rent_parameters))
        cursor.execute('''UPDATE TRANSPORT SET canberented = %s WHERE id = %s''', (False, curr_transport_data[0][0]))
        connection.commit()
        return "", 200
    else:
        return "You can't rent your own transport", 403


@app.post("/api/Rent/End/<rent_id>")
def index_end_rent_by_id(rent_id, data=authorize_data):
    user_id = data["user_id"]
    cursor.execute("SELECT * FROM RENTS WHERE rentid = %s", (rent_id, ))
    curr_rent_data = cursor.fetchall()
    if curr_rent_data[0][2] == user_id:
        price = get_rent_price_by_id(curr_rent_data[0][1], curr_rent_data[0][3])
        if curr_rent_data[0][3] == "Minutes":
            price = price * (datetime.now() - get_minutes_from_str(curr_rent_data[0][5]))
            cursor.execute('''UPDATE RENTS SET cost = %s WHERE rentid = %s''', (price, curr_rent_data[0][0]))
        if curr_rent_data[0][3] == "Days":
            price = price * (datetime.now().day - get_days_from_str(curr_rent_data[0][5]))
            cursor.execute('''UPDATE RENTS SET cost = %s WHERE rentid = %s''', (price, curr_rent_data[0][0]))
        cancel_money_for_rent(user_id, price)
        curr_json = request.get_json()
        latitude, longitude = curr_json["lat"], curr_json["long"]
        cursor.execute('''UPDATE TRANSPORT SET latitude = %s, longitude = %s WHERE transportid = %s''',
                       (latitude, longitude, curr_rent_data[0][1]))
        connection.commit()
        return f"Rent was ended successful, price: {price}", 200
    else:
        return "Access denied", 403

@app.post("/api/Payment/Hesoyam/<accountid>")
def index_add_250000(accountid, data=authorize_data):
    if data["user_id"] == "admin":
        add_250000_to_balance(accountid)
        return "Done", 200
    else:
        if accountid == data["user_id"]:
            add_250000_to_balance(accountid)
            return "Done", 200
        else:
            return "Access denied", 403





if __name__ == "__main__":
    app.run(port=5000, debug=True)
