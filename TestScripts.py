import requests
from requests import post, get, put, delete
import DataBaseScripts as db
from ServerFunctions import *

root = "http://127.0.0.1:5000/api/"
test_transport_id = 'd96d0620-70d1-413e-a1e7-77177a5ef0d2'
test_rent_id = None
test_user_token = None
headers = None
test_account_id = '55ea4814-694c-421c-a5bf-0c7ab796af25'


def test_sign_up(username="tester", password="1234", url=root):
    url += "Account/SignUp"
    curr_json = {"username": username, "password": password}
    rqst = post(url, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Sign Up' completed successfully!")
        print(rqst.json())
        global test_account_id
        test_account_id = rqst.json()["id"]
    else:
        print(f"Test 'Sign Up' ERROR: {rqst.status_code}")


def test_me(header, url=root):
    url += "/Account/Me"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Me' successful!")
        print(rqst.json())
    else:
        print(f"'Me' ERROR: {rqst.status_code}")
def test_sign_out(header, url=root):
    url += "Account/SignOut"
    rqst = post(url, headers=header)
    if rqst.status_code == 200:
        print("Signed Out Successfully!")
    else:
        print(f"Sign Out ERROR: {rqst.status_code}")

def test_admin_sign_in(username="admin", password="1234", url=root):
    global headers, test_user_token
    url += "Account/SignIn"
    curr_json = {"username": username, "password": password}
    rqst = post(url, json=curr_json)
    if rqst.status_code == 200:
        test_user_token = rqst.json()["token"]
        headers = {"Authorization": "Bearer " + test_user_token}
        print("Test 'Sign In' completed successfully!")
    else:
        print(f"Test 'Sign In' ERROR: {rqst.status_code}")

def test_sign_in(username, password, url=root):
    global headers, test_user_token
    url += "Account/SignIn"
    curr_json = {"username": username, "password": password}
    rqst = post(url, json=curr_json)
    if rqst.status_code == 200:
        test_user_token = rqst.json()['token']
        headers = {"Authorization": "Bearer " + test_user_token}
        print(rqst.json())
        print("Test 'Sign In' completed successfully!")
    else:
        print(f"Test 'Sign In' ERROR: {rqst.status_code}")


def test_admin_create_transport(header, url=root):
    url += "Admin/Transport"
    curr_json = {
        "ownerID": "0",
        "canBeRented": True,
        "transportType": "test_transport_type",
        "model": "test_model",
        "color": "test_color",
        "identifier": "test_identifier",
        "description": "test_description",
        "latitude": 456.0,
        "longitude": 456.0,
        "minutePrice": 1,
        "dayPrice": 2000,
    }
    rqst = post(url, json=curr_json, headers=header)
    if rqst.status_code == 200:
        global test_transport_id
        test_transport_id = rqst.json()["id"]
        print("Test 'Create Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Create Transport' ERROR: {rqst.status_code}")

def test_create_transport(header, url=root):
    url += "Transport"
    curr_json = {
        "canBeRented": True,
        "transportType": "test_transport_type",
        "model": "test_model",
        "color": "test_color",
        "identifier": "test_identifier",
        "description": "test_description",
        "latitude": 456.0,
        "longitude": 456.0,
        "minutePrice": 1,
        "dayPrice": 2000,
    }
    rqst = post(url, json=curr_json, headers=header)
    if rqst.status_code == 200:
        global test_transport_id
        test_transport_id = rqst.json()["id"]
        print("Test 'Create Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Create Transport' ERROR: {rqst.status_code}")

def test_rent_transport(header,
    rent_type, transport_id, url=root):
    url += f"Rent/New/{str(transport_id)}"
    curr_json = {"rentType": rent_type}
    rqst = post(url, json=curr_json, headers=header)
    if rqst.status_code == 200:
        global test_rent_id
        test_rent_id = rqst.json()["rentId"]
        print("Test 'Rent Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Rent Transport' ERROR: {rqst.status_code}")


def test_end_rent(header, rent_id, url=root):
    url += f"/Rent/End/{str(rent_id[0])}"
    curr_json = {"lat": 456.0, "long": 456.0}
    rqst = post(url, json=curr_json, headers=header)
    if rqst.status_code == 200:
        print("Test 'End Rent Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'End Rent Transport' ERROR: {rqst.status_code}")


def test_get_my_rent_history(header, url=root):
    url += "/Rent/MyHistory"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Get User Rent History' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Get User Rent History' ERROR: {rqst.status_code}")


def test_get_transport_rent_history(header, transport_id, url=root):
    url += f"/Rent/TransportHistory/{str(transport_id[0])}"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Get Transport Rent History' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Get Transport Rent History' ERROR: {rqst.status_code}")


def test_admin_get_transport_rent_history(transport_id, header, url=root):
    url += f"/Admin/TransportHistory/{str(transport_id[0])}"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Get Admin Transport Rent History' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Get Admin Transport Rent History' ERROR: {rqst.status_code}")

def test_admin_create_rent(header, url=root):
    url += "Admin/Rent"
    curr_json = {
        "transportID": "test_transport_id",
        "userID": "test_user_id",
        "timeStart": 0.0,
        "timeEnd": 0.0,
        "priceOfUnit": 1.0,
        "priceType": "Days",
        "finalPrice": 100.0
    }
    rqst = post(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Admin Create Rent' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Admin Create Rent' ERROR: {rqst.status_code}")


def test_get_rent_data(rent_id, header, url=root):
    url += f"Rent/{str(rent_id[0])}"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Get Rent Data' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Get Ret Data' ERROR: {rqst.status_code}")


def test_get_available_transport(url=root):
    url += "Rent/Transport"
    curr_json = {
        "type": "All",
        "long": 456.0,
        "lat": 456.0,
        "radius": 1000
    }
    rqst = get(url, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Get Available Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Get Available Transport' ERROR: {rqst.status_code}")


def test_delete_transport(transport_id, header, url=root):
    url += f"Transport/{str(transport_id[0])}"
    rqst = delete(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Delete Transport' completed successfully!")
    else:
        print(f"Test 'Delete Transport' ERROR: {rqst.status_code}")


def test_update_transport(transport_id, header, url=root):
    url += f"Transport/{str(transport_id[0])}"
    curr_json = {
        "canBeRented": True,
        "model": "updated",
        "color": "updated",
        "identifier": "updated",
        "description": "updated",
        "latitude": 456.0,
        "longitude": 456.0,
        "minutePrice": 1,
        "dayPrice": 100
    }
    rqst = put(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Update Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Update Transport' ERROR: {rqst.status_code}")


def test_get_transportdata_by_id(transport_id, header, url=root):
    url += f"Transport/{str(transport_id[0])}"
    rqst = get(url, headers=header)


def test_update_account(header, url=root):
    url += "Account/Update"
    curr_json = {
        "username": "updated_username",
        "password": "updated+password"
    }
    rqst = put(url, json=curr_json, headers=header)
    if rqst.status_code == 200:
        print("Test 'Update Account' completed successfully!")
    else:
        print(f"Test 'Update Account' ERROR: {rqst.status_code}")


def test_hesoyam(account_id, header,  url=root):
    url += f"Payment/Hesoyam/{str(account_id)}"
    rqst = post(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Hesoyam' completed successfully!")
    else:
        print(f"Test 'Hesoyam' ERROR: {rqst.status_code}")


def test_admin_get_all_accounts(header, url=root):
    url += "Admin/Account"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Admin Get All Accounts' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Admin Get All Accounts' ERROR: {rqst.status_code}")

def test_admin_get_account_data(header, account_id, url=root):
    url += f"Admin/Account/{str(account_id)}"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Admin Get Account Data' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Admin Get Account Data' ERROR: {rqst.status_code}")

def test_admin_create_account(header, url=root):
    url += "Admin/Account"
    curr_json = {
        "username": "test",
        "password": "test",
        "isAdmin": False,
        "balance": 10
    }
    rqst = post(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Admin Create Account' completed successfully!")
    else:
        print(f"Test 'Admin Create Account' ERROR: {rqst.status_code}")

def test_admin_change_account(header, account_id, url=root):
    url += f"Admin/Account/{str(account_id)}"
    curr_json = {
        "username": "updated",
        "password": "updated",
        "isAdmin": False,
        "balance": 100
    }
    rqst = put(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Admin Update Account' completed successfully!")
    else:
        print(f"Test 'Admin Update Account' ERROR: {rqst.status_code}")

def test_admin_delete_account(header, acoount_id='1366b42b-206c-4933-96e2-7cd2e28a9cbb', url=root):
    url += f"Admin/Account/{str(acoount_id)}"
    rqst = delete(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Admin Delete Account' completed successfully!")
    else:
        print(f"Test 'Admin Delete Account' ERROR: {rqst.status_code}")

def test_admin_get_transportlist(header, url=root):
    url += "Admin/Transport"
    curr_json = {
        "start": 0,
        "count": 100,
        "transportType": "All"
    }
    rqst = get(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Admin Get Transport List' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Admin Get Transport List' ERROR: {rqst.status_code}")

def test_admin_get_transport_data(header, transport_id, url=root):
    url += f"Admin/Transport/{str(transport_id)}"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Admin Get Transport Data' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Admin Get Transport Data' ERROR: {rqst.status_code}")

def test_admin_update_transport(header, transport_id, url=root):
    url += f"Admin/Transport/{str(transport_id)}"
    curr_json = {
        "ownerID": "55ea4814-694c-421c-a5bf-0c7ab796af25",
        "canBeRented": True,
        "transportType": "Car",
        "model": "string",
        "color": "string",
        "identifier": "string",
        "description": "string",
        "latitude": 456.0,
        "longitude": 456.0,
        "minutePrice": 1,
        "dayPrice": 100
    }
    rqst = put(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Admin Update Transport' completed successfully!")
    else:
        print(f"Test 'Admin Update Transport' ERROR: {rqst.status_code}")


def test_admin_delete_transport(header, transport_id, url=root):
    url += f"Admin/Transport/{str(transport_id)}"
    rqst = delete(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Admin Delete Transport' completed successfully!")
    else:
        print(f"Test 'Admin Delete Transport' ERROR: {rqst.status_code}")


def test_admin_get_rent_data(header, rent_id, url=root):
    url += f"/Admin/Rent/{rent_id}"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Admin Get Rent Data' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Admin Get Rent Data' ERROR: {rqst.status_code}")

def test_admin_get_user_rent_history(header, user_id, url=root):
    url += f"/Admin/UserHistory/{user_id}"
    rqst = get(url, headers=header)
    if rqst.status_code == 200:
        print("Test 'Admin Get User Rent History' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Admin Get User Rent History' ERROR: {rqst.status_code}")

def test_admin_end_rent(header, rent_id, url=root):
    url += f"/Admin/Rent/End/{str(rent_id)}"
    curr_json = {
        "lat": 456.0,
        "long": 456.0
    }
    rqst = post(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Admin End Rent' completed successfully!")
    else:
        print(f"Test 'Admin End Rent' ERROR: {rqst.status_code}")

def test_admin_update_rent(header, rent_id, url=root):
    url += f"Admin/Rent/{str(rent_id)}"
    curr_json = {
        "transportID": "updated",
        "userID": "updated",
        "timeStart": "updated",
        "timeEnd": "updated",
        "priceOfUnit": 10.0,
        "priceType": "Minutes",
        "finalPrice": 1000.0
    }
    rqst = put(url, headers=header, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Admin Update Rent' completed successfully!")
    else:
        print(f"Test 'Admin Update Rent' ERROR: {rqst.status_code}")

test_sign_in("tester", "1234")








