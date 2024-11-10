import csv


def store_dicts_as_csv(data: list[dict], filename: str):
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
