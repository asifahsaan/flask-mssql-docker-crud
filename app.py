from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = "supersecretkey"  # TODO: move to .env for production

# Connection details
server = "192.168.0.102" #192.168.100.22       # or host.docker.internal if inside Docker
database = "test"
username = "flask_user"
password = "123"
driver = "{ODBC Driver 17 for SQL Server}"  # use 17 if 18 not installed

connection_string = (
    f"DRIVER={driver};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};PWD={password};"
    f"Encrypt=no;"
)


def get_connection():
    return pyodbc.connect(connection_string)


@app.route("/")
def home():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM flask_demo ORDER BY id DESC;")
    rows = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return render_template("index.html", rows=rows)


@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO flask_demo (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    flash("✅ Record added successfully!")
    return redirect(url_for("home"))


@app.route("/update", methods=["POST"])
def update():
    id = request.form["id"]
    name = request.form["name"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE flask_demo SET name=? WHERE id=?", (name, id))
    conn.commit()
    conn.close()
    flash("✏️ Record updated successfully!")
    return redirect(url_for("home"))


@app.route("/delete", methods=["POST"])
def delete():
    id = request.form["id"]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM flask_demo WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Record deleted successfully!")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
