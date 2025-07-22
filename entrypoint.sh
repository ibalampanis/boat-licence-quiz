#!/bin/bash

# Import questions into the database
python << EOF
from app import app, db, Question
from config import Config
import json

def load_questions_from_file():
    """Load questions from JSON file into database"""
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            questions_data = json.load(f)

        count = 0
        for q_data in questions_data:
            existing = Question.query.filter_by(
                question_text=q_data["question"]
            ).first()
            if not existing:
                question = Question(
                    question_text=q_data["question"],
                    option_a=q_data["options"]["a"],
                    option_b=q_data["options"]["b"],
                    option_c=q_data["options"]["c"],
                    option_d="", # Adding empty option_d since it's required
                    correct_answer=q_data["correct_answer"],
                )
                db.session.add(question)
                count += 1

        db.session.commit()
        print(f"Questions loaded successfully! Added {count} new questions.")
    except FileNotFoundError:
        print("WARNING: questions.json file not found.")
    except Exception as e:
        print(f"Error loading questions: {e}")

with app.app_context():
    db.create_all()
    question_count = Question.query.count()
    print(f"Current question count: {question_count}")
    
    if question_count == 0:
        load_questions_from_file()
        new_count = Question.query.count()
        print(f"After loading, question count: {new_count}")
EOF

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:6789 app:app
