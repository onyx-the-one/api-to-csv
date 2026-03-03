import argparse
import csv
import json
import time
import requests
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Periodically request data from an API and log results to a CSV file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-u", "--url", required=True, help="API endpoint URL to query.")
    parser.add_argument(
        "-i", "--interval", type=float, default=60,
        help="Time between requests in seconds."
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("api_log.csv"),
        help="Output CSV file."
    )
    parser.add_argument(
        "--method", choices=["GET", "POST"], default="GET",
        help="HTTP method for requests."
    )
    parser.add_argument(
        "--params", type=json.loads, default={},
        help="Optional JSON parameters for GET or POST requests."
    )
    parser.add_argument(
        "--flatten", action="store_true",
        help="Flatten top-level JSON keys into CSV columns (if dict)."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print debug output."
    )

    return parser.parse_args()


def fetch_data(url, method, params, verbose=False):
    """Send request and return JSON or text response."""
    try:
        if verbose:
            print(f"Requesting {method} {url} with {params}")
        if method == "GET":
            r = requests.get(url, params=params)
        else:
            r = requests.post(url, json=params)
        r.raise_for_status()

        try:
            return r.json()
        except json.JSONDecodeError:
            return {"response": r.text}
    except Exception as e:
        if verbose:
            print(f"Request failed: {e}")
        return {"error": str(e)}


def log_to_csv(output_path, data, flatten=False, verbose=False):
    """Append one row to CSV file."""
    timestamp = datetime.now().isoformat()

    if flatten and isinstance(data, dict):
        row = {"timestamp": timestamp, **data}
    else:
        row = {"timestamp": timestamp, "data": json.dumps(data, ensure_ascii=False)}

    file_exists = output_path.exists()

    with open(output_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    if verbose:
        print(f"[{timestamp}] Logged to {output_path}")


def main():
    args = parse_args()

    print(f"Starting API logger for {args.url}")
    print(f"Interval: {args.interval}s, output: {args.output}\n")

    while True:
        data = fetch_data(args.url, args.method, args.params, args.verbose)
        log_to_csv(args.output, data, args.flatten, args.verbose)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
