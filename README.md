# Boat Licence Quiz - Greek Speedboat License Quiz Application

This application is a multiple-choice quiz for individuals preparing for the Greek speedboat (boat) license exam.

## Features

- User registration and login
- Quiz execution with random questions
- Results viewing and statistics
- Statistics reset functionality
- Administrator features:
  - User management
  - Add, edit, and delete questions

## Running with Docker

### Prerequisites

- Docker and Docker Compose installed on your system

### Using the Management Script (deploy.sh)

The repository includes a comprehensive management script `scripts/deploy.sh` that offers complete application management:

```bash
# Show help
./deploy.sh help

# Deploy for production environment
./deploy.sh prod

# Deploy for development environment
./deploy.sh dev

# Stop production containers
./deploy.sh stop

# Stop development containers
./deploy.sh stop-dev

# Show container status
./deploy.sh status

# Create database backup
./deploy.sh backup

# Restore database backup
./deploy.sh restore

# Clean all project containers and images
./deploy.sh clean
```

### Manual Execution (Production)

1. Clone the repository
2. Build and start the containers:

```bash
docker-compose up -d
```

3. The application will be available at `http://localhost:5678`

4. To stop the application:

```bash
docker-compose down
```

### Manual Execution (Development)

For development environment with hot-reloading:

```bash
docker-compose -f docker-compose.dev.yml up
```

This will mount the local code to the container, allowing immediate updates when you make changes.

## Local Execution (without Docker)

1. Clone the repository
2. Create and activate a conda environment:

```bash
conda create -n boat-licence-env python=3.10
conda activate boat-licence-env
```

3. Install the required libraries:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

The application will be available at `http://localhost:5678`

## Creating Administrator Account

During registration, enter the administrator code defined in the `config.py` file.

## Updating Existing Database

If you already have an existing database and want to add the administrator functionality, run:

```bash
python scripts/migrate_add_superuser.py
```

## Project Structure

```
boat-licence-quiz/
├── app.py                          # Main Flask application with all routes and business logic
├── config.py                       # Configuration settings (database, quiz settings, admin code)
├── models.py                       # SQLAlchemy database models (User, Question, QuizAttempt)
├── requirements.txt                # Python dependencies
├── questions.json                  # Question database in JSON format (1800+ questions)
├── answers.json                    # Answer key for questions (validation purposes)
├── README.md                       # Project documentation
├── 
├── # Docker Configuration
├── Dockerfile                      # Production Docker image configuration
├── Dockerfile.dev                  # Development Docker image configuration  
├── docker-compose.yml              # Production Docker Compose configuration
├── docker-compose.dev.yml          # Development Docker Compose configuration
├── entrypoint.sh                   # Docker entrypoint script for database initialization
├── 
├── # Database & Backups
├── instance/
│   └── quiz_app.db                 # SQLite database file (created automatically)
├── backups/                        # Database backup directory
│   └── quiz_app_db_*.sqlite        # Timestamped database backups
├── 
├── # Scripts & Utilities
├── scripts/
│   ├── deploy.sh                   # Comprehensive deployment management script
│   ├── check_questions.py          # Script to validate questions in database
│   ├── reload_questions.py         # Script to reload questions from JSON to database
│   ├── flush_and_reload_questions.sh # Docker script to refresh questions
│   └── migrate_add_superuser.py    # Database migration for admin functionality
├── 
├── # Frontend Assets
├── static/
│   ├── css/
│   │   └── style.css               # Custom CSS styles for the application
│   └── js/
│       └── quiz.js                 # JavaScript for quiz functionality and interactions
├── 
├── # Templates (Greek Interface)
├── templates/
│   ├── base.html                   # Base template with navigation and layout
│   ├── login.html                  # User login page
│   ├── register.html               # User registration page
│   ├── dashboard.html              # Main dashboard after login
│   ├── quiz.html                   # Quiz interface with questions and timer
│   ├── results.html                # Quiz results and score display
│   ├── statistics.html             # User statistics and performance analytics
│   ├── admin.html                  # Admin panel for user and question management
│   ├── add_question.html           # Form to add new questions
│   ├── edit_question.html          # Form to edit existing questions
│   └── files.html                  # File management interface
├── 
├── # Documentation & Analysis
├── notebooks/
│   ├── check_questions.ipynb       # Jupyter notebook for question analysis
│   └── quiz_analysis.ipynb         # Jupyter notebook for quiz statistics analysis
├── 
└── # Resource Files
└── files/
    ├── corpus_&_questions.pdf      # Original question corpus documentation
    ├── questions_1.pdf             # First set of questions (PDF format)
    └── questions_2.pdf             # Second set of questions (PDF format)
```

## Key Components

### Core Application Files
- **`app.py`**: Main Flask application containing all routes, authentication, quiz logic, and admin functionality
- **`models.py`**: Database models defining User, Question, and QuizAttempt entities with relationships
- **`config.py`**: Configuration settings including database URL, quiz parameters (20 questions, 45-minute timer), and admin code

### Data Files
- **`questions.json`**: Contains 1800+ multiple-choice questions in Greek for the boat license exam
- **`answers.json`**: Answer key file for validation and cross-reference purposes
- **`instance/quiz_app.db`**: SQLite database storing users, questions, and quiz attempts

### Deployment & Management
- **`scripts/deploy.sh`**: Comprehensive management script supporting:
  - Production/development deployment
  - Container management (start/stop/status)
  - Database backup/restore functionality
  - System cleanup operations
- **Docker files**: Multi-environment containerization support
- **Migration scripts**: Database schema updates and data management

### Frontend Interface
- **Templates**: Complete Greek-language interface including:
  - User authentication (login/register)
  - Quiz interface with timer and progress tracking
  - Results display with detailed statistics
  - Admin panel for question and user management
- **Static assets**: Custom CSS and JavaScript for enhanced user experience

### Development Tools
- **Jupyter notebooks**: Data analysis tools for question validation and quiz statistics
- **Utility scripts**: Database maintenance and question management tools

## Technical Features

### Quiz System
- **Random Question Selection**: 20 questions randomly selected from 1800+ question pool
- **Timed Quizzes**: 45-minute time limit with JavaScript timer
- **Progress Tracking**: Real-time progress indicators and question navigation
- **Score Calculation**: Automatic scoring with detailed result breakdown
- **Statistics**: Comprehensive user performance analytics

### User Management
- **Authentication**: Secure login/registration system using Flask-Login
- **Role-based Access**: Regular users and administrators with different permissions
- **Statistics Tracking**: Individual user performance history and analytics

### Administration
- **Question Management**: Add, edit, delete questions through web interface
- **User Management**: Admin panel for user oversight
- **Database Operations**: Backup, restore, and maintenance capabilities

### Database Design
- **User Model**: Stores user credentials, preferences, and admin status
- **Question Model**: Stores questions with multiple-choice options and metadata
- **QuizAttempt Model**: Tracks quiz sessions, answers, scores, and timing

### Deployment Options
- **Docker Production**: Optimized container with Gunicorn WSGI server
- **Docker Development**: Hot-reload enabled development environment
- **Local Development**: Direct Python execution with Flask development server
- **Database Management**: Automated initialization and migration support

## Configuration

### Environment Variables
The application supports the following environment variables for configuration:

```bash
SECRET_KEY=your-production-secret-key-change-this    # Flask secret key for sessions
DATABASE_URL=sqlite:///quiz_app.db                   # Database connection string
FLASK_ENV=production                                 # Flask environment (production/development)
TZ=Europe/Athens                                     # Timezone for the application
```

### Application Settings
Key settings in `config.py`:

```python
QUESTIONS_PER_QUIZ = 20          # Number of questions per quiz session
QUIZ_TIME_MINUTES = 45           # Time limit for each quiz in minutes
SUPERUSER_CODE = "boat-licence-admin-2025"  # Admin registration code
```

## Security Considerations

- **Password Security**: Passwords are hashed using Werkzeug's secure password hashing
- **Session Management**: Flask-Login handles secure session management
- **Admin Access**: Admin functionality requires special registration code
- **Database**: SQLite database with proper foreign key constraints
- **Environment Variables**: Sensitive configuration stored in environment variables

## API Endpoints

The application provides several key endpoints:

- `GET /` - Dashboard/Home page
- `POST /login` - User authentication
- `POST /register` - User registration  
- `GET /quiz` - Start new quiz session
- `POST /submit_quiz` - Submit quiz answers
- `GET /results/<attempt_id>` - View quiz results
- `GET /statistics` - User performance statistics
- `GET /admin` - Admin panel (superuser only)
- `POST /admin/add_question` - Add new question (admin only)
- `POST /admin/edit_question/<id>` - Edit question (admin only)
- `DELETE /admin/delete_question/<id>` - Delete question (admin only)

## Database Schema

### User Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `created_at`
- `is_superuser` (Boolean)

### Question Table  
- `id` (Primary Key)
- `question_text`
- `option_a`, `option_b`, `option_c`, `option_d`
- `correct_answer` ('a', 'b', 'c', or 'd')
- `category`
- `difficulty`
- `created_at`

### QuizAttempt Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `questions_data` (JSON)
- `user_answers` (JSON)
- `score`, `correct_answers`, `total_questions`
- `started_at`, `completed_at`
- `is_completed`

## Troubleshooting

### Common Issues

**Database Issues:**
```bash
# Reset database
rm instance/quiz_app.db
python app.py  # Will recreate database

# Reload questions
python scripts/reload_questions.py
```

**Docker Issues:**
```bash
# Clean Docker environment
./scripts/deploy.sh clean

# Check container logs
docker-compose logs -f web
```

**Permission Issues:**
```bash
# Fix script permissions
chmod +x scripts/*.sh
chmod +x entrypoint.sh
```

### Development Tips

- Use `docker-compose -f docker-compose.dev.yml up` for development with hot-reload
- Check `instance/quiz_app.db` exists before running the app
- Verify `questions.json` format if questions aren't loading
- Admin code is defined in `config.py` - change for production use

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is under the MIT License.
