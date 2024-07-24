import requests
import json


def get_bearer_token(sas_server, user, pw):
    url = f"https://{sas_server}/SASLogon/oauth/token"
    payload = f"grant_type=password&username={user} &password={pw}"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic c2FzLmNsaTo='}

    response = requests.request("POST", url, headers=headers, data=payload)
    bearer_token = json.loads(response.text)['access_token']
    return bearer_token
