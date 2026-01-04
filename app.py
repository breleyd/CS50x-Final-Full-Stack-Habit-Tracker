import os
import getpass

import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from flask import render_template, request
from matplotlib.dates import DateFormatter

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# from helpers import
from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # CHATgpt - Asked how to dynamically return an error message upon invalid username/password input

        # Validate username and password
        if not username or not password:
            return jsonify({"success": False, "error": "Both fields are required."}), 400

        # Check if username and password match in the database
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not user or not check_password_hash(user[0]["hash"], password):
            return jsonify({"success": False, "error": "Incorrect username or password."}), 400

        # If successful, redirect
        session["user_id"] = user[0]["id"]
        # return jsonify({"success": True}), 200
        return jsonify({"success": True, "message": "Log in successful."}), 200

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username and password is NOT blank
        errors = []

        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")
        if password != confirmation:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Passwords need to be at least 8 characters long.")

        # If there are validation errors, return them immediately
        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        # Check if the username already exists
        user_exists = db.execute("SELECT * FROM users WHERE username = ?", username)
        if user_exists:
            errors.append("Username already exists.")
            return jsonify({"success": False, "errors": errors}), 400

        # Hash the password
        hash = generate_password_hash(password)

        # Register the new user
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # If registration is successful, redirect to login
        return jsonify({"success": True, "message": "Registration successful. You can now log in."}), 200
        # Don't use return redirect(/login)

    else:
        return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("habit_name")

        # Get the habit data for the specific user and habit name
        habits = db.execute("""
            SELECT timestamp, duration, habit_name
            FROM habits
            WHERE user_id = ? AND habit_name = ?
            ORDER BY timestamp
        """, user_id, name)

        # If no data exists for this habit
        if not habits:
            return render_template("graph.html", error="No data found for the selected habit.")

        # Extract data
        timestamps = [habit['timestamp'] for habit in habits]
        durations = [habit['duration'] for habit in habits]

        # CHATGPT - unsure of how to implement a plotted graph with data from a sqlite3 database

        # Convert the string 'timestamp' to datetime for plotting
        timestamps = [datetime.strptime(t, "%Y-%m-%d") for t in timestamps]

        # Get the minimum and maximum values for both axes
        min_timestamp = min(timestamps)
        max_timestamp = max(timestamps)
        min_duration = min(durations)
        max_duration = max(durations)

        # Create the graph
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, durations, marker='o', linestyle='-', color='r')
        plt.title(f"Duration of '{name}' Habit Over Time")
        plt.xlabel("Timestamp")
        plt.ylabel("Duration (minutes)")

        # Set axis limits dynamically
        plt.xlim(min_timestamp, max_timestamp)
        plt.ylim(min_duration, max_duration)

        # Set the format for the x-axis dates (DD/MM/YYYY)
        date_format = DateFormatter('%d/%m/%Y')
        plt.gca().xaxis.set_major_formatter(date_format)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        # Adjust layout to prevent the bottom from being cut off
        plt.tight_layout()

        # Convert the plot to a base64 string to embed in HTML
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

        # Render the graph in an HTML template
        return render_template("graph.html", plot_img=img_base64)

    else:
        # If no POST request, show the form and habits data
        habit = db.execute("SELECT name FROM habit WHERE user_id = ?", user_id)
        return render_template("index.html", habit=habit)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("habit_name")

        # Validate that habit_name is provided
        if not name:
            return jsonify({"success": False, "error": "Habit is required."}), 400

        # Insert the habit into the database
        try:
            db.execute("INSERT INTO habit (user_id, name) VALUES (?, ?)", user_id, name)
            return jsonify({"success": True, "message": "Habit added successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500  # Handle any database errors

    else:
        return render_template("add.html")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    user_id = session["user_id"]
    if request.method == "POST":
        name = request.form.get("habit_name")

        # Validate that habit_name is provided
        if not name:
            return jsonify({"success": False, "error": "Habit is required."}), 400

        # Insert the habit into the database
        try:
            db.execute("DELETE FROM habits WHERE habit_name = ?", name)
            db.execute("DELETE FROM habit WHERE name = ?", name)
            return jsonify({"success": True, "message": "Habit removed successfully."}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500  # Handle any database errors
    else:
        habit = db.execute("SELECT name FROM habit WHERE user_id = ?", user_id)
        return render_template("remove.html", habit=habit)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    user_id = session["user_id"]
    if request.method == "POST":
        # Collect form data
        name = request.form.get("habit_name")
        duration = request.form.get("duration")
        timestamp = request.form.get("timestamp")

        # Validate inputs (server-side)
        if not name or not duration or not timestamp:
            return jsonify({"success": False, "error": "All fields are required."}), 400

        # Convert timestamp to date (removing time part)
        timestamp_date = datetime.strptime(timestamp, "%Y-%m-%d").date()

        # Check if habit already exists on that day (ignoring the time part)
        timestamp_exists = db.execute("""
            SELECT timestamp
            FROM habits
            WHERE user_id = ? AND habit_name = ? AND DATE(timestamp) = ?
        """, user_id, name, timestamp_date)

        if timestamp_exists:
            return jsonify({"success": False, "error": "Habit already exists on that day."}), 400

        # Check if the duration is a positive number
        try:
            duration = float(duration)
            if duration < 0:
                return jsonify({"success": False, "error": "Duration must be a positive number."}), 400
        except ValueError:
            return jsonify({"success": False, "error": "Duration must be a valid number."}), 400

        # Proceed with adding the habit
        db.execute("""
            INSERT INTO habits (user_id, habit_name, duration, timestamp)
            VALUES (?, ?, ?, ?)
        """, user_id, name, duration, timestamp)

        return jsonify({"success": True, "message": "Habit added successfully."}), 200

    else:
        habit = db.execute("SELECT name FROM habit WHERE user_id = ?", user_id)
        return render_template("update.html", habit=habit)
