#!/usr/bin/env python3
import argparse
import csv
import json
import requests
from pathlib import Path
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Parse logs and API data into a structured CSV export.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-l", "--log",
        type=Path,
        required=True,
        help="Path to the log file (text or JSON lines)."
    )

    parser.add_argument(
        "-u", "--url",
        type=str,
        required=True,
        help="API endpoint returning JSON data."
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("output.csv"),
        help="Output CSV file path."
    )

    parser.add_argument(
        "--method",
        type=str,
        choices=["GET", "POST"],
        default="GET",
        help="HTTP method for API request."
    )

    parser.add_argument(
        "--params",
        type=json.loads,
        default={},
        help="Optional JSON string for query parameters or POST body."
    )

    parser.add_argument(
        "--delimiter",
        type=str,
        default=",",
        help="CSV delimiter character."
    )

    parser.add_argument(
        "--timestamp",
        action="store_true",
        help="Add timestamp column to output CSV."
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed output for debugging."
    )

    return parser.parse_args()


def read_logs(file_path):
    """Read log file (plain text or JSON lines)."""
    entries = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"log": line})
    return entries


def fetch_api_data(url, method, params, verbose=False):
    """Fetch data from API, supporting GET or POST with optional params."""
    if verbose:
        print(f"Requesting {method} {url} with params: {params}")

    if method == "GET":
        r = requests.get(url, params=params)
    else:
        r = requests.post(url, json=params)

    r.raise_for_status()
    return r.json()


def merge_data(logs, api_data, add_timestamp=False):
    """Merge log and API data into a unified list for CSV writing."""
    combined = []
    for i, log_entry in enumerate(logs):
        api_entry = api_data[i] if i < len(api_data) else {}
        merged = {**log_entry, **api_entry}
        if add_timestamp:
            merged["timestamp"] = datetime.now().isoformat()
        combined.append(merged)
    return combined


def write_csv(data, output_path, delimiter, verbose=False):
    """Write combined data to CSV."""
    if not data:
        raise ValueError("No data to write.")

    keys = sorted(set().union(*(d.keys() for d in data)))
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)

    if verbose:
        print(f"CSV successfully written to {output_path}")


def main():
    args = parse_args()

    if args.verbose:
        print(f"Reading logs from {args.log}")
    logs = read_logs(args.log)

    api_data = fetch_api_data(args.url, args.method, args.params, args.verbose)

    combined = merge_data(logs, api_data, args.timestamp)
    write_csv(combined, args.output, args.delimiter, args.verbose)


if __name__ == "__main__":
    main()
