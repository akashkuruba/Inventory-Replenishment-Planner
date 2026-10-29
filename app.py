import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__)

# On hosts such as Embarko, DATA_DIR is the persistent storage location.
# Locally, the database stays in this project folder.
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(DATA_DIR, exist_ok=True)
DATABASE = os.path.join(DATA_DIR, "inventory.db")


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def setup_database():
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            reorder_level INTEGER NOT NULL DEFAULT 10,
            daily_demand INTEGER NOT NULL DEFAULT 1,
            lead_time INTEGER NOT NULL DEFAULT 3
        )
    """)
    connection.commit()
    connection.close()


def parse_product_form():
    name = request.form.get("name", "").strip()
    try:
        quantity = int(request.form.get("quantity", "0"))
        reorder_level = int(request.form.get("reorder_level", "10"))
        daily_demand = int(request.form.get("daily_demand", "1"))
        lead_time = int(request.form.get("lead_time", "3"))
    except ValueError:
        raise ValueError("Please enter valid whole numbers.")

    if not name:
        raise ValueError("Please enter a product name.")
    if min(quantity, reorder_level, daily_demand, lead_time) < 0:
        raise ValueError("Numbers cannot be negative.")

    return name, quantity, reorder_level, daily_demand, lead_time


@app.route("/")
def home():
    connection = get_db_connection()
    total_products = connection.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]
    low_stock = connection.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= reorder_level"
    ).fetchone()[0]
    total_units = connection.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM products"
    ).fetchone()[0]
    products = connection.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()
    connection.close()

    return render_template(
        "index.html",
        total_products=total_products,
        low_stock=low_stock,
        total_units=total_units,
        products=products
    )


@app.route("/add", methods=["POST"])
def add_product():
    try:
        values = parse_product_form()
    except ValueError as error:
        return str(error), 400

    connection = get_db_connection()
    connection.execute("""
        INSERT INTO products
        (name, quantity, reorder_level, daily_demand, lead_time)
        VALUES (?, ?, ?, ?, ?)
    """, values)
    connection.commit()
    connection.close()
    return redirect(url_for("home"))


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    connection = get_db_connection()
    connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    connection.close()
    return redirect(url_for("home"))


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    connection = get_db_connection()
    product = connection.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if product is None:
        connection.close()
        abort(404, description="Product not found.")

    if request.method == "POST":
        try:
            values = parse_product_form()
        except ValueError as error:
            connection.close()
            return str(error), 400

        connection.execute("""
            UPDATE products
            SET name = ?, quantity = ?, reorder_level = ?,
                daily_demand = ?, lead_time = ?
            WHERE id = ?
        """, (*values, product_id))
        connection.commit()
        connection.close()
        return redirect(url_for("home"))

    connection.close()
    return render_template("edit.html", product=product)


# Create the database automatically when the app starts.
setup_database()

if __name__ == "__main__":
    # Works locally and on hosts that supply PORT.
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
