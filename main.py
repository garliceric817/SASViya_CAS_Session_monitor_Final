import requests
from viya_function import *
from prometheus_client import Gauge, Counter, start_http_server, CollectorRegistry
import schedule
import time

endpoint = "tksviya.unx.sas.com"
cas_endpoint = "tksviya.unx.sas.com"

# Viya - Get Bearer Token
BT = get_bearer_token(endpoint, "Jask", "demopw")
# Define CAS API URL
# cas_path = "cas/nodes"
cas_port = 47384 #47384


# define prmetheus metrics
cas_node_status_gauge = Gauge('cas_server_health', 'Indicates server health (1 for healthy, 0 for unhealthy)', ['cas_node'])
session_cpu_usage_gauge = Gauge('cas_session_cpu', 'CPU usage of sessions', ['session_name', 'node_type'])
session_mem_usage_gauge = Gauge('cas_session_mem', 'MEM usage of sessions', ['session_name', 'node_type'])


def fetch_and_update_prometrics():
    cas_node_status = get_cas_info(cas_endpoint, cas_port, BT)
    print(cas_node_status)
    try:
        for server in cas_node_status:
            cas_node_status_gauge.labels(cas_node=server).set(1 if cas_node_status[server] is True else 0)
    except IOError:
        print("Cant get node status")
    return


# get CPU & Mem usage of each session.
def fetch_and_update_prometrics_cpu_mem(last_times_session_list):
    session_list = get_session(cas_endpoint, cas_port, BT)

    # remove gone sessions
    for session_name in last_times_session_list:
        try:
            if session_name not in session_list:
                print(f'{session_name} is gone, remove corresponding metrics')
                node_type = ["controller", "backup-controller", "worker"]
                for node in node_type:
                    # session_cpu_usage_gauge.labels(session_name=session_name, node_type=node).set(0)
                    # session_mem_usage_gauge.labels(session_name=session_name, node_type=node).set(0)
                    session_cpu_usage_gauge.remove(session_name, node)
                    session_mem_usage_gauge.remove(session_name, node)
        except IOError:
            print('First layer exception')
            continue

    print(session_list)
    # for loop for each Session
    for session_name in session_list:
        session_on_node = get_session_node(cas_endpoint, cas_port, BT, session_list[session_name])
        print(session_name)
        print(session_on_node)

        controller_cpu_sum = 0
        bk_controller_cpu_sum = 0
        worker_cpu_sum = 0
        controller_mem_sum = 0
        bk_controller_mem_sum = 0
        worker_mem_sum = 0

        try:
        # for loop for each PID on a node
            for node in session_on_node:
                try:
                    cpu_mem_list = get_grid_info(cas_endpoint, cas_port, BT, node, session_on_node[node])
                except IOError:
                    for i in range(3):
                        print(f"retry {i+1}")
                        time.sleep(30)
                        cpu_mem_list = get_grid_info(cas_endpoint, cas_port, BT, node, session_on_node[node])
                        if cpu_mem_list is None:
                            continue
                        else:
                            break

                # [0] = CPU, [1] = MEM
                if "controller" in node:
                    controller_cpu_sum += int(cpu_mem_list[0])
                    controller_mem_sum += int(cpu_mem_list[1])
                elif "backup" in node:
                    bk_controller_cpu_sum += int(cpu_mem_list[0])
                    bk_controller_mem_sum += int(cpu_mem_list[1])
                elif "worker" in node:
                    worker_cpu_sum += int(cpu_mem_list[0])
                    worker_mem_sum += int(cpu_mem_list[1])
            # Have gotten the total CPU, Mem usage of a Session.Then update the Prometheus Metrics
            session_cpu_usage_gauge.labels(session_name=session_name, node_type="controller").set(controller_cpu_sum)
            session_cpu_usage_gauge.labels(session_name=session_name, node_type="backup-controller").set(
                bk_controller_cpu_sum)
            session_cpu_usage_gauge.labels(session_name=session_name, node_type="worker").set(worker_cpu_sum)

            session_mem_usage_gauge.labels(session_name=session_name, node_type="controller").set(controller_mem_sum)
            session_mem_usage_gauge.labels(session_name=session_name, node_type="backup-controller").set(
                bk_controller_mem_sum)
            session_mem_usage_gauge.labels(session_name=session_name, node_type="worker").set(worker_mem_sum)
            # except requests.RequestException as e:
            #     print(f"Error fetching data from {session_name}: {e}")
            #     continue
        except IOError:     # Set all metrics value = 0 of disappeared session
            print(f"Session - {session_name} is gone, set all metrics = 0")
            node_type_list = ["worker", "backup-controller", "controller"]
            try:
                for node in node_type_list:
                    # session_cpu_usage_gauge.labels(session_name=session_name, node_type=node).set(0)
                    # session_mem_usage_gauge.labels(session_name=session_name, node_type=node).set(0)
                    session_cpu_usage_gauge.remove(session_name, node)
                    session_mem_usage_gauge.remove(session_name, node)
            except IOError:
                print('middle layer exception')
                continue

    session_list_final = get_session(cas_endpoint, cas_port, BT)
    # remove gone session
    for session_name in session_list:
        try:
            if session_name not in session_list_final:
                print(f'{session_name} is gone, remove corresponding metrics')
                node_type = ["controller", "backup-controller", "worker"]
                for node in node_type:
                    # session_cpu_usage_gauge.labels(session_name=session_name, node_type=node).set(0)
                    # session_mem_usage_gauge.labels(session_name=session_name, node_type=node).set(0)
                    session_cpu_usage_gauge.remove(session_name, node)
                    session_mem_usage_gauge.remove(session_name, node)
        except IOError:
            print('last layer exception')
            continue

    return session_list_final
# get_grid_info(cas_endpoint, cas_port, BT, "worker-0.sas-cas-server-default.viya4deploy.svc.cluster.local", 244571)


if __name__ == "__main__":
    # Start Prometheus HTTP server
    start_http_server(8000)  # Port where Prometheus will scrape metrics

    # Schedule job
    initial_session_list = []
    while True:

        fetch_and_update_prometrics()
        final_session_list = fetch_and_update_prometrics_cpu_mem(initial_session_list)
        initial_session_list = final_session_list
        time.sleep(30)





