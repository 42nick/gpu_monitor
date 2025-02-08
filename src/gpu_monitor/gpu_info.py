"""Functions to get GPU information using the nvidia-smi command."""

import subprocess
from typing import Any


def get_gpu_info() -> list[dict[str, Any]]:
    """Get the GPU information using the nvidia-smi command.

    Returns:
        A list of dictionaries containing GPU information like e.g. index, name, memory used and utilization of the gpu.
    """
    try:
        # Run the nvidia-smi command and get the output
        result = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "nvidia-smi",
                "--query-gpu=index,timestamp,name,memory.total,memory.used,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Parse the output
        gpu_info_dict = {}
        for line in result.stdout.strip().split("\n"):
            index, timestamp, name, memory_total, memory_used, utilization_gpu = line.split(", ")
            gpu_info_dict[f"gpu_{index}_timestamp"] = timestamp
            gpu_info_dict[f"gpu_{index}_name"] = name
            gpu_info_dict[f"gpu_{index}_memory_total"] = int(memory_total)
            gpu_info_dict[f"gpu_{index}_memory_used"] = int(memory_used)
            try:
                gpu_info_dict[f"gpu_{index}_utilization_gpu"] = int(utilization_gpu)
            except ValueError:
                gpu_info_dict[f"gpu_{index}_utilization_gpu"] = utilization_gpu
    except FileNotFoundError:
        print("nvidia-smi command not found.")
        return {}
    except subprocess.CalledProcessError as cpe:
        print(f"CalledProcessError occurred: {cpe}")
        return {}

    return gpu_info_dict
