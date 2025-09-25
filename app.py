from flask import Flask, jsonify, request, redirect, url_for, render_template_string
import pyodbc
import os

app = Flask(__name__)

# Connection string (from env vars)
server = os.getenv("DB_SERVER", "localhost")
database = os.getenv("DB_NAME", "test")
username = os.getenv("DB_USER", "flask_user")
password = os.getenv("DB_PASSWORD", "123")
driver = "{ODBC Driver 18 for SQL Server}"
port = os.getenv("DB_PORT", "1433")

connection_string = (
    f"DRIVER={driver};"
    f"SERVER={server},{port};"
    f"DATABASE={database};"
    f"UID={username};PWD={password};"
    "Encrypt=no;"
)

# 🔹 Home page: View + Add + Update + Delete
@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    # Insert logic
    if request.method == "POST" and "name" in request.form:
        name = request.form.get("name")
        if name:
            try:
                conn = pyodbc.connect(connection_string)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO flask_demo (name) VALUES (?)", (name,))
                conn.commit()
                conn.close()
                message = f"Inserted: {name}"
            except Exception as e:
                message = f"Error: {str(e)}"

    # Fetch rows
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 50 * FROM flask_demo ORDER BY id DESC;")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        rows = []
        message = f"DB Error: {str(e)}"

    # HTML Template with CRUD buttons
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask + SQL Server Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            form { margin-bottom: 20px; }
            input[type=text] { padding: 5px; width: 250px; }
            button { padding: 5px 10px; margin-left: 5px; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background: #f2f2f2; }
            .msg { margin: 10px 0; color: green; }
            .error { margin: 10px 0; color: red; }
        </style>
    </head>
    <body>
        <h1>Flask + SQL Server Demo (CRUD)</h1>
        <form method="post">
            <input type="text" name="name" placeholder="Enter a name" required>
            <button type="submit">Add</button>
        </form>
        {% if message %}
            <div class="{{ 'error' if 'Error' in message else 'msg' }}">{{ message }}</div>
        {% endif %}
        <h2>Data from flask_demo</h2>
        <table>
            <tr><th>ID</th><th>Name</th><th>Created At</th><th>Actions</th></tr>
            {% for row in rows %}
                <tr>
                    <td>{{ row.id }}</td>
                    <td>{{ row.name }}</td>
                    <td>{{ row.created_at }}</td>
                    <td>
                        <form action="{{ url_for('update', row_id=row.id) }}" method="post" style="display:inline;">
                            <input type="text" name="new_name" placeholder="New name" required>
                            <button type="submit">Update</button>
                        </form>
                        <form action="{{ url_for('delete', row_id=row.id) }}" method="post" style="display:inline;">
                            <button type="submit" onclick="return confirm('Delete this row?');">Delete</button>
                        </form>
                    </td>
                </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html, rows=rows, message=message)

# 🔹 Delete route
@app.route("/delete/<int:row_id>", methods=["POST"])
def delete(row_id):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM flask_demo WHERE id = ?", (row_id,))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    except Exception as e:
        return f"Error deleting row {row_id}: {e}"

# 🔹 Update route
@app.route("/update/<int:row_id>", methods=["POST"])
def update(row_id):
    new_name = request.form.get("new_name")
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("UPDATE flask_demo SET name = ? WHERE id = ?", (new_name, row_id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    except Exception as e:
        return f"Error updating row {row_id}: {e}"

# 🔹 JSON API routes still available
@app.route("/data")
def get_data():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 50 * FROM flask_demo ORDER BY id DESC;")
        rows = cursor.fetchall()
        result = [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        conn.close()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/add/<name>")
def add_data(name):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flask_demo (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "inserted": name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
