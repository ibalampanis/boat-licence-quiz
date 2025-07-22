from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_superuser = db.Column(db.Boolean, default=False)

    # Relationships
    quiz_attempts = db.relationship(
        "QuizAttempt", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_statistics(self):
        attempts = self.quiz_attempts
        if not attempts:
            return {
                "total_quizzes": 0,
                "average_score": 0,
                "best_score": 0,
                "total_questions_answered": 0,
                "correct_answers": 0,
                "accuracy_percentage": 0,
            }

        total_quizzes = len(attempts)
        scores = [attempt.score for attempt in attempts]
        total_correct = sum(attempt.correct_answers for attempt in attempts)
        total_questions = sum(attempt.total_questions for attempt in attempts)

        return {
            "total_quizzes": total_quizzes,
            "average_score": round(sum(scores) / total_quizzes, 2),
            "best_score": max(scores),
            "total_questions_answered": total_questions,
            "correct_answers": total_correct,
            "accuracy_percentage": round((total_correct / total_questions * 100), 2)
            if total_questions > 0
            else 0,
        }


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'a', 'b', 'c', or 'd'
    category = db.Column(db.String(100))
    difficulty = db.Column(db.String(20), default="medium")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "question_text": self.question_text,
            "options": {
                "a": self.option_a,
                "b": self.option_b,
                "c": self.option_c,
            },
            "correct_answer": self.correct_answer,
        }


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    questions_data = db.Column(db.Text, nullable=False)  # JSON string of questions
    user_answers = db.Column(db.Text)  # JSON string of user answers
    score = db.Column(db.Float, nullable=False, default=0)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False, default=20)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)

    def get_questions(self):
        return json.loads(self.questions_data) if self.questions_data else []

    def set_questions(self, questions_list):
        self.questions_data = json.dumps(questions_list)

    def get_user_answers(self):
        return json.loads(self.user_answers) if self.user_answers else {}

    def set_user_answers(self, answers_dict):
        self.user_answers = json.dumps(answers_dict)

    def calculate_score(self):
        questions = self.get_questions()
        answers = self.get_user_answers()
        correct = 0

        for question in questions:
            question_id = str(question["id"])
            if (
                question_id in answers
                and answers[question_id] == question["correct_answer"]
            ):
                correct += 1

        self.correct_answers = correct
        self.total_questions = len(questions)
        self.score = round((correct / len(questions)) * 100, 2) if questions else 0
        return self.score
