// Additional JavaScript functionality for the quiz application

// Auto-save functionality
function autoSave() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', () => {
                localStorage.setItem(`quiz_${input.name}`, input.value);
            });
        });
    });
}

// Load saved data
function loadSavedData() {
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        const savedValue = localStorage.getItem(`quiz_${input.name}`);
        if (savedValue && input.type !== 'submit') {
            if (input.type === 'radio' || input.type === 'checkbox') {
                if (input.value === savedValue) {
                    input.checked = true;
                }
            } else {
                input.value = savedValue;
            }
        }
    });
}

// Clear saved data when quiz is submitted
function clearSavedData() {
    Object.keys(localStorage).forEach(key => {
        if (key.startsWith('quiz_')) {
            localStorage.removeItem(key);
        }
    });
}

// Timer functionality
function startTimer(duration, display) {
    let timer = duration, minutes, seconds;
    const interval = setInterval(() => {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        if (display) {
            display.textContent = minutes + ":" + seconds;
        }

        if (--timer < 0) {
            clearInterval(interval);
            // Auto-submit quiz when time runs out
            if (typeof submitQuiz === 'function') {
                alert('Ο χρόνος τελείωσε! Υποβολή του κουίζ...');
                submitQuiz();
            }
        }
    }, 1000);

    return interval;
}

// Keyboard navigation for quiz
document.addEventListener('keydown', function (e) {
    if (typeof currentQuestionIndex !== 'undefined') {
        switch (e.key) {
            case 'ArrowLeft':
                if (typeof previousQuestion === 'function') {
                    previousQuestion();
                }
                break;
            case 'ArrowRight':
                if (typeof nextQuestion === 'function') {
                    nextQuestion();
                }
                break;
            case '1':
            case '2':
            case '3':
            case '4':
                const optionMap = { '1': 'a', '2': 'b', '3': 'c', '4': 'd' };
                const currentCard = document.querySelector(`[data-question-index="${currentQuestionIndex}"]`);
                if (currentCard) {
                    const radio = currentCard.querySelector(`input[value="${optionMap[e.key]}"]`);
                    if (radio) {
                        radio.checked = true;
                        radio.dispatchEvent(new Event('change'));
                    }
                }
                break;
        }
    }
});

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    autoSave();
    loadSavedData();

    // Add timer if quiz page
    if (document.querySelector('.quiz-container')) {
        const timerDisplay = document.createElement('div');
        timerDisplay.className = 'timer-display text-center mb-3';

        // Use quizTimeMinutes from the template if available, fallback to 45 minutes
        const minutes = typeof quizTimeMinutes !== 'undefined' ? quizTimeMinutes : 45;

        timerDisplay.innerHTML = `<h5>Χρόνος που απομένει: <span id="timer">${minutes}:00</span></h5>`;
        document.querySelector('.quiz-container').prepend(timerDisplay);

        // Start timer
        startTimer(minutes * 60, document.getElementById('timer'));
    }

    // Clear saved data when quiz is submitted
    const submitButton = document.getElementById('submit-btn');
    if (submitButton) {
        submitButton.addEventListener('click', clearSavedData);
    }
});

// Smooth scrolling for navigation
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(toast);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}