from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3




app = Flask(__name__)
app.secret_key = "secret123"


# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("database.db",)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])

@app.route("/index")
@app.route("/home")
def index():
    # If user already logged in, send them to dashboard
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        conn.close()

        valid = False
        if user:
            try:
                valid = check_password_hash(user["password"], password)
            except ValueError:
                # Handles invalid / old / corrupted hashes
                valid = False

        if valid:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            flash("Login successful", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")



# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("All fields are required", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        role = "employee"  # default role

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                (email, hashed_password, role)
            )
            conn.commit()
            conn.close()

            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] == "admin":
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("employee_dashboard"))


# ---------- EMPLOYEE DASHBOARD ----------
@app.route("/employee_dashboard")
def employee_dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()

    # Existing logs query (unchanged)
    logs = conn.execute(
        "SELECT * FROM work_logs WHERE user_id=? ORDER BY work_date DESC",
        (session["user_id"],)
    ).fetchall()

    # Total logs
    summary = conn.execute(
        "SELECT COUNT(*) as total_logs FROM work_logs WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    #  New: Approved logs count
    approved_logs = conn.execute(
        "SELECT COUNT(*) as count FROM work_logs WHERE user_id=? AND status='Approved'",
        (session["user_id"],)
    ).fetchone()["count"]

    #  New: Pending logs count
    pending_logs = conn.execute(
        "SELECT COUNT(*) as count FROM work_logs WHERE user_id=? AND status='Pending'",
        (session["user_id"],)
    ).fetchone()["count"]

    conn.close()

    return render_template(
        "employee_dashboard.html",
        logs=logs,
        total_logs=summary["total_logs"],
        approved_logs=approved_logs,
        pending_logs=pending_logs
    )


# ---------- ADD LOG ----------
@app.route("/add_log", methods=["GET", "POST"])
def add_log():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO work_logs (user_id, work_date, description, status) VALUES (?, ?, ?, 'Pending')",
            (
                session["user_id"],
                request.form.get("date"),
                request.form.get("description")
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("employee_dashboard"))

    return render_template("add_log.html")


# ---------- EDIT LOG ----------
@app.route("/edit_log/<int:id>", methods=["GET", "POST"])
def edit_log(id):
    conn = get_db()
    log = conn.execute(
        "SELECT * FROM work_logs WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":
        conn.execute(
            "UPDATE work_logs SET work_date=?, description=? WHERE id=?",
            (
                request.form.get("date"),
                request.form.get("description"),
                id
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for("employee_dashboard"))

    conn.close()
    return render_template("edit_log.html", log=log)


# ---------- DELETE LOG ----------
@app.route("/delete_log/<int:id>")
def delete_log(id):
    conn = get_db()
    conn.execute("DELETE FROM work_logs WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("employee_dashboard"))


# ---------- ADMIN DASHBOARD ----------
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    status = request.args.get("status", "Pending")

    conn = get_db()

    # Existing logs query (unchanged)
    logs = conn.execute("""
        SELECT work_logs.*, users.email
        FROM work_logs
        JOIN users ON work_logs.user_id = users.id
        WHERE work_logs.status=?
        ORDER BY work_date DESC
    """, (status,)).fetchall()

    #  New: Get approved logs count per employee
    chart_data = conn.execute("""
        SELECT users.email, COUNT(work_logs.id) as total
        FROM work_logs
        JOIN users ON work_logs.user_id = users.id
        WHERE work_logs.status = 'Approved'
        GROUP BY users.email
    """).fetchall()

    conn.close()

    # Convert to lists for Chart.js
    employee_names = [row["email"] for row in chart_data]
    approved_counts = [row["total"] for row in chart_data]

    return render_template(
        "admin_dashboard.html",
        logs=logs,
        status=status,
        
    )

# ---------- APPROVE ----------
@app.route("/approve/<int:id>")
def approve(id):
    conn = get_db()
    conn.execute(
        "UPDATE work_logs SET status='Approved' WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))


@app.route("/create_first_admin", methods=["GET", "POST"])
def create_first_admin():
    con = get_db()

    # Check if any admin already exists
    admin = con.execute(
        "SELECT id FROM users WHERE role='admin'"
    ).fetchone()

    if admin:
        con.close()
        return render_template(
            "create_admin.html",
            message="Admin already exists"
        )

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            con.close()
            return render_template(
                "create_admin.html",
                message="All fields are required"
            )

        try:
            con.execute(
                "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                (
                    email,
                    generate_password_hash(password),
                    "admin"
                )
            )
            con.commit()
            con.close()

            return render_template(
                "create_admin.html",
                message=f"Admin created successfully. Email: {email}"
            )

        except sqlite3.IntegrityError:
            con.close()
            return render_template(
                "create_admin.html",
                message="Email already exists"
            )

    con.close()
    return render_template("create_admin.html")


@app.route("/create_admin", methods=["GET", "POST"])
def create_admin():
    # Allow only admins
    if "user_id" not in session or session["role"] != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("All fields are required", "danger")
            return redirect(url_for("create_admin"))

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                (
                    email,
                    generate_password_hash(password),
                    "admin"
                )
            )
            conn.commit()
            conn.close()

            flash("New admin created successfully", "success")
            return redirect(url_for("admin_dashboard"))

        except sqlite3.IntegrityError:
            flash("Email already exists", "danger")
            return redirect(url_for("create_admin"))

    return render_template("create_admin.html")


if __name__ == "__main__":
    app.run(debug=True)


#mohammedsadhiq97@gmail.com 
#1212

#username: admin@example.com
#password: admin123
