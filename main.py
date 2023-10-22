from flask import Flask
from flask_cors import CORS, cross_origin
import uuid
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from flasgger import Swagger


from ServerFunctions import *


app = Flask(__name__)
app.static_folder = 'spec'
cors = CORS(app)
app.config["SWAGGER"] = {
    'title': 'Simbir.GO API',
    'uiversion': 3,
    'openapi': '3.0.0',
    'specs_route': '/apidocs/',
    'specs': [
        {
            'endpoint': 'spec',
            'route': '/spec/spec.yaml'
        }
    ]
}
app.config["SECRET_KEY"] = "secret-key"
app.config["CORS_HEADERS"] = "Content-Type"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=60)
jwt = JWTManager(app)

with open('spec/spec.yaml', 'r') as spec_file:
    openapi_spec = yaml.safe_load(spec_file)
Swagger(app, template=openapi_spec)

transport_columns_names = [
    "id",
    "canBeRented",
    "transportType",
    "model",
    "color",
    "identifier",
    "description",
    "latitude",
    "longitude",
    "minutePrice",
    "dayPrice",
    "ownerID",
]

user_parameters = ["id", "username", "password", "privilege"]


def authenticate(curr_json):
    try:
        curr_username = curr_json["username"]
        curr_password = curr_json["password"]
        cursor.execute(
            "SELECT password, id FROM USERS WHERE username = %s", (curr_username,)
        )
        user_password = cursor.fetchall()
        user_password = user_password[0]
    except IndexError:
        return None
    else:
        if user_password[0] == curr_password:
            cursor.execute("SELECT * FROM USERS WHERE username = %s", (curr_username,))
            curr_user_data = cursor.fetchall()
            curr_user_data = curr_user_data[0]
            return curr_user_data
        return None


@app.get("/api/Account/Me")
@jwt_required()
@cross_origin()
def index_account_me():
    if check_token(get_token()):
        curr_id = get_id_from_token()
        return get_all_user_data_by_id(curr_id)
    return "", 401


@app.get("/api/Admin/Account")
@jwt_required()
@cross_origin()
def admin_get_all_accounts():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if is_admin(curr_id):
        headers = request.headers
        start = int(headers["start"])
        end = start + int(headers["count"])
        cursor.execute("""SELECT id FROM USERS""")
        identifiers = cursor.fetchall()
        identifiers = identifiers[start:end + 1]
        output = []
        for identity in identifiers:
            cursor.execute('''SELECT * FROM USERS WHERE id = %s''', (identity, ))
            base_data = cursor.fetchall()
            base_data = base_data[0]
            cursor.execute('''SELECT balance FROM BALANCES WHERE userid = %s''', (identity, ))
            balance = cursor.fetchall()
            if balance:
                balance = balance[0]
            else:
                balance = ("Not found", )
            output.append(make_dict_from_userdata_list(base_data, balance))
        return output, 200
    else:
        return "Access denied", 403


@app.get("/api/Admin/Account/<user_id>")
@jwt_required()
@cross_origin()
def admin_get_account_data(user_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute("""SELECT * FROM USERS WHERE id = %s""", (user_id,))
    output = cursor.fetchall()
    if not output:
        return "Account not found", 404
    output = output[0]
    cursor.execute("""SELECT balance FROM BALANCES WHERE userid = %s""", (user_id, ))
    balance_data = cursor.fetchall()
    if not balance_data:
        return "Balance not found", 404
    balance_data = balance_data[0]
    return make_dict_from_userdata_list(output, balance_data)


@app.post("/api/Account/SignIn")
@cross_origin()
def index_sign_in():
    curr_json = request.get_json()
    data = authenticate(curr_json)
    print(data)
    if data:
        curr_token = create_access_token(identity=data[0])
        cursor.execute('''INSERT INTO TOKENS (token, status) VALUES (%s, %s)''', (str(curr_token), True))
        connection.commit()
        return {"token": curr_token}, 200
    return "This user/password combination Not Found", 404


@app.post("/api/Account/SignUp")
@cross_origin()
def index_sign_up():
    curr_json = request.get_json()
    curr_username = curr_json["username"]
    curr_password = curr_json["password"]
    curr_id = str(uuid.uuid4())
    usernames = get_set_of_usernames()
    if curr_username not in usernames:
        output = {
            "id": curr_id,
            "username": curr_username,
            "password": curr_password,
            "privilege": "user",
        }
        cursor.execute(
            "INSERT INTO USERS (id, username, password, privilege) VALUES (%s, %s, %s, %s)",
            (curr_id, curr_username, curr_password, "user"),
        )
        cursor.execute(
            "INSERT INTO BALANCES (userid, balance) VALUES (%s, %s)", (curr_id, 0)
        )
        connection.commit()
        return output, 200
    return f"Username {curr_username} is already used", 409


@app.post("/api/Admin/Account")
@jwt_required()
@cross_origin()
def admin_create_account():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    curr_json = request.get_json()
    username = curr_json["username"]
    if username in get_set_of_usernames():
        return "This username is already used", 409
    user_id = str(uuid.uuid4())
    password = curr_json["password"]
    isadmin = "admin" if curr_json["isAdmin"] else "user"
    balance = curr_json["balance"]
    cursor.execute(
        "INSERT INTO USERS (id, username, password, privilege) VALUES (%s, %s, %s, %s)",
        (user_id, username, password, isadmin),
    )
    cursor.execute(
        "INSERT INTO BALANCES (userid, balance) VALUES (%s, %s)", (user_id, balance)
    )
    connection.commit()
    return "Account was created", 200


@app.post("/api/Account/SignOut")
@jwt_required()
def index_sign_out():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    cursor.execute('''UPDATE TOKENS SET status = %s WHERE token = %s''', (False, get_token()))
    connection.commit()
    return "", 200


@app.put("/api/Account/Update")
@jwt_required()
@cross_origin()
def index_update_account():
    if check_token(get_token()):
        curr_id = get_id_from_token()
        curr_json = request.get_json()
        new_username = curr_json["username"]
        new_password = curr_json["password"]
        usernames = get_set_of_usernames()
        if new_username not in usernames:
            cursor.execute(
                "UPDATE USERS SET username = %s WHERE id = %s", (new_username, curr_id)
            )
            cursor.execute(
                "UPDATE USERS SET password = %s WHERE id = %s", (new_password, curr_id)
            )
            return "", 200
        return "Username is already used", 409
    return "NOT VALID TOKEN", 401


@app.put("/api/Admin/Account/<user_id>")
@jwt_required()
def admin_change_account(user_id):
    if check_token(get_token()):
        curr_id = get_id_from_token()
        if not is_admin(curr_id):
            return "Access denied", 403
        cursor.execute('''SELECT 8 FROM USERS WHERE id = %s''', (user_id, ))
        a = cursor.fetchall()
        if not a:
            return "User not found", 404
        curr_json = request.get_json()
        new_username = curr_json["username"]
        if new_username in get_set_of_usernames():
            return "Username is already used", 409
        new_password = curr_json["password"]
        new_privilege = "admin" if curr_json["isAdmin"] else "user"
        new_balance = curr_json["balance"]
        cursor.execute(
            """UPDATE USERS SET username = %s, password = %s, privilege = %s WHERE id = %s""",
            (new_username, new_password, new_privilege, user_id),
        )
        cursor.execute(
            """UPDATE BALANCES SET balance = %s WHERE userid = %s""", (new_balance, user_id)
        )
        connection.commit()
        return "Account was changed", 200
    return "Access denied", 401


@app.delete("/api/Admin/Account/<user_id>")
@jwt_required()
def admin_delete_account(user_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute("DELETE FROM USERS WHERE id = %s", (user_id,))
    cursor.execute("DELETE FROM BALANCES WHERE userid = %s", (user_id,))
    connection.commit()
    return "Done", 200



@app.get("/api/Transport/<transport_id>")
@cross_origin()
def index_get_transport_data_by_id(transport_id):
    global transport_columns_names
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (str(transport_id),))
    curr_transport_data = cursor.fetchall()
    if not curr_transport_data:
        return "Transport not found", 404
    curr_transport_data = curr_transport_data[0]
    if len(curr_transport_data) != 0:
        output = dict()
        for i in range(12):
            output[transport_columns_names[i]] = curr_transport_data[i]
        return output, 200
    return "There is no this transport in database", 404


@app.get("/api/Admin/Transport")
@jwt_required()
def admin_get_transport_list():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    headers = request.headers
    start = int(headers["start"])
    end = start + int(headers["count"])
    transport_type = headers["transportType"]
    if transport_type == "All":
        cursor.execute("""SELECT * FROM TRANSPORT""")
        all_transport = cursor.fetchall()
        if not all_transport:
            return "Transport not found", 404
        all_transport = all_transport[start : end + 1]
        return [make_dict_from_transportdata_list(transport) for transport in all_transport]
    cursor.execute(
        """SELECT * FROM TRANSPORT WHERE transporttype = %s""", (transport_type,)
    )
    all_transport = cursor.fetchall()
    if not all_transport:
        return "Transport not found", 404
    all_transport = all_transport[0]
    all_transport = all_transport[start : end + 1]
    return [make_dict_from_transportdata_list(transport) for transport in all_transport]


@app.get("/api/Admin/Transport/<transport_id>")
@jwt_required()
def admin_get_transport_data_by_id(transport_id):
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (transport_id,))
    curr_transport_data = cursor.fetchall()
    if not curr_transport_data:
        return "Transport not found", 404
    curr_transport_data = curr_transport_data[0]
    return make_dict_from_transportdata_list(curr_transport_data)


@app.post("/api/Transport")
@jwt_required()
@cross_origin()
def index_add_transport():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    global transport_columns_names
    curr_json = request.get_json()
    curr_car_parameters = [str(uuid.uuid4()), curr_json["canBeRented"]]
    for parameter in transport_columns_names[2:11]:
        curr_car_parameters.append(curr_json[str(parameter)])
    curr_car_parameters.append(str(curr_id))
    cursor.execute(
        """INSERT INTO TRANSPORT ("id", "canberented", "transporttype", "model", "color", "identifier",
    "description", "latitude", "longitude", "minuteprice", "dayprice", "ownerid")
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        tuple(curr_car_parameters),
    )
    connection.commit()
    return make_dict_from_transportdata_list(curr_car_parameters)


@app.post("/api/Admin/Transport")
@cross_origin()
@jwt_required()
def admin_create_transport():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    global transport_columns_names
    if not is_admin(curr_id):
        return "Access denied", 403
    curr_json = request.get_json()
    curr_car_parameters = [str(uuid.uuid4()), curr_json["canBeRented"]]
    for parameter in transport_columns_names[2:]:
        curr_car_parameters.append(curr_json[str(parameter)])
    cursor.execute(
        """INSERT INTO TRANSPORT ("id", "canberented", "transporttype", "model", "color", "identifier",
        "description", "latitude", "longitude", "minuteprice", "dayprice", "ownerid")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        tuple(curr_car_parameters),
    )
    connection.commit()
    return make_dict_from_transportdata_list(curr_car_parameters), 200


@app.put("/api/Transport/<transport_id>")
@jwt_required()
@cross_origin()
def index_update_transport(transport_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    global transport_columns_names
    owner_id = get_onwerid_by_transport_id(transport_id)
    if str(owner_id) == str(curr_id):
        cursor.execute('''SELECT * FROM TRANSPORT WHERE id = %s''', (transport_id, ))
        transportdata_list = cursor.fetchall()
        if not transportdata_list:
            return "Transport not found", 404
        transportdata_list = transportdata_list[0]
        old_transport_data = make_dict_from_transportdata_list(transportdata_list)
        curr_json = request.get_json()
        print(old_transport_data)
        for parameter in transport_columns_names[1:11]:
            if parameter != "transportType" and parameter != "ownerID" and parameter != "id":
                old_transport_data[str(parameter)] = curr_json[str(parameter)]
        cursor.execute(
            """UPDATE TRANSPORT SET "id" = %s, "canberented" = %s, "transporttype" = %s, "model" = %s, "color" = %s,
        "identifier" = %s, "description" = %s, "latitude" = %s, "longitude" = %s, "minuteprice" = %s, 
        "dayprice" = %s, ownerid = %s""",
            tuple(make_list_from_transportdata_dict(old_transport_data)),
        )
        connection.commit()
        return old_transport_data, 200
    return "Access denied", 403


@app.put("/api/Admin/Transport/<transport_id>")
@jwt_required()
def admin_update_transport(transport_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute('''SELECT * FROM TRANSPORT WHERE id = %s''', (transport_id, ))
    a = cursor.fetchall()
    if not a:
        return "Transport not found", 404
    curr_json = request.get_json()
    curr_transport_parameters = []
    for parameter in transport_columns_names[1:]:
        curr_transport_parameters.append(curr_json[str(parameter)])
    curr_transport_parameters.append(str(transport_id))
    cursor.execute(
        """UPDATE TRANSPORT SET "canberented" = %s, "transporttype" = %s, "model" = %s, "color" = %s,
            "identifier" = %s, "description" = %s, "latitude" = %s, longitude = %s,
            "minuteprice" = %s, "dayprice" = %s, ownerid = %s WHERE id = %s""",
        tuple(curr_transport_parameters),
    )
    connection.commit()
    return "Done", 200


@app.delete("/api/Transport/<transport_id>")
@jwt_required()
def index_delete_transport(transport_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    try:
        owner_id = get_onwerid_by_transport_id(transport_id)
    except IndexError:
        return "This transport not found", 404
    if str(owner_id) == str(curr_id):
        cursor.execute("DELETE FROM TRANSPORT WHERE id = %s", (transport_id,))
        return "Deleted successfully", 200
    return "Access denied", 403


@app.delete("/api/Admin/Transport/<transport_id>")
@jwt_required()
def admin_delete_transport(transport_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute("DELETE FROM TRANSPORT WHERE id = %s", (transport_id,))
    connection.commit()
    return "Done", 200


@app.get("/api/Rent/Transport")
def index_get_available_transport():
    curr_data = request.headers
    transport_type = curr_data["type"]
    x_circle = float(curr_data["lat"])
    y_circle = float(curr_data["long"])
    radius = float(curr_data["radius"])

    cursor.execute("SELECT * FROM TRANSPORT")
    all_transport = cursor.fetchall()
    if not all_transport:
        return "No transport in database", 404
    available_transport = [
        x[0]
        for x in all_transport
        if check_availability(float(x[7]), float(x[8]), x_circle, y_circle, radius)
        and (x[2] == transport_type or transport_type == "All")
    ]
    return available_transport


@app.get("/api/Rent/<rent_id>")
@jwt_required()
@cross_origin()
def index_get_rent_data(rent_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    cursor.execute("""SELECT * FROM RENTS WHERE rentid = %s""", (rent_id,))
    curr_rent_data = cursor.fetchall()
    if not curr_rent_data:
        return "Rent not found", 404
    curr_rent_data = curr_rent_data[0]
    if (
        curr_rent_data[2] == curr_id
        or get_onwerid_by_transport_id(curr_rent_data[1]) == curr_id
    ):
        return make_dict_from_rentdata_list(curr_rent_data), 200
    return "Access denied", 403


@app.get("/api/Rent/MyHistory")
@jwt_required()
@cross_origin()
def index_get_my_rent_history():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    cursor.execute("SELECT * FROM RENTS WHERE rentorid = %s", (curr_id,))
    rents = cursor.fetchall()
    if not rents:
        return "No rents", 404
    return [make_dict_from_rentdata_list(rent) for rent in rents], 200

@app.get("/api/Admin/Rent/<rent_id>")
@jwt_required()
@cross_origin()
def admin_get_rent_data(rent_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute('''SELECT * FROM RENTS WHERE rentid = %s''', (rent_id, ))
    curr_rent_data = cursor.fetchall()
    if not curr_rent_data:
        return "Rent not found", 404
    curr_rent_data = curr_rent_data[0]
    return make_dict_from_rentdata_list(curr_rent_data)


@app.get("/api/Admin/UserHistory/<user_id>")
@jwt_required()
@cross_origin()
def admin_get_user_rent_history(user_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute("""SELECT * FROM RENTS WHERE rentorid = %s""", (user_id,))
    rents_data = cursor.fetchall()
    if not rents_data:
        return "This user's rents not found (or user does not exist)", 404
    return [make_dict_from_rentdata_list(rent) for rent in rents_data], 200


@app.get("/api/Rent/TransportHistory/<transport_id>")
@jwt_required()
@cross_origin()
def index_get_transport_history_by_id(transport_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (transport_id,))
    curr_transport_data = cursor.fetchall()
    if not curr_transport_data:
        return "This transport not found", 404
    curr_transport_data = curr_transport_data[0]
    if curr_transport_data[11] == curr_id:
        cursor.execute("SELECT * FROM RENTS WHERE transportid = %s", (transport_id,))
        rents_history = cursor.fetchall()
        if not rents_history:
            return "Rents not found", 404
        return [make_dict_from_rentdata_list(rent) for rent in rents_history]
    else:
        return "Access denied", 403


@app.get("/api/Admin/TransportHistory/<transport_id>")
@jwt_required()
def admin_get_transport_rent_history(transport_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute("""SELECT * FROM RENTS WHERE transportid = %s""", (transport_id,))
    rents_data = cursor.fetchall()
    if not rents_data:
        return "Transport's rent history not found (or transport does not exist)", 404
    output = [make_dict_from_rentdata_list(rent_data) for rent_data in rents_data]
    return output, 200


@app.post("/api/Rent/New/<transport_id>")
@jwt_required()
@cross_origin()
def index_rent_transport(transport_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    cursor.execute("SELECT * FROM TRANSPORT WHERE id = %s", (transport_id, ))
    curr_transport_data = cursor.fetchall()
    if not curr_transport_data:
        return "Transport not found", 404
    curr_transport_data = curr_transport_data[0]
    if not curr_transport_data:
        return "This transport not found", 404
    if not curr_transport_data[1]:
        return "This transport can't be rented", 403
    if curr_transport_data[11] != curr_id:
        curr_json = request.get_json()
        rent_type = curr_json["rentType"]
        rent_id = str(uuid.uuid4())
        if rent_type == "Minutes":
            start = str(datetime.datetime.today().now())[:19]
            unit_price = curr_transport_data[9]
        elif rent_type == "Days":
            start = str(datetime.datetime.today().date())
            unit_price = curr_transport_data[0][10]
        else:
            return "Wrong Rent Type", 400
        curr_rent_parameters = [
            rent_id,
            transport_id,
            curr_id,
            start,
            "Not rated",
            unit_price,
            rent_type,
            0,
        ]
        cursor.execute(
            """INSERT INTO RENTS ("rentid", "transportid", "rentorid", "start", "ending", "unitprice",
         "renttype", "finalprice")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            tuple(curr_rent_parameters),
        )
        cursor.execute(
            """UPDATE TRANSPORT SET canberented = %s WHERE id = %s""",
            (False, curr_transport_data[0]),
        )
        connection.commit()
        return make_dict_from_rentdata_list(curr_rent_parameters), 200
    else:
        return "You can't rent your own transport", 403


@app.post("/api/Admin/Rent")
@jwt_required()
def admin_create_rent():
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cj = request.get_json()
    (
        transport_id,
        user_id,
        time_start,
        time_end,
        price_of_unit,
        price_type,
        final_price,
    ) = (
        cj["transportID"],
        cj["userID"],
        cj["timeStart"],
        cj["timeEnd"],
        cj["priceOfUnit"],
        cj["priceType"],
        cj["finalPrice"],
    )
    rent_id = uuid.uuid4()
    cursor.execute(
        """INSERT INTO RENTS (rentid, transportid, rentorid, start, ending, unitprice, renttype, finalprice)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            str(rent_id),
            str(transport_id),
            str(user_id),
            time_start,
            time_end,
            price_of_unit,
            price_type,
            final_price,
        ),
    )
    connection.commit()
    return cj, 200


@app.post("/api/Rent/End/<rent_id>")
@jwt_required()
@cross_origin()
def index_end_rent_by_id(rent_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    cursor.execute("SELECT * FROM RENTS WHERE rentid = %s", (rent_id, ))
    curr_rent_data = cursor.fetchall()
    if not curr_rent_data:
        return "Rent not found", 404
    curr_rent_data = curr_rent_data[0]
    unit_price = curr_rent_data[5]
    print(curr_rent_data)
    if curr_rent_data[2] == curr_id:
        if curr_rent_data[6] == "Minutes":
            difference = datetime.datetime.now() - get_minutes_from_str(str(curr_rent_data[3]))
            price = unit_price + unit_price * difference.total_seconds() // 60
            cursor.execute(
                """UPDATE RENTS SET finalprice = %s WHERE rentid = %s""",
                (price, curr_rent_data[0]),
            )
        elif curr_rent_data[6] == "Days":
            price = unit_price + unit_price * (
                datetime.datetime.now().day - get_days_from_str(str(curr_rent_data[3]))
            )
            cursor.execute(
                """UPDATE RENTS SET finalprice = %s WHERE rentid = %s""",
                (price, curr_rent_data[0]),
            )
        else:
            return "Wrong rent type", 502
        cancel_money_for_rent(curr_id, price)
        cursor.execute(
            """UPDATE RENTS SET ending = %s WHERE rentid = %s""",
            (str(datetime.datetime.now()), curr_rent_data[0]))
        curr_json = request.get_json()
        latitude, longitude = curr_json["lat"], curr_json["long"]
        cursor.execute(
            """UPDATE TRANSPORT SET latitude = %s, longitude = %s WHERE id = %s""",
            (latitude, longitude, curr_rent_data[1]),
        )
        connection.commit()
        return {
            "price": price
        }, 200
    else:
        return "Access denied", 403


@app.post("/api/Admin/Rent/End/<rent_id>")
@jwt_required()
@cross_origin()
def admin_end_rent(rent_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute("SELECT * FROM RENTS WHERE rentid = %s", (rent_id,))
    curr_rent_data = cursor.fetchall()
    if not curr_rent_data:
        return "Rent not found", 404
    curr_rent_data = curr_rent_data[0]
    if curr_rent_data != 0:
        return "Rent have already been ended", 409
    unit_price = curr_rent_data[5]
    user_id = curr_rent_data[2]
    if curr_rent_data[6] == "Minutes":
        price = unit_price + unit_price * (datetime.datetime.now() - get_minutes_from_str(curr_rent_data[3]))
        cursor.execute(
            """UPDATE RENTS SET finalprice = %s WHERE rentid = %s""",
            (price, curr_rent_data[0]),
        )
    elif curr_rent_data[6] == "Days":
        price = unit_price + unit_price * (datetime.datetime.now().day - get_days_from_str(curr_rent_data[3]))
        cursor.execute(
            """UPDATE RENTS SET finalprice = %s WHERE rentid = %s""",
            (price, curr_rent_data[0]),
        )
    else:
        return "Wrong Rent Type", 502
    cancel_money_for_rent(user_id, price)
    curr_json = request.get_json()
    latitude, longitude = curr_json["lat"], curr_json["long"]
    cursor.execute(
        """UPDATE TRANSPORT SET latitude = %s, longitude = %s WHERE id = %s""",
        (latitude, longitude, curr_rent_data[1]),
    )
    connection.commit()
    return "Done", 200


@app.put("/api/Admin/Rent/<rent_id>")
@jwt_required()
@cross_origin()
def admin_update_rent_data(rent_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if not is_admin(curr_id):
        return "Access denied", 403
    cursor.execute('''SELECT * FROM RENTS WHERE rentid = %s''', (rent_id, ))
    a = cursor.fetchall()
    if not a:
        return "Rent not found", 404
    cj = request.get_json()
    (
        transport_id,
        user_id,
        time_start,
        time_end,
        price_of_unit,
        price_type,
        final_price,
    ) = (
        cj["transportID"],
        cj["userID"],
        cj["timeStart"],
        cj["timeEnd"],
        cj["priceOfUnit"],
        cj["priceType"],
        cj["finalPrice"],
    )
    cursor.execute(
        """UPDATE RENTS SET transportid = %s, rentorid = %s, start = %s, ending = %s,
    unitprice = %s, renttype = %s, finalprice = %s WHERE rentid = %s""",
        (
            transport_id,
            user_id,
            time_start,
            time_end,
            price_of_unit,
            price_type,
            final_price,
            rent_id,
        ),
    )
    connection.commit()
    return "Done", 200


@app.post("/api/Payment/Hesoyam/<account_id>")
@jwt_required()
def index_add_250000(account_id):
    if not check_token(get_token()):
        return "NOT VALID TOKEN", 401
    curr_id = get_id_from_token()
    if is_admin(curr_id):
        try:
            add_250000_to_balance(account_id)
            return "Done", 200
        except ():
            return "User not found", 404
    else:
        if account_id == curr_id:
            try:
                add_250000_to_balance(account_id)
                return "Done", 200
            except ():
                return "User not found", 404
