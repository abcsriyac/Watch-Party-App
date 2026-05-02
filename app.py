# Connect to database
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from models import db, User, Movie, WatchSession
from datetime import datetime
from collections import Counter

import threading

session_lock = threading.Lock()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# =========================================================
# INDEX JUSTIFICATION (IMPORTANT FOR DEMO)
# =========================================================
# In models.py, the following indexes are assumed:
#
# 1. movie_id (INDEX)
#    -> Used in report filtering:
#       query.filter(WatchSession.movie_id == movie_id)
#    -> Supports:
#       • Filter sessions by movie (REPORT FEATURE)
#       • Sessions-per-movie aggregation
#
# 2. host_id (INDEX)
#    -> Used in report filtering:
#       query.filter(WatchSession.host_id == host_id)
#    -> Supports:
#       • Filter sessions by host (REPORT FEATURE)
#       • Sessions-per-host aggregation
#
# 3. date (INDEX)
#    -> Used in range queries:
#       query.filter(WatchSession.date >= start_date,
#                    WatchSession.date <= end_date)
#    -> Supports:
#       • Date range filtering in REPORT FEATURE
#
# 4. session_id (PRIMARY KEY - automatically indexed)
#    -> Used in:
#       • UPDATE session (/sessions/<id>)
#       • DELETE session (/sessions/<id>)
#    -> Ensures fast lookup for CRUD operations
#
# WHY THESE INDEXES:
# - These columns are heavily used in WHERE clauses
# - They support the most important feature: REPORTING
# - Improve performance by avoiding full table scans
# =========================================================


# -------------------------
# CREATE SESSION (CREATE)
# -------------------------
# No index needed here directly
# but inserts benefit from session_id primary key structure

@app.route('/sessions', methods=['POST'])
def add_session():
    data = request.json

    try:
        with db.session.begin():  
            session = WatchSession(
                movie_id=data['movie_id'],
                host_id=data['host_id'],
                date=data['date'],
                time=data['time'],
                location=data.get('location', '')
            )
            db.session.add(session)

        return jsonify({"message": "Session added"})

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Transaction failed"}), 500

#@app.route('/sessions', methods=['POST'])
#def add_session():
#    data = request.json
#    with session_lock:
##    session = WatchSession(
#        movie_id=data['movie_id'],
#        host_id=data['host_id'],
#        date=data['date'],
#        time=data['time'],
#        location=data.get('location', '')
#    )
#    db.session.add(session)
#    db.session.commit()
#    return jsonify({"message": "Session added"})


# -------------------------
# UPDATE SESSION (UPDATE)
# -------------------------
# Uses PRIMARY KEY index:
# session_id → fast lookup for update

@app.route('/sessions/<int:id>', methods=['PUT'])
def update_session(id):
    session = WatchSession.query.get(id)  # indexed via PK (session_id)
    data = request.json

    with session_lock:

        session.movie_id = data.get('movie_id', session.movie_id)
        session.host_id = data.get('host_id', session.host_id)
        session.date = data.get('date', session.date)
        session.time = data.get('time', session.time)
        session.location = data.get('location', session.location)

        db.session.commit()
        return jsonify({"message": "Updated"})


# -------------------------
# DELETE SESSION (DELETE)
# -------------------------
# Also uses PRIMARY KEY index (session_id)

@app.route('/sessions/<int:id>', methods=['DELETE'])
def delete_session(id):
    with session_lock:
        session = WatchSession.query.get(id)  # fast lookup via index
        db.session.delete(session)
        db.session.commit()
        return jsonify({"message": "Deleted"})


# =========================================================
# REPORT FEATURE (MOST IMPORTANT FOR INDEXES)
# =========================================================
# This is where MOST indexes are used

@app.route('/sessions/report', methods=['GET'])
def report():
    query = WatchSession.query

    # -----------------------------------------
    # INDEX USAGE: movie_id
    # Supports filtering sessions by movie
    # -----------------------------------------
    movie_id = request.args.get('movie_id')
    if movie_id:
        query = query.filter(WatchSession.movie_id == movie_id)
        # uses movie_id index → fast lookup instead of full scan

    # -----------------------------------------
    # INDEX USAGE: host_id
    # Supports filtering sessions by host
    # -----------------------------------------
    host_id = request.args.get('host_id')
    if host_id:
        query = query.filter(WatchSession.host_id == host_id)
        # uses host_id index

    # -----------------------------------------
    # INDEX USAGE: date index (range query)
    # Supports filtering sessions by date range
    # -----------------------------------------
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        query = query.filter(
            WatchSession.date >= start_date,
            WatchSession.date <= end_date
        )
        # uses date index for efficient range search

    sessions = query.all()

    result = []
    total_duration = 0

    for s in sessions:
        duration = s.movie.duration if s.movie and s.movie.duration else 0
        total_duration += duration

        result.append({
            "session_id": s.session_id,
            "movie": s.movie.title if s.movie else "Unknown",
            "host": s.host.name if s.host else "Unknown",
            "date": str(s.date),
            "time": str(s.time),
            "location": s.location,
            "duration": duration
        })

    total_sessions = len(sessions)

    stats = {
        "total_sessions": total_sessions,
        "filtered": True
    }

    if total_sessions > 0:
        stats.update({
            "average_duration": round(total_duration / total_sessions, 2),
            "sessions_per_movie": dict(Counter([s.movie.title for s in sessions if s.movie])),
            "sessions_per_host": dict(Counter([s.host.name for s in sessions if s.host]))
        })

    return jsonify({
        "sessions": result,
        "stats": stats
    })


# -------------------------
# GET ALL SESSIONS
# -------------------------
# No filter → full table scan (no index benefit here)
# acceptable because it's small dataset display

@app.route('/sessions', methods=['GET'])
def get_sessions():
    sessions = WatchSession.query.all()
    result = []

    for s in sessions:
        result.append({
            "session_id": s.session_id,
            "movie": s.movie.title if s.movie else "Unknown",
            "host": s.host.name if s.host else "Unknown",
            "date": str(s.date),
            "time": str(s.time),
            "location": s.location
        })

    return jsonify(result)


# -------------------------
# SUPPORTING TABLE: MOVIES
# -------------------------
# Small lookup table
# No index needed beyond primary key

@app.route('/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    return jsonify([{"movie_id": m.movie_id, "title": m.title} for m in movies])


# -------------------------
# SUPPORTING TABLE: USERS
# -------------------------
# Also small lookup table

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"user_id": u.user_id, "name": u.name} for u in users])


@app.route("/")
def home():
    return "Hello World! Flask is running:)"

if __name__ == "__main__":
    app.run(debug=True)