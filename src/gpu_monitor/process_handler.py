"""Process Handler Module.

This module provides functionality to start and monitor a process, capturing its CPU and memory usage,
as well as GPU usage if applicable. The monitored data is stored in a CSV file at specified intervals.
"""

import csv
import logging
import os
import time
from datetime import datetime
from math import inf

import psutil

from gpu_monitor.gpu_info import get_gpu_info


# Configure logging
log_level = os.getenv("GPU_MONITOR_LOG_LEVEL", logging.WARNING)
logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def store_dicts_as_csv(data: list[dict], filename: str) -> None:
    """Store a list of dictionaries as a CSV file.

    Args:
        data: A list of dictionaries containing the data to be written to the CSV file.
        filename: The name of the CSV file to write the data to.
    """
    if not data:
        print("No data to write.")
        return

    # Get the fieldnames from the keys of the first dictionary
    fieldnames = data[0].keys()

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def start_and_monitor(
    command: str,
    interval: int = 1,
    max_duration: int = inf,
    storing_interval: int = 10,
    storing_location: str = ".vscode/process_info.csv",
    log_cpu_usage: bool = False,
) -> None:
    """Start and monitor a process.

    Args:
        command: The command to run.
        interval: Interval between checks in seconds.
        max_duration: Maximum duration to run in seconds.
        storing_interval: Interval between storing data in seconds.
        storing_location: Location to store the CSV file.
        log_cpu_usage: Whether to log CPU usage.
    """
    # Start the subprocess
    if command.split()[0].split(".")[-1] == "py":
        command = f"python {command}"
        logger.debug(f"Adding python to command: {command}")
    process = psutil.Popen(command.split())

    # Get the process ID
    pid = process.pid

    # Monitor the process
    storage_data = []
    try:
        start_time = time.time()
        time_since_laster_csv_update = 0
        while time.time() - start_time < max_duration and process.is_running():
            # Check if the process is still running
            if psutil.pid_exists(pid):
                proc = psutil.Process(pid)
                cpu_usage = proc.cpu_percent(interval=interval) if log_cpu_usage else 0
                memory_info = proc.memory_info()
                memory_usage = memory_info.rss

                for child in proc.children(recursive=True):
                    try:
                        memory_usage += child.memory_info().rss
                    except psutil.NoSuchProcess:
                        continue

                process_ressource_data = get_gpu_info()
                process_ressource_data["cpu_usage"] = cpu_usage
                process_ressource_data["memory_usage"] = memory_usage
                process_ressource_data["timestamp"] = str(datetime.now())  # noqa: DTZ005
                storage_data.append(process_ressource_data)

                time_since_laster_csv_update += interval
                if time_since_laster_csv_update >= storing_interval:
                    store_dicts_as_csv(storage_data, storing_location)
                    time_since_laster_csv_update = 0

                time.sleep(interval)
            else:
                logger.debug("Process has terminated.")
                break
    except KeyboardInterrupt:
        logger.debug("Monitoring stopped.")
    finally:
        # Log GPU info to CSV
        store_dicts_as_csv(storage_data, storing_location)
        # Terminate the process
        logger.debug("Terminating the process.")

        for child in process.children(recursive=True):  # or parent.children() for recursive=False
            child.kill()
        process.kill()
        process.wait()
        logger.debug("Process terminated.")
