import subprocess
import time
from datetime import datetime
from math import inf

import psutil

from gpu_monitor.gpu_info import GPUInfoLogger, get_gpu_info
from gpu_monitor.io import store_dicts_as_csv


def start_and_monitor(
    command: str,
    interval: int = 1,
    max_duration: int = inf,
    storing_interval: int = 10,
    storing_location: str = "process_info.csv",
):
    # Start the subprocess
    process = psutil.Popen(command, shell=True)

    # Get the process ID
    pid = process.pid

    # Initialize GPUInfoLogger

    # Monitor the process
    storage_data = []
    try:
        start_time = time.time()
        time_since_laster_csv_update = 0
        while time.time() - start_time < max_duration:
            # Check if the process is still running
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                cpu_usage = proc.cpu_percent(interval=interval)
                memory_info = proc.memory_info()

                process_ressource_data = get_gpu_info()
                process_ressource_data["cpu_usage"] = cpu_usage
                process_ressource_data["memory_usage"] = memory_info.rss
                process_ressource_data["timestamp"] = str(datetime.now())
                storage_data.append(process_ressource_data)

                if time_since_laster_csv_update >= storing_interval:
                    store_dicts_as_csv(storage_data, storing_location)
                    time_since_laster_csv_update = 0

                time.sleep(interval)
            else:
                print("Process has terminated.")
                break
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    finally:
        # Log GPU info to CSV
        store_dicts_as_csv(storage_data, storing_location)
        # Terminate the process
        print("Terminating the process.")
        process.kill()
        process.wait()
        print("Process terminated.")


if __name__ == "__main__":
    command = "python .vscode/test.py"  # Replace with your command
    start_and_monitor(command, interval=1, max_duration=15, storing_interval=1)
