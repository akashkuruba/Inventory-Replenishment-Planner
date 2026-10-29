# Inventory Replenishment Planner

A small Flask + SQLite inventory management app for a college mini-project.

## Features
- Dashboard totals for products, low-stock items, and total units
- Add, edit, and delete products
- Search by product name and filter by stock status
- Suggested reorder quantity calculation
- Server-side validation for non-negative whole numbers
- SQLite persistence

## Run locally
```bash
python -m pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000.

## Deployment notes
- The app reads `DATA_DIR` for the database location when provided by the hosting platform.
- It reads `PORT` for the port and binds to `0.0.0.0`.
- A WSGI host can run it with `gunicorn app:app`.
- Confirm the host's persistent storage configuration before deploying. The `inventory.db` file is intentionally not included in this ZIP; the app creates a new empty database on first startup.


## Render Deployment

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`

SQLite data may not persist across restarts on hosts with ephemeral storage unless persistent storage is configured.
