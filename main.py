import requests
from viya_function import *
from prometheus_client import Gauge, Counter, start_http_server
import schedule
import time

endpoint = "tksviya.unx.sas.com"
cas_endpoint = "tksviya.unx.sas.com"

# Viya - Get Bearer Token
BT = get_bearer_token(endpoint, "Jask", "demopw")
# Define CAS API URL
# cas_path = "cas/nodes"
cas_port = 47384 #47839

# define prmetheus metrics
cas_node_status_gauge = Gauge('cas_server_health', 'Indicates server health (1 for healthy, 0 for unhealthy)', ['cas_node'])
session_cpu_usage_gauge = Gauge('cas_session_cpu', 'CPU usage of sessions', ['session_name', 'node_type'])
session_mem_usage_gauge = Gauge('mem_session_cpu', 'MEM usage of sessions', ['session_name', 'node_type'])


def fetch_and_update_prometrics():
    cas_node_status = get_cas_info(cas_endpoint, cas_port, BT)
    print(cas_node_status)
    for server in cas_node_status:
        print(cas_node_status[server])
        cas_node_status_gauge.labels(cas_node=server).set(1 if cas_node_status[server] is True else 0)
    return


# get CPU & Mem usage of each session.
session_list = get_session(cas_endpoint, cas_port, BT)
print(session_list)
# for loop for each Session
for session_name in session_list:
    session_on_node = get_session_node(cas_endpoint, cas_port, BT, session_list[session_name])

    controller_cpu_sum = 0
    bk_controller_cpu_sum = 0
    worker_cpu_sum = 0
    controller_mem_sum = 0
    bk_controller_mem_sum = 0
    worker_mem_sum = 0

    # for loop for each PID on a node
    for node in session_on_node:
        cpu_mem_list = get_grid_info(cas_endpoint, cas_port, BT, node, session_on_node[node])
        if "controller" in node:
            controller_cpu_sum += cpu_mem_list[0]
            controller_mem_sum += cpu_mem_list[1]
        elif "backup" in node:
            bk_controller_cpu_sum += cpu_mem_list[0]
            bk_controller_mem_sum += cpu_mem_list[1]
        elif "worker" in node:
            worker_cpu_sum += cpu_mem_list[0]
            worker_mem_sum += cpu_mem_list[1]
    # Have gotten the total CPU, Mem usage of a Session.Then update the Prometheus Metrics
    session_cpu_usage_gauge.labels(session_name=session_name, node_type="controller").set(controller_cpu_sum)
    session_cpu_usage_gauge.labels(session_name=session_name, node_type="backup-controller").set(bk_controller_cpu_sum)
    session_cpu_usage_gauge.labels(session_name=session_name, node_type="worker").set(worker_cpu_sum)

    session_mem_usage_gauge.labels(session_name=session_name, node_type="controller").set(controller_mem_sum)
    session_mem_usage_gauge.labels(session_name=session_name, node_type="backup-controller").set(bk_controller_mem_sum)
    session_mem_usage_gauge.labels(session_name=session_name, node_type="worker").set(worker_mem_sum)


# get_grid_info(cas_endpoint, cas_port, BT, "worker-0.sas-cas-server-default.viya4deploy.svc.cluster.local", 244571)


# schedule.every(30).seconds.do(fetch_and_update_prometrics)
#
# if __name__ == "__main__":
#     # Start Prometheus HTTP server
#     start_http_server(8000)  # Port where Prometheus will scrape metrics
#
#     # Schedule job
#     while True:
#         schedule.run_pending()
#         time.sleep(1)






