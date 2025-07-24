#!/usr/bin/env python
"""
Script to flush all questions from the database and reload from questions.json
"""
from app import app, db
from models import Question
import json

def reload_questions():
    with app.app_context():
        # Count questions before deletion
        count_before = Question.query.count()
        print(f"Questions before flush: {count_before}")
        
        # Delete all existing questions
        Question.query.delete()
        db.session.commit()
        
        print("All questions have been deleted from the database.")
        
        # Reload from questions.json
        try:
            with open("questions.json", "r", encoding="utf-8") as f:
                questions_data = json.load(f)
            
            count = 0
            for q_data in questions_data:
                question = Question(
                    question_text=q_data["question"],
                    option_a=q_data["options"]["a"],
                    option_b=q_data["options"]["b"],
                    option_c=q_data["options"]["c"],
                    option_d="",  # Adding empty option_d since it's required
                    correct_answer=q_data["correct_answer"],
                    # Add category and difficulty if they exist in the JSON
                    category=q_data.get("category", None),
                    difficulty=None,
                )
                db.session.add(question)
                count += 1
            
            db.session.commit()
            print(f"Questions loaded successfully! Added {count} new questions.")
            
            # Verify the reload
            count_after = Question.query.count()
            print(f"Questions after reload: {count_after}")
            
        except FileNotFoundError:
            print("ERROR: questions.json file not found.")
        except Exception as e:
            print(f"Error loading questions: {e}")
            db.session.rollback()

if __name__ == "__main__":
    reload_questions()
