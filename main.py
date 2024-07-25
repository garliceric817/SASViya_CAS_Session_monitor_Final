import requests
from function import get_bearer_token, get_cas_info

endpoint = "tksviya.unx.sas.com"
cas_endpoint = "tksviya.unx.sas.com"

# Get Bearer Token
BT = get_bearer_token(endpoint, "Jask", "demopw")
# Define CAS API URL
cas_path = "cas/nodes"
cas_port = 47384

# Get every CAS nodes' status
cas_node_status = get_cas_info(cas_endpoint, cas_port, BT)




