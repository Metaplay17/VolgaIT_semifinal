from flask import Flask, request, Response
import json
import uuid
import psycopg2
from http import HTTPStatus
from datetime import time, datetime

app = Flask(__name__)

authorize_data = {
    "user_id": False
}
transport_columns_names = ["ID", "canBeRented", "transportType", "model", "color", "identifier", "description", "latitude",
                           "longitude", "minutePrice", "dayPrice", "ownerID"]

connection = psycopg2.connect(user="postgres", password="qazedcrfvs1A")
cursor = connection.cursor()

def get_set_of_usernames():
    cursor.execute("SElECT USERNAME FROM USERS")
    usernames = set([name[0] for name in cursor.fetchall()])
    return usernames

def get_onwerid_by_transport_id(transport_id):
    cursor.execute("SELECT ownerID FROM TRANSPORT WHERE ID = %s", (transport_id,))
    owner_id = cursor.fetchall()
    owner_id = owner_id[0][0]
    return owner_id

@app.get("/api/Account/Me")
# def index_account_me():
    # TODO


@app.post("/api/Account/SignIn")
def index_sign_in():
    curr_json = request.get_json()
    curr_username = curr_json["username"]
    curr_password = curr_json["password"]
    cursor.execute("SELECT PASSWORD, ID FROM USERS WHERE USERNAME = %s", (curr_username, ))
    row = cursor.fetchall()
    if row[0][0] == curr_password:
        cursor.execute("SELECT ID FROM USERS WHERE USERNAME = %s", (curr_username, ))
        user_id = row[0][1]
        authorize_data["user_id"] = user_id
        return 200
    return "Incorrect username/password", 409


@app.post("/api/Account/SignUp")
def index_sign_up():
    curr_json = request.get_json()
    curr_username = curr_json["username"]
    curr_password = curr_json["password"]
    curr_id = str(uuid.uuid4())
    cursor.execute("SElECT USERNAME FROM USERS")
    usernames = get_set_of_usernames()
    if curr_username not in usernames:
        cursor.execute("INSERT INTO USERS (ID, USERNAME, PASSWORD) VALUES (%s, %s, %s)", (curr_id, curr_username, curr_password))
        connection.commit()
        return 200
    return f"Username {curr_username} is already used", 409


@app.post("/api/Account/SignOut")
def index_sign_out(data=authorize_data):
    data["user_id"] = False
    return 200


@app.put("/api/Account/Update")
def index_update_account(data=authorize_data):
    if data["user_id"]:
        curr_json = request.get_json()
        new_username = curr_json["username"]
        new_password = curr_json["password"]
        usernames = get_set_of_usernames()
        if new_username not in usernames:
            cursor.execute("UPDATE USERS SET USERNAME = %s WHERE ID = %s", (new_username, data["user_id"]))
            cursor.execute("UPDATE USERS SET PASSWORD = %s WHERE ID = %s", (new_password, data["user_id"]))
            return Response(HTTPStatus.OK)
        return

@app.get("/api/Transport/<transport_id>")
def index_get_transport_data_by_id(transport_id):
    global transport_columns_names
    cursor.execute("SELECT * FROM TRANSPORT WHERE ID = %s", (str(transport_id), ))
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
    curr_car_parameters = [str(uuid.uuid4())]
    for parameter in transport_columns_names[1:11]:
        curr_car_parameters.append(curr_json[str(parameter)])
    curr_car_parameters.append(str(data["user_id"]))
    cursor.execute('''INSERT INTO TRANSPORT ("id", "canberented", "transporttype", "model", "color", "identifier", "description", "latitude", "minuteprice", "dayprice", "ownerid") 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', tuple(curr_car_parameters))
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
        cursor.execute("DELETE FROM TRANSPORT WHERE ID = %s", (transport_id, ))
        return "Deleted successfully", 200
    return "Access denied", 403


@app.get("/api/Rent/Transport")
def index_get_available_transport():
    curr_json = request.get_json()
    transport_type = curr_json["type"]
    x_circle = curr_json["lat"]
    y_circle = curr_json["long"]
    radius = curr_json["radius"]
    def check_availability(x, y, x_circle=x_circle, y_circle=y_circle, radius=radius):
        if (x - x_circle)**2 + (y - y_circle)**2 <= radius**2:
            return True
        return False
    cursor.execute("SELECT * FROM TRANSPORT")
    all_transport = cursor.fetchall()
    available_transport = [x[0] for x in all_transport if check_availability(int(x[7]), int(x[8])) and x[2] == transport_type]
    return available_transport

@app.get("/api/Rent/<rentid>")
def index_get_rent_data_by_id(rentid):
    # TODO Обращение к бд и вывод данных по аренде

@app.get("api/Rent/MyHistory")
def index_get_my_rent_history(data=authorize_data):
    # if data["user_id"]:
    user_id = authorize_data["user_id"]
    cursor.execute("SELECT * FROM RENTS WHERE rentorid = %s", (user_id, ))
    rents = cursor.fetchall()
    return rents, 200

@app.get("api/Rent/TransportHistory/<transport_id>")
def index_get_transport_history_by_id(transport_id, data=authorize_data):
    user_id = data["user_id"]
    cursor.execute("SELECT * FROM TRANSPORT WHERE ID = %s", (transport_id, ))
    curr_transport_data = cursor.fetchall()
    if curr_transport_data[11] == user_id:
        cursor.execute("SELECT * FROM RENTS WHERE transportid = %s", (transport_id, ))
        rents_history = cursor.fetchall()
        return rents_history
    else:
        return "Access denied", 403

@app.post("api/Rent/New/<transport_id>")
def index_rent_transport(transport_id, data=authorize_data):
    user_id = data["user_id"]
    cursor.execute("SELECT * FROM TRANSPORT WHERE ID = %s", (transport_id,))
    curr_transport_data = cursor.fetchall()
    if curr_transport_data[11] != user_id and user_id:
        curr_json = request.get_json()
        rent_type = curr_json["rentType"]
        rent_id = str(uuid.uuid4())
        curr_rent_parameters = [rent_id, transport_id, user_id, rent_type, 0, 0]
        cursor.execute('''INSERT INTO RENTS ("ID", "rentid", "transportid", "rentorid", "renttype", "cost", "during") 
            VALUES (%s, %s, %s, %s, %s, %s, %s)''', tuple(curr_rent_parameters))
        connection.commit()
    else:
        return "You can't rent your own transport", 403

@app.post("api/Rent/End/<rent_id>")
def index_end_rent_by_id(rent_id, data=authorize_data):
    user_id = data["user_id"]
    cursor.execute("SELECT * FROM RENTS WHERE ID = %s", (rent_id, ))
    curr_rent_data = cursor.fetchall()
    if curr_rent_data[2] == user_id:
        # TODO DATE TIME
        cursor.execute
    else:
        return "Access denied", 403




if __name__ == "__main__":
    app.run(port=5000, debug=True)

