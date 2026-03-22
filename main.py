"""

Большое спасибо за интерес к нашей компании! К сожалению, сейчас мы не готовы пригласить вас на следующий этап. Ценим ваше внимание и будем рады взаимодействию в будущем.

Комментарий к ТЗ: В проекте есть readme,, файл с зависимостями. В проекте нет .gitignore,
 линтера или форматтера. вся функциональность в одном файле.
   Используется контекстный менеджер, что верно. Аннотации используются.
. Используется @pytest.fixture.
             Не используется @pytest.mark.parametrize. Есть серьёзные нарушения PEP-8.
"""

import argparse
import csv
from tabulate import tabulate
from statistics import median
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
from typing import List,Dict,TypedDict
import Reports
import DataLoader


def main():
    parser = argparse.ArgumentParser(description="Reports Generator")
    parser.add_argument('--files', nargs='+', required=True, help = 'Path to CSV files')
    report_choices = list(Reports.REPORTS_MAP.keys())
    parser.add_argument('--report', type=str,choices=report_choices,
                        required=True, help = f"Report Name. Allowed Reports: {", ".join(report_choices)}")
    args = parser.parse_args()

    try:
        processor = DataLoader.DataProcessor(args.files)
        all_data = processor.loaddata()
    except Exception as err:
        print(f"Error loading file: {err}")
        sys.exit(0)
    if not all_data:
        print("Data is empty. Not found or files are empty")
        sys.exit(0)
    report_class = Reports.REPORTS_MAP[args.report]

    report_instance = report_class(all_data)

    try:
        report_body = report_instance.CreateReport()
        report_headers = report_instance.get_headers()
    except Exception as e:
        print(f"Generating report error: {args.report}: {e}", file=sys.stderr)
        return

    display_name = report_instance.REPORT_NAME

    print(f"\n Report: {display_name.upper()} ")

    print(tabulate(report_body, headers=report_headers, tablefmt="fancy_grid"))
    print("\n")

if __name__ == "__main__":
    main()