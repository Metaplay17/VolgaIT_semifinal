from requests import post

url = "http://127.0.0.1:5000/"

def create_transport(url=url):
    url += "api/Transport"
    curr_json = {
        "canberented": True,
        "transporttype": "test_transport_type",
        "model": "test_model",
        "color": "test_color",
        "identifier": "test_identifier",
        "description": "test_description",
        "latitude": 456.0,
        "longitude": 456.0,
        "minuteprice": 1,
        "dayprice": 2000
    }
    rqst = post(url, json=curr_json)
    return rqst.json()

def rent_transport(transport_id, url=url):
    url += f"/api/Rent/New/{transport_id}"
    curr_json = {
        "renttype": "Minutes"
    }
    rqst = post(url, json=curr_json)
    return rqst

def end_rent(rent_id, url=url):
    url += f"/api/Rent/End/{rent_id}"
    curr_json = {
        "lat": 456,
        "long": 456
    }
    rqst = post(url, json=curr_json)
    return rqst

print(end_rent("bf146d41-62db-4bad-99b7-1c8bee777800"))

