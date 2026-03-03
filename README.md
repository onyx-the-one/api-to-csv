# API Logger

## Overview
A lightweight Python tool that periodically requests data from an API endpoint and appends the results (with a timestamp) to a CSV log file.

## Features
- Periodic API polling (configurable interval)
- Supports `GET` and `POST` requests
- Automatically timestamps each entry
- Optionally flattens JSON objects into separate CSV columns
- Simple, argument-based configuration using `argparse`

## Requirements
- Python 3.8 or higher
- The `requests` library

Install dependency:
```bash
pip install requests
```

## Usage
Basic example (query API every 30 seconds and append to CSV):
```bash
python api_logger.py -u https://api.example.com/status -i 30 -o status_log.csv
```

## Command-line Options
| Option | Description | Default |
|---------|--------------|----------|
| `-u, --url` | API endpoint to query | *(required)* |
| `-i, --interval` | Time between requests in seconds | `60` |
| `-o, --output` | Output CSV file path | `api_log.csv` |
| `--method` | HTTP method (`GET` or `POST`) | `GET` |
| `--params` | JSON string of API parameters | `{}` |
| `--flatten` | Flatten top-level JSON keys into CSV columns | Disabled |
| `--verbose` | Enable detailed logging output | Disabled |

## Examples
### Log every 15 seconds
```bash
python api_logger.py -u https://api.coindesk.com/v1/bpi/currentprice.json -i 15
```

### Log with JSON parameters and flatten output
```bash
python api_logger.py -u https://api.example.com/data \
  --method POST --params '{"query":"value"}' --interval 20 --flatten
```

### Verbose real-time logging
```bash
python api_logger.py -u https://api.example.com/status --verbose
```
