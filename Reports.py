import sys
from abc import ABC, abstractmethod
from statistics import median
from typing import Any, Dict, List, Type

from entities import Cell


class ReportBase(ABC):
    REPORT_NAME = "Base Report"
    HEADERS = ["student", "date"]

    def __init__(self, data: List[Cell]):
        self.data = data

    def get_headers(self):
        return self.HEADERS

    @abstractmethod
    def CreateReport():
        pass


class MedianCoffeeSpentReport(ReportBase):
    REPORT_NAME = "median-coffee"
    HEADERS = ["student", "median-coffee-spent"]

    def __init__(self, data: List[Cell]):
        super().__init__(data)
        self.arr_data: Dict[str, List[int]] = {}

    def CreateReport(self):
        for row in self.data:
            try:
                student = row.name
                coffee_spent = row.coffee_spent
                if student not in self.arr_data:
                    self.arr_data[student] = []
                self.arr_data[student].append(coffee_spent)
            except KeyError:
                print("KeyError", file=sys.stderr)
            except ValueError:
                print("ValueError", file=sys.stderr)
            except Exception as err:
                print(f"Error: {err}")
        report_data: List[Dict[str, Any]] = []
        for student, coffee_spent in self.arr_data.items():
            median_cs = median(coffee_spent)
            report_data.append({"student": student, "median-coffee-spent": median_cs})
        sorted_data = sorted(
            report_data, key=lambda x: x["median-coffee-spent"], reverse=True
        )
        return [
            [item["student"], round(item["median-coffee-spent"], 2)]
            for item in sorted_data
        ]


REPORTS_MAP: Dict[str, Type[ReportBase]] = {
    MedianCoffeeSpentReport.REPORT_NAME: MedianCoffeeSpentReport
}
