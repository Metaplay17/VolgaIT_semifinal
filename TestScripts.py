import requests
from requests import post, get, put, delete
import DataBaseScripts as db
from ServerFunctions import *

root = "http://127.0.0.1:5000/api/"
test_transport_id = None
test_rent_id = None
test_user_token = None

def test_sign_up(username="tester", password="1234", url=root):
    url += "Account/SignUp"
    curr_json = {
        "username": username,
        "password": password
    }
    rqst = post(url, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'Sign Up' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Sign Up' ERROR: {rqst.status_code}")


def test_sign_in(username="tester", password="1234", url=root):
    url += "Account/SignIn"
    curr_json = {
        "username": username,
        "password": password
    }
    rqst = post(url, json=curr_json)
    if rqst.status_code == 200:
        global test_user_token
        test_user_token = rqst.json()["token"]
        print("Test 'Sign In' completed successfully!")
    else:
        print(f"Test 'Sign In' ERROR: {rqst.status_code}")


def test_create_transport(url=root):
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
        "dayPrice": 2000
    }
    global test_user_token
    headers = {
        "Authorization": "Bearer " + test_user_token
    }
    print(test_user_token)
    rqst = post(url, json=curr_json, headers=headers)
    if rqst.status_code == 200:
        global test_transport_id
        test_transport_id = rqst.json()["id"]
        print("Test 'Create Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Create Transport' ERROR: {rqst.status_code}")


def test_rent_transport(rent_type, transport_id=test_transport_id, url=root):
    url += f"Rent/New/{transport_id}"
    curr_json = {
        "renttype": rent_type
    }
    rqst = post(url, json=curr_json)
    if rqst.status_code == 200:
        global test_rent_id
        test_rent_id = rqst.json()["id"]
        print("Test 'Rent Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Rent Transport' ERROR: {rqst.status_code}")


def test_end_rent(rent_id=test_rent_id, url=root):
    url += f"/Rent/End/{rent_id}"
    curr_json = {
        "lat": 456.0,
        "long": 456.0
    }
    rqst = post(url, json=curr_json)
    if rqst.status_code == 200:
        print("Test 'End Rent Transport' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'End Rent Transport' ERROR: {rqst.status_code}")


def test_get_my_rent_history(url=root):
    url += "/Rent/MyHistory"
    rqst = get(url)
    if rqst.status_code == 200:
        print("Test 'Get User Rent History' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Get User Rent History' ERROR: {rqst.status_code}")


def test_get_transport_rent_history(transport_id=test_transport_id, url=root):
    url += f"/Rent/TransportHistory/{transport_id}"
    rqst = get(url)
    if rqst.status_code == 200:
        print("Test 'Get Transport Rent History' completed successfully!")
        print(rqst.json())
    else:
        print(f"Test 'Get Transport Rent History' ERROR: {rqst.status_code}")


# test_sign_up()
test_sign_in()
test_create_transport()