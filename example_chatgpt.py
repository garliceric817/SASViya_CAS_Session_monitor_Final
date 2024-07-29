
#1. Define Metrics with Labels
from prometheus_client import Gauge, Counter, start_http_server

# Define metrics with a 'server' label
health_gauge = Gauge('server_health', 'Indicates server health (1 for healthy, 0 for unhealthy)', ['server'])
sessions_counter = Counter('total_sessions', 'Total number of sessions', ['server'])

import requests

# List of server endpoints or server names
servers = {
    'server1': 'http://server1-endpoint.com/status',
    'server2': 'http://server2-endpoint.com/status',
    'server3': 'http://server3-endpoint.com/status',
}

# 2. Fetch and Update Metrics for Multiple Servers
def fetch_and_update_metrics():
    for server_name, url in servers.items():
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            data = response.json()

            # Assuming the API response contains 'healthy' and 'session_count'
            is_healthy = data.get('healthy', False)
            session_count = data.get('session_count', 0)

            # Update Prometheus metrics for each server
            health_gauge.labels(server=server_name).set(1 if is_healthy else 0)
            sessions_counter.labels(server=server_name).inc(session_count)

        except requests.RequestException as e:
            print(f"Error fetching data from {server_name}: {e}")


# 3. Schedule Regular API Calls
import schedule
import time

def job():
    fetch_and_update_metrics()

# Schedule the job every minute
schedule.every(1).minute.do(job)

# Main loop to keep the script running
if __name__ == "__main__":
    # Start Prometheus HTTP server
    start_http_server(8000)  # Port where Prometheus will scrape metrics

    # Schedule job
    while True:
        schedule.run_pending()
        time.sleep(1)

# 4. Configure Prometheus
scrape_configs:
  - job_name: 'my_app'
    static_configs:
      - targets: ['localhost:8000']