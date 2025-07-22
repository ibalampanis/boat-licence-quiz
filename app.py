from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
    abort,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from functools import wraps
from models import db, User, Question, QuizAttempt
from config import Config
import json
import random
from datetime import datetime
from werkzeug.security import generate_password_hash
import os
from flask import send_from_directory

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = (
    "Παρακαλώ συνδεθείτε για να έχετε πρόσβαση σε αυτή τη σελίδα."
)
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


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
        print("WARNING: questions.json file not found. Please create it with your questions.")
        # Check if there are any questions in the database already
        question_count = Question.query.count()
        if question_count > 0:
            print(f"Found {question_count} questions already in the database.")
        else:
            print("No questions found in database. Application may not function correctly.")
    except Exception as e:
        print(f"Error loading questions: {e}")


with app.app_context():
    db.create_all()
    load_questions_from_file()


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash("Το όνομα χρήστη υπάρχει ήδη", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Το email έχει ήδη εγγραφεί", "danger")
            return render_template("register.html")

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)

        # Check if superuser code was provided and is correct
        superuser_code = request.form.get("superuser_code", "")
        if superuser_code and superuser_code == app.config["SUPERUSER_CODE"]:
            user.is_superuser = True
            flash("Δημιουργήθηκε λογαριασμός διαχειριστή", "success")

        db.session.add(user)
        db.session.commit()

        flash("Η εγγραφή ολοκληρώθηκε με επιτυχία", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash("Μη έγκυρο όνομα χρήστη ή κωδικός πρόσβασης", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    stats = current_user.get_statistics()
    recent_attempts = (
        QuizAttempt.query.filter_by(user_id=current_user.id, is_completed=True)
        .order_by(QuizAttempt.completed_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html", stats=stats, recent_attempts=recent_attempts
    )


@app.route("/start_quiz")
@login_required
def start_quiz():
    # Get random 20 questions
    total_questions = Question.query.count()
    if total_questions < app.config["QUESTIONS_PER_QUIZ"]:
        flash(
            f"Δεν υπάρχουν αρκετές ερωτήσεις στη βάση δεδομένων. Χρειάζονται τουλάχιστον {app.config['QUESTIONS_PER_QUIZ']} ερωτήσεις.",
            "warning",
        )
        return redirect(url_for("dashboard"))

    # Get random questions
    questions = (
        Question.query.order_by(db.func.random())
        .limit(app.config["QUESTIONS_PER_QUIZ"])
        .all()
    )

    # Create quiz attempt
    quiz_attempt = QuizAttempt(user_id=current_user.id)
    quiz_attempt.set_questions([q.to_dict() for q in questions])
    db.session.add(quiz_attempt)
    db.session.commit()

    session["current_quiz_id"] = quiz_attempt.id
    return redirect(url_for("take_quiz"))


@app.route("/quiz")
@login_required
def take_quiz():
    quiz_id = session.get("current_quiz_id")
    if not quiz_id:
        return redirect(url_for("start_quiz"))

    quiz_attempt = QuizAttempt.query.get_or_404(quiz_id)
    if quiz_attempt.user_id != current_user.id:
        flash("Μη εξουσιοδοτημένη πρόσβαση στο κουίζ", "danger")
        return redirect(url_for("dashboard"))

    if quiz_attempt.is_completed:
        return redirect(url_for("quiz_results", quiz_id=quiz_id))

    questions = quiz_attempt.get_questions()
    user_answers = quiz_attempt.get_user_answers()

    return render_template(
        "quiz.html",
        questions=questions,
        user_answers=user_answers,
        quiz_id=quiz_id,
        quiz_time_minutes=app.config["QUIZ_TIME_MINUTES"],
    )


@app.route("/submit_answer", methods=["POST"])
@login_required
def submit_answer():
    quiz_id = request.json.get("quiz_id")
    question_id = request.json.get("question_id")
    answer = request.json.get("answer")

    quiz_attempt = QuizAttempt.query.get_or_404(quiz_id)
    if quiz_attempt.user_id != current_user.id:
        return jsonify({"success": False, "message": "Unauthorized"})

    user_answers = quiz_attempt.get_user_answers()
    user_answers[str(question_id)] = answer
    quiz_attempt.set_user_answers(user_answers)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/submit_quiz", methods=["POST"])
@login_required
def submit_quiz():
    quiz_id = request.json.get("quiz_id")
    quiz_attempt = QuizAttempt.query.get_or_404(quiz_id)

    if quiz_attempt.user_id != current_user.id:
        return jsonify({"success": False, "message": "Unauthorized"})

    # Calculate score and mark as completed
    quiz_attempt.calculate_score()
    quiz_attempt.is_completed = True
    quiz_attempt.completed_at = datetime.utcnow()
    db.session.commit()

    # Clear session
    session.pop("current_quiz_id", None)

    return jsonify(
        {"success": True, "redirect": url_for("quiz_results", quiz_id=quiz_id)}
    )


@app.route("/results/<int:quiz_id>")
@login_required
def quiz_results(quiz_id):
    quiz_attempt = QuizAttempt.query.get_or_404(quiz_id)
    if quiz_attempt.user_id != current_user.id:
        flash("Μη εξουσιοδοτημένη πρόσβαση", "danger")
        return redirect(url_for("dashboard"))

    if not quiz_attempt.is_completed:
        flash("Το κουίζ δεν έχει ολοκληρωθεί ακόμα", "warning")
        return redirect(url_for("take_quiz"))

    questions = quiz_attempt.get_questions()
    user_answers = quiz_attempt.get_user_answers()

    # Prepare detailed results
    detailed_results = []
    for question in questions:
        q_id = str(question["id"])
        user_answer = user_answers.get(q_id, "")
        is_correct = user_answer == question["correct_answer"]

        detailed_results.append(
            {
                "question": question,
                "user_answer": user_answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
            }
        )

    return render_template(
        "results.html", quiz_attempt=quiz_attempt, detailed_results=detailed_results
    )


@app.route("/statistics")
@login_required
def statistics():
    stats = current_user.get_statistics()
    all_attempts = (
        QuizAttempt.query.filter_by(user_id=current_user.id, is_completed=True)
        .order_by(QuizAttempt.completed_at.desc())
        .all()
    )

    # Prepare data for charts
    chart_data = {"dates": [], "scores": [], "categories": {}}

    for attempt in all_attempts[-10:]:  # Last 10 attempts for chart
        chart_data["dates"].append(attempt.completed_at.strftime("%Y-%m-%d"))
        chart_data["scores"].append(attempt.score)

    return render_template(
        "statistics.html", stats=stats, all_attempts=all_attempts, chart_data=chart_data
    )


@app.route("/reset_statistics", methods=["POST"])
@login_required
def reset_statistics():
    # Delete all quiz attempts for the current user
    QuizAttempt.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    flash("Τα στατιστικά σας μηδενίστηκαν με επιτυχία", "success")
    return redirect(url_for("statistics"))


def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superuser:
            flash("Πρόσβαση μόνο για διαχειριστές", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/admin")
@login_required
@superuser_required
def admin_panel():
    users = User.query.all()
    questions = Question.query.all()
    return render_template("admin.html", users=users, questions=questions)


@app.route("/admin/user/delete/<int:user_id>", methods=["POST"])
@login_required
@superuser_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent superuser from deleting themselves
    if user.id == current_user.id:
        flash("Δεν μπορείτε να διαγράψετε τον εαυτό σας", "danger")
        return redirect(url_for("admin_panel"))

    db.session.delete(user)
    db.session.commit()
    flash(f"Ο χρήστης {user.username} διαγράφηκε με επιτυχία", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/user/toggle_superuser/<int:user_id>", methods=["POST"])
@login_required
@superuser_required
def toggle_superuser(user_id):
    user = User.query.get_or_404(user_id)

    # Prevent superuser from removing their own privileges
    if user.id == current_user.id:
        flash(
            "Δεν μπορείτε να αφαιρέσετε τα δικαιώματα διαχειριστή από τον εαυτό σας",
            "danger",
        )
        return redirect(url_for("admin_panel"))

    user.is_superuser = not user.is_superuser
    db.session.commit()
    flash(
        f"Τα δικαιώματα του χρήστη {user.username} ενημερώθηκαν με επιτυχία", "success"
    )
    return redirect(url_for("admin_panel"))


@app.route("/admin/question/delete/<int:question_id>", methods=["POST"])
@login_required
@superuser_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Η ερώτηση διαγράφηκε με επιτυχία", "success")
    return redirect(url_for("admin_panel"))


@app.route("/admin/question/add", methods=["GET", "POST"])
@login_required
@superuser_required
def add_question():
    if request.method == "POST":
        question_text = request.form["question_text"]
        option_a = request.form["option_a"]
        option_b = request.form["option_b"]
        option_c = request.form["option_c"]
        correct_answer = request.form["correct_answer"]

        # Create new question
        question = Question(
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d="",  # Empty string for option_d
            correct_answer=correct_answer,
        )

        db.session.add(question)
        db.session.commit()
        flash("Η ερώτηση προστέθηκε με επιτυχία", "success")
        return redirect(url_for("admin_panel"))

    return render_template("add_question.html")


@app.route("/admin/question/edit/<int:question_id>", methods=["GET", "POST"])
@login_required
@superuser_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)

    if request.method == "POST":
        question.question_text = request.form["question_text"]
        question.option_a = request.form["option_a"]
        question.option_b = request.form["option_b"]
        question.option_c = request.form["option_c"]
        question.option_d = ""  # Empty string for option_d
        question.correct_answer = request.form["correct_answer"]

        db.session.commit()
        flash("Η ερώτηση ενημερώθηκε με επιτυχία", "success")
        return redirect(url_for("admin_panel"))

    return render_template("edit_question.html", question=question)


@app.route("/files")
@login_required
def list_files():
    """List all files in the files directory for download"""
    files_dir = os.path.join(os.getcwd(), "files")
    files = []
    
    # Ensure the directory exists
    if os.path.exists(files_dir) and os.path.isdir(files_dir):
        # Get all files (not directories) in the files folder
        files = [f for f in os.listdir(files_dir) if os.path.isfile(os.path.join(files_dir, f))]
    
    return render_template("files.html", files=files)

@app.route("/download/<filename>")
@login_required
def download_file(filename):
    """Download a file from the files directory"""
    return send_from_directory("files", filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6789)
