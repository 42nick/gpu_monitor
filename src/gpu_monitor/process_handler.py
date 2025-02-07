"""Process Handler Module.

This module provides functionality to start and monitor a process, capturing its CPU and memory usage,
as well as GPU usage if applicable. The monitored data is stored in a CSV file at specified intervals.
"""

from __future__ import annotations

import csv
import logging
import os
import subprocess
import time
from datetime import datetime
from math import inf
from pathlib import Path

import psutil

from gpu_monitor.gpu_info import get_gpu_info


DEFAULT_STORING_ROOT = Path.home().joinpath(".gpu_monitor")
DEFAULT_STORING_ROOT.mkdir(exist_ok=True)
DEFAULT_STORING_NAME = "gpu_logs.csv"


# Configure logging
log_level = os.getenv("GPU_MONITOR_LOG_LEVEL", logging.WARNING)
logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def store_dicts_as_csv(data: list[dict], filepath: str) -> None:
    """Store a list of dictionaries as a CSV file.

    Args:
        data: A list of dictionaries containing the data to be written to the CSV file.
        filepath: The name of the CSV file to write the data to.
    """
    if not data:
        print("No data to write.")
        return

    # Get the fieldnames from the keys of the first dictionary
    fieldnames = data[0].keys()

    if filepath is None:
        storing_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = DEFAULT_STORING_ROOT.joinpath(f"{storing_date}_{DEFAULT_STORING_NAME}")

    with open(filepath, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def check_nvidia_smi() -> None:
    """Check if nvidia-smi is available."""
    try:
        subprocess.run(  # noqa: S603
            ["nvidia-smi"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        logger.warning("nvidia-smi command not found. Can not log GPU data.")


def start_process(command: str) -> psutil.Popen:
    """Start the subprocess.

    Args:
        command: The command to run.

    Returns:
        The started process.
    """
    if command.split()[0].split(".")[-1] == "py":
        command = f"python {command}"
        logger.debug(f"Adding python to command: {command}")
    return psutil.Popen(command.split())


def collect_process_data(proc: psutil.Process, log_cpu_usage: bool) -> dict:
    """Collect data from the process.

    Args:
        proc: The process to collect data from.
        log_cpu_usage: Whether to log CPU usage.

    Returns:
        A dictionary containing the collected data.
    """
    cpu_usage = proc.cpu_percent(interval=0) if log_cpu_usage else 0
    memory_info = proc.memory_full_info()
    memory_usage_rss = memory_info.rss
    memory_usage_pss = memory_info.pss
    memory_usage_uss = memory_info.uss
    shared_memory = memory_info.shared

    for child in proc.children(recursive=True):
        try:
            child_memory_info = child.memory_full_info()
            memory_usage_rss += child_memory_info.rss
            memory_usage_pss += child_memory_info.pss
            memory_usage_uss += child_memory_info.uss
            shared_memory += child_memory_info.shared
        except psutil.NoSuchProcess:
            continue

    process_resource_data = get_gpu_info()
    process_resource_data["cpu_usage"] = cpu_usage
    process_resource_data["memory_usage_rss"] = memory_usage_rss
    process_resource_data["memory_usage_pss"] = memory_usage_pss
    process_resource_data["memory_usage_uss"] = memory_usage_uss
    process_resource_data["shared_memory"] = shared_memory
    process_resource_data["timestamp"] = str(datetime.now())

    return process_resource_data


def start_and_monitor(
    command: str,
    interval: float = 1.0,
    max_duration: float = inf,
    storing_interval: int = 10,
    log_location: Path | None = None,
    log_cpu_usage: bool = False,
) -> None:
    """Start and monitor a process.

    Args:
        command: The command to run.
        interval: Interval between checks in seconds.
        max_duration: Maximum duration to run in seconds.
        storing_interval: Interval between storing data in seconds.
        log_location: Location to store the CSV file.
        log_cpu_usage: Whether to log CPU usage.
    """
    check_nvidia_smi()

    process = start_process(command)
    pid = process.pid

    storage_data = []
    try:
        start_time = time.time()
        time_since_last_csv_update = 0
        while time.time() - start_time < max_duration and process.is_running():
            if psutil.pid_exists(pid) and process.status() != psutil.STATUS_ZOMBIE:
                proc = psutil.Process(pid)
                process_resource_data = collect_process_data(proc, log_cpu_usage)
                storage_data.append(process_resource_data)

                time_since_last_csv_update += interval
                if time_since_last_csv_update >= storing_interval:
                    store_dicts_as_csv(storage_data, log_location)
                    time_since_last_csv_update = 0

                time.sleep(interval)
            else:
                logger.debug("Process has terminated.")
                break
    except KeyboardInterrupt:
        logger.debug("Monitoring stopped.")
    finally:
        store_dicts_as_csv(storage_data, log_location)
        logger.debug("Terminating the process.")

        for child in process.children(recursive=True):
            child.kill()
        process.kill()
        process.wait()
        logger.debug("Process terminated.")

    return process.returncode
