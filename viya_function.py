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
        node_connect_status = {item['name']: item['connected'] for item in data}
        # print(data)
        return node_connect_status
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return


def get_session(cas_server, port, bt):
    path = "cas/sessions"
    url = f"https://{cas_server}:{port}/{path}"

    headers = {
        'Authorization': f"Bearer {bt}",
        'Accept': "application/vnd.sas.collection+json"
    }

    # Send the GET request with SSL verification disabled
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        # print(data)
        session_list = {session_info["name"]: session_info["uuid"] for session_info in data}
        return session_list
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return


def get_session_node(cas_server, port, bt, uuid):
    path = f"cas/sessions/{uuid}/nodes/metrics"
    url = f"https://{cas_server}:{port}/{path}"

    headers = {
        'Authorization': f"Bearer {bt}",
        'Accept': "application/vnd.sas.collection+json"
    }

    # Send the GET request with SSL verification disabled
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        pid_on_node = {chunk['name']: chunk['pid'] for chunk in data}

        return pid_on_node
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return


def get_grid_info(cas_server, port, bt, node_name, pid):
    path = f"grid/{node_name}/processes/{pid}"
    url = f"https://{cas_server}:{port}/{path}"

    headers = {
        'Authorization': f"Bearer {bt}",
        'Accept': "application/vnd.sas.collection+json"
    }

    # Send the GET request with SSL verification disabled
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        data = response.json()
        cpu = data["cpu"]
        mem = data["vmSize"]
        return (cpu, mem)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return
