# HA-recovery-stats

Recover and fix Home Assistant energy statistics from an old database backup.

## Requirements

- Python 3.11+
- A Home Assistant instance with a Long-Lived Access Token

## Setup

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with your settings:
```
HA_URL=wss://your-ha-instance:8123/api/websocket
HA_TOKEN=your_long_lived_access_token_here
DRY_RUN=true
START_DATE=01/01/2024
END_DATE=31/12/2025
```

You can generate a Long-Lived Access Token from HA → Profile → Security.

## Step 1 — Extract from DB

In `app.py` on row 78, replace `database_path` with your db path:
```python
database_path = "/path/to/old_home-assistant_v2.db"
```

Insert the list of your energy metrics in `list.txt`:
```
sensor.consumption_43
sensor.consumption_45
sensor.consumption_47
sensor.consumption_38
...
```

Run the extraction script:
```shell
./script_01.sh
```
This will create a `.tsv` file for each metric under `stats/`.

## Step 2 — Merge files

```shell
./script_02.sh
```
This merges all `.tsv` files into a single `statisticdata.tsv`.

## Step 3 — Import

Copy `statisticdata.tsv` to your HA instance and import it using the integration.

## Step 4 — Fix negative deltas

After import, some statistics may have negative sum deltas. Use `fix_negatives.py` to detect and fix them.

First run in dry-run mode (`DRY_RUN=true` in `.env`) to see what would be fixed:
```shell
python fix_negatives.py
```

When you're happy with the output, set `DRY_RUN=false` in `.env` and run again to apply the fixes.

### .env parameters

| Parameter    | Description                                      | Default                                              |
|--------------|--------------------------------------------------|------------------------------------------------------|
| `HA_URL`     | WebSocket URL of your HA instance                | `ws://homeassistant.local:8123/api/websocket`        |
| `HA_TOKEN`   | Long-Lived Access Token                          | *(required)*                                         |
| `DRY_RUN`    | `true` to only show issues, `false` to fix them  | `true`                                               |
| `START_DATE` | Start of date range to check (dd/mm/yyyy)        | `01/01/1970`                                         |
| `END_DATE`   | End of date range to check (dd/mm/yyyy)          | `31/12/2099`                                         |
