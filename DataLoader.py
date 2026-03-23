import csv
import sys
from datetime import datetime
from typing import List

from entities import Cell

REQUIRED_HEADERS = {
    "student",
    "date",
    "coffee_spent",
    "sleep_hours",
    "study_hours",
    "mood",
    "exam",
}


class DataProcessor:
    def __init__(self, file_paths: List[str]):
        self.Data: List[Cell] = []
        self.filepaths = file_paths

    def _validate_headers(self, headers: List):
        file_header_set = set(headers)
        missing_headers = REQUIRED_HEADERS - file_header_set
        if missing_headers:
            print(
                f"File is missing required columns: {', '.join(missing_headers)}",
                file=sys.stderr,
            )

    def loaddata(self):
        for path in self.filepaths:
            try:
                with open(path, mode="r", newline="") as file:
                    csv_reader = csv.reader(file)
                    try:
                        headers = next(csv_reader)
                    except StopIteration:
                        print(f"Warning: File {path} is empty")
                        continue
                    self._validate_headers(headers=headers)
                    file.seek(0)
                    csv_file = csv.DictReader(file)
                    for row in csv_file:
                        try:
                            datetime.strptime(row["date"], "%Y-%m-%d")
                        except ValueError:
                            print("Warning: Wrong date format", file=sys.stderr)
                            continue
                        self.Data.append(
                            Cell(
                                row["student"],
                                datetime.strptime(row["date"], "%Y-%m-%d"),
                                int(row["coffee_spent"]),
                                float(row["sleep_hours"]),
                                float(row["study_hours"]),
                                row["mood"],
                                row["exam"],
                            )
                        )
            except FileNotFoundError:
                print("File Not Found")
                sys.exit(1)
            except Exception as err:
                print(f"Error reading file {path} : {err}")
        return self.Data
