import requests
import json

import http.client
import ssl


def get_bearer_token(sas_server, user, pw):
    url = f"https://{sas_server}/SASLogon/oauth/token"
    payload = f"grant_type=password&username={user} &password={pw}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic c2FzLmNsaTo='
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    bearer_token = json.loads(response.text)['access_token']
    return bearer_token


def get_cas_info(cas_server, port, bt):
    path = "cas/nodes"
    url = f"https://{cas_server}:{port}/{path}"

    headers = {
        'Authorization': f"Bearer {bt}",
        'Accept': "application/vnd.sas.collection+json"
    }

    # Send the GET request with SSL verification disabled
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        # uuids = [item['uuid'] for item in data if 'uuid' in item]
        # print(uuids)
        name_connected_dict = {item['name']: item['connected'] for item in data}
        print(name_connected_dict)
        # print(data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
    return name_connected_dict

