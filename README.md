# Home Assistant Shelly Exporter

A Python script to export Shelly switch entities from Home Assistant to a CSV file.

## Features

- Fetches all entities from Home Assistant via the REST API.
- Filters for Shelly switch entities (excludes availability/connectivity sensors).
- Exports unique devices to a CSV file with `id` and `name`.
- Supports environment variables for secure configuration.

## Prerequisites

- Python 3.x
- Home Assistant instance accessible via network.
- Long-Lived Access Token from Home Assistant.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/arielna/ha-shelly-exporter.git
    cd ha-shelly-exporter
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   Windows: `.\.venv\Scripts\activate`
    *   Mac/Linux: `source .venv/bin/activate`

4.  **Install dependencies:**
    ```bash
    pip install requests python-dotenv
    ```

## Configuration

1.  Create a `.env` file in the project root:
    ```bash
    cp .env.example .env  # (If example exists, otherwise create new)
    ```

2.  Add your Home Assistant details to `.env`:
    ```makefile
    HA_URL=http://YOUR_HA_IP:8123
    HA_TOKEN=your_long_lived_access_token_here
    ```

## Usage

Run the script:

```bash
python ha-shelly-export.py
```

### Options

*   `--url`: Override HA URL (defaults to `HA_URL` in env).
*   `--token`: Override Access Token (defaults to `HA_TOKEN` in env).
*   `--output`: Specify a custom output CSV filename (default: auto-generated with timestamp).

```bash
python ha-shelly-export.py --output my-export.csv
```
