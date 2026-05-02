from app import app
from models import db, User, Movie

with app.app_context():
    # Add Users
    u1 = User(name="Alice Johnson", email="alice@example.com")
    u2 = User(name="Bob Smith", email="bob@example.com")
    u3 = User(name="Carol Lee", email="carol@example.com")
    db.session.add_all([u1, u2, u3])

    # Add Movies
    m1 = Movie(title="Inception", genre="Sci-Fi", release_year=2010, duration=148)
    m2 = Movie(title="The Lion King", genre="Animation", release_year=1994, duration=88)
    m3 = Movie(title="The Matrix", genre="Sci-Fi", release_year=1999, duration=136)
    db.session.add_all([m1, m2, m3])

    db.session.commit()
    print("Sample users and movies added!")