from app import app, db, Question

with app.app_context():
    question_count = Question.query.count()
    print(f"Total questions in database: {question_count}")
    
    if question_count > 0:
        # Print a few questions as sample
        questions = Question.query.limit(3).all()
        print("\nSample questions:")
        for i, q in enumerate(questions):
            print(f"{i+1}. {q.question_text}")
    else:
        print("No questions found in the database!")
