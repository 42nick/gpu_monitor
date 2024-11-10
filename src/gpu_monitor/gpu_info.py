import csv
import subprocess
from typing import Any, TypedDict


def get_gpu_info() -> list[dict[str, Any]]:
    try:
        # Run the nvidia-smi command and get the output
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,timestamp,name,memory.total,memory.used,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Parse the output
        gpu_info_dict = {}
        for line in result.stdout.strip().split("\n"):
            index, timestamp, name, memory_total, memory_used, utilization_gpu = line.split(", ")
            gpu_info_dict[f"gpu_{index}_timestamp"] = timestamp
            gpu_info_dict[f"gpu_{index}_name"] = name
            gpu_info_dict[f"gpu_{index}_memory_total"] = int(memory_total)
            gpu_info_dict[f"gpu_{index}_memory_used"] = int(memory_used)
            gpu_info_dict[f"gpu_{index}_utilization_gpu"] = int(utilization_gpu)

        return gpu_info_dict

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


class GPUInfoLogger:
    def __init__(self):
        self.gpu_info_list = []

    def store_gpu_info(self):
        gpu_info = get_gpu_info()
        self.gpu_info_list.append(gpu_info)

    def log_csv(self, filename: str):
        with open(filename, "w", newline="") as csvfile:
            fieldnames = ["index", "timestamp", "name", "memory_total", "memory_used", "utilization_gpu"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for gpu_info in self.gpu_info_list:
                for info in gpu_info:
                    writer.writerow(info)


# Example usage
if __name__ == "__main__":
    gpu_logger = GPUInfoLogger()
    gpu_logger.store_gpu_info()
    gpu_logger.store_gpu_info()
    gpu_logger.store_gpu_info()

    gpu_logger.log_csv("gpu_info.csv")

    print(gpu_logger.gpu_info_list)
