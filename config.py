import os


class Config:
    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "your-secret-key-here-change-in-production"
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///quiz_app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QUESTIONS_PER_QUIZ = 20
    QUIZ_TIME_MINUTES = 45  # Quiz time limit in minutes
    SUPERUSER_CODE = "fouskoto-admin-2025"  # Secret code to create superuser
