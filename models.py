from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Movie(db.Model):
    __tablename__ = 'movies'
    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(50))
    release_year = db.Column(db.Integer)
    duration = db.Column(db.Integer)

class WatchSession(db.Model):
    __tablename__ = 'watch_sessions'
    session_id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), index=True)
    host_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), index=True)
    date = db.Column(db.String(20), index=True)       # e.g., '2026-03-20'
    time = db.Column(db.String(20))       # e.g., '18:00'
    location = db.Column(db.String(200))  # optional location

    movie = db.relationship('Movie')
    host = db.relationship('User')

    duration = db.Column(db.Integer)   # duration in minutes
    invited = db.Column(db.Integer)    # number of invited people
    accepted = db.Column(db.Integer)   # number of accepted invites
    attended = db.Column(db.Integer)

#class SessionParticipant(db.Model):
#    __tablename__ = 'session_participants'
#    session_id = db.Column(db.Integer, db.ForeignKey('watch_sessions.session_id'), primary_key=True)
#    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
#   status = db.Column(db.String(10))