import psycopg2
import datetime
from flask import request
from flask_jwt_extended import decode_token
import yaml

connection = psycopg2.connect(user="postgres", password="qazedcrfvs1A")
cursor = connection.cursor()


def authenticate(username, password):
    curr_json = request.get_json()
    curr_username = curr_json["username"]
    curr_password = curr_json["password"]
    cursor.execute("SELECT password, id FROM USERS WHERE username = %s", (curr_username,))
    user_password = cursor.fetchall()
    if not user_password:
        return "Not found", 404
    user_password = user_password[0]
    if user_password[0] == curr_password:
        cursor.execute("SELECT * FROM USERS WHERE username = %s", (curr_username,))
        curr_user_data = cursor.fetchall()
        if not curr_user_data:
            return "Not found", 404
        curr_user_data = curr_user_data[0]
        return curr_user_data
    return None


def get_token():
    return request.headers["Authorization"][7:]

def check_token(token):
    cursor.execute('''SELECT status FROM TOKENS WHERE token = %s''', (token, ))
    status = cursor.fetchall()
    if not status:
        return False
    status = status[0]
    return status[0]

def get_id_from_token():
    return decode_token(request.headers["Authorization"][7:])['sub']

def get_all_user_data_by_id(user_id):
    cursor.execute("SELECT * FROM USERS WHERE id = %s", (user_id, ))
    data = cursor.fetchall()
    if not data:
        return "Users not found", 404
    data = data[0]
    cursor.execute('''SELECT balance FROM BALANCES WHERE userid = %s''', (user_id, ))
    balance_data = cursor.fetchall()
    if not balance_data:
        return "Balances not found", 404
    balance_data = balance_data[0]
    return make_dict_from_userdata_list(data, balance_data)

def make_dict_from_userdata_list(userdata_list, balance):
    d = dict()
    d["id"] = userdata_list[0]
    d["username"] = userdata_list[1]
    d["password"] = userdata_list[2]
    d["privilege"] = userdata_list[3]
    d["balance"] = balance[0]
    return d


def make_dict_from_rentdata_list(rentdata_list):
    d = dict()
    d["rentId"] = rentdata_list[0],
    d["tranportId"] = rentdata_list[1],
    d["rentorId"] = rentdata_list[2],
    d["timeStart"] = rentdata_list[3],
    d["timeEnd"] = rentdata_list[4],
    d["priceOfUnit"] = rentdata_list[5],
    d["priceType"] = rentdata_list[6],
    d["finalPrice"] = rentdata_list[7]
    return d


def get_set_of_user_id():
    cursor.execute('''SELECT id FROM USERS''')
    a = cursor.fetchall()
    return a


def make_dict_from_transportdata_list(transportdata_list):
    d = dict()
    d["id"] = transportdata_list[0],
    d["canBeRented"] = transportdata_list[1],
    d["transportType"] = transportdata_list[2],
    d["model"] = transportdata_list[3],
    d["color"] = transportdata_list[4],
    d["identifier"] = transportdata_list[5],
    d["description"] = transportdata_list[6],
    d["latitude"] = transportdata_list[7],
    d["longitude"] = transportdata_list[8],
    d["minutePrice"] = transportdata_list[9],
    d["dayPrice"] = transportdata_list[10],
    d["ownerID"] = transportdata_list[11]
    return d

def make_list_from_transportdata_dict(data):
    curr_transport_data = []
    curr_transport_data.append(data["id"])
    curr_transport_data.append(data["canBeRented"])
    curr_transport_data.append(data["transportType"])
    curr_transport_data.append(data["model"])
    curr_transport_data.append(data["color"])
    curr_transport_data.append(data["identifier"])
    curr_transport_data.append(data["description"])
    curr_transport_data.append(float(data["latitude"]))
    curr_transport_data.append(float(data["longitude"]))
    curr_transport_data.append(float(data["minutePrice"]))
    curr_transport_data.append(float(data["dayPrice"]))
    curr_transport_data.append(data["ownerID"])
    print(curr_transport_data)
    return curr_transport_data

def get_set_of_usernames():
    cursor.execute("SELECT USERNAME FROM USERS")
    usernames = set([name[0] for name in cursor.fetchall()])
    return usernames


def check_availability(x, y, x_circle, y_circle, radius):
    if (x - x_circle) ** 2 + (y - y_circle) ** 2 <= radius ** 2:
        return True
    return False


def is_admin(userid):
    cursor.execute("SELECT privilege FROM USERS WHERE id = %s", (userid,))
    curr_user_data = cursor.fetchall()
    if not curr_user_data:
        return "User not found", 404
    curr_user_data = curr_user_data[0]
    if curr_user_data[0] == "admin":
        return True
    return False


def add_250000_to_balance(user_id):
    cursor.execute('''SELECT * FROM BALANCES WHERE userid = %s''', (user_id,))
    curr_balance_data = cursor.fetchall()
    if not curr_balance_data:
        return "Balance not found", 404
    curr_balance_data = curr_balance_data[0]
    cursor.execute('''UPDATE BALANCES SET balance = %s WHERE userid = %s''',
                   (curr_balance_data[1] + 250000, user_id))
    connection.commit()


def get_balance_by_id(user_id):
    cursor.execute('''SELECT balance FROM BALANCES WHERE userid = %s''', (user_id,))
    curr_data = cursor.fetchall()
    if not curr_data:
        return "Balance not found", 404
    curr_data = curr_data[0]
    return curr_data[1]


def get_rent_price_by_id(transport_id, rent_type):
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (transport_id,))
    curr_data = cursor.fetchall()
    if not curr_data:
        return "Transport not found", 404
    curr_data = curr_data[0]
    if rent_type == "Minutes":
        print(curr_data)
        return curr_data[9]
    elif rent_type == "Days":
        return curr_data[10]
    else:
        return False


def cancel_money_for_rent(user_id, total):
    cursor.execute('''SELECT balance FROM BALANCES WHERE userid = %s''', (user_id,))
    curr_balance = cursor.fetchall()
    if not curr_balance:
        return "Balance not found", 404
    curr_balance = curr_balance[0]
    curr_balance = curr_balance[0]
    curr_balance -= total
    cursor.execute('''UPDATE BALANCES SET balance = %s WHERE userid = %s''', (curr_balance, user_id))


def get_minutes_from_str(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")


def get_days_from_str(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d").day


def get_onwerid_by_transport_id(transport_id):
    cursor.execute("SELECT ownerID FROM TRANSPORT WHERE ID = %s", (transport_id,))
    owner_id = cursor.fetchall()
    if not owner_id:
        return "Transport not found", 404
    owner_id = owner_id[0]
    owner_id = owner_id[0]
    return owner_id