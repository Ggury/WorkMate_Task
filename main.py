import argparse
import sys

from tabulate import tabulate

import DataLoader
import Reports


def main():
    parser = argparse.ArgumentParser(description="Reports Generator")
    parser.add_argument("--files", nargs="+", required=True, help="Path to CSV files")
    report_choices = list(Reports.REPORTS_MAP.keys())
    parser.add_argument(
        "--report",
        type=str,
        choices=report_choices,
        required=True,
        help=f"Report Name. Allowed Reports: {', '.join(report_choices)}",
    )
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
