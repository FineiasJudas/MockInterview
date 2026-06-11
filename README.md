# MockInterview

A web application for practicing technical interview questions through timed, category-based mock exams.

**Live demo:** https://mockinterview-et2i.onrender.com/


## Distinctiveness and Complexity

### Why MockInterview is Distinct

MockInterview is fundamentally different from all other projects in this course. It is not a social network, an e-commerce platform, an email client, a wiki, or a search engine. It is a technical interview preparation tool — a category of application that did not appear in any form throughout the CS50W curriculum.

The core purpose of the application is to help software developers prepare for technical job interviews by simulating the experience of answering timed questions under pressure. This concept, while familiar to anyone who has used platforms like LeetCode, HackerRank, or Pramp, introduces a completely different set of challenges from the projects covered in the course: timed sessions, per-question answer tracking, score calculation, historical performance tracking, and category-based statistical analysis.

The problem MockInterview solves is also contextually relevant. As a software engineering student completing CS50W, the ability to practice for technical interviews is a real and immediate need — not an abstract exercise. The application was designed with this audience in mind: developers who want to test their knowledge across multiple technology categories before stepping into an interview.

### Why MockInterview is Complex

The complexity of MockInterview goes well beyond a simple CRUD application. Several aspects of the system required careful design and non-trivial implementation:

**Exam generation logic:** When a user starts a new exam, the application does not simply retrieve questions in order. It filters questions by the selected categories, shuffles them randomly using Python's `random` module, and selects the requested number of questions. This means every exam is unique, even if the same categories are selected. The selected questions are stored as `ExamQuestion` objects linked to the exam, preserving the state of each question-answer pair independently.

**Flashcard-style interface with JavaScript:** The exam page does not display all questions at once. Instead, it presents one question at a time in a flashcard style, controlled entirely by JavaScript on the front-end. The user navigates forward and backward through the questions using Next and Previous buttons, and their selected answers are stored in hidden input fields. A progress bar updates dynamically to reflect how far along the user is. This required careful DOM manipulation and state management in JavaScript without any page reloads.

**Real-time countdown timer:** Each exam session includes a live timer that counts upward from zero, showing the elapsed time in MM:SS format. When the user submits the exam, the total duration in seconds is sent to the server along with the answers and stored in the database. This gives both the user and the system a record of how long each exam took.

**Asynchronous submission via fetch:** When the user clicks "Submit Exam", the application does not submit a traditional HTML form. Instead, it uses JavaScript's `fetch` API to send a POST request to a dedicated API endpoint (`/api/submit`) with the exam ID, all answers, and the elapsed time encoded as JSON. The server processes the submission, calculates the score, creates a `Result` object, marks the exam as completed, and returns a redirect URL. The JavaScript then redirects the user to the result page. This entire flow happens without a page reload.

**Score calculation and result storage:** The server-side submission logic iterates through every `ExamQuestion` associated with the exam, compares the submitted answer to the correct option stored in the `Question` model, marks each question as correct or incorrect, and calculates the final score percentage. All of this is stored persistently so the user can review their results at any time.

**Per-category statistics with Chart.js:** The Stats page aggregates the user's historical performance broken down by category. For each category, it calculates the total number of questions answered, the number of correct answers, and the percentage score. These statistics are passed to the template and rendered as a bar chart using Chart.js, giving the user a visual overview of which technology areas they are strongest and weakest in.

**Deployment on Render:** The application is deployed and accessible online at https://mockinterview-et2i.onrender.com/, which required configuring a production-ready environment including a `build.sh` script and a `requirements.txt` file.


## Files

### Root level

- **`manage.py`** — Django's command-line utility for administrative tasks.
- **`requirements.txt`** — List of Python dependencies required to run the application.
- **`build.sh`** — Shell script used by Render during deployment to install dependencies and run migrations.
- **`db.sqlite3`** — SQLite database file (used in development).

### `mockinterview/` (project configuration)

- **`settings.py`** — Django project settings, including installed apps, database configuration, static files, and the custom `AUTH_USER_MODEL`.
- **`urls.py`** — Root URL configuration that includes the `interviews` app URLs.
- **`wsgi.py`** — WSGI entry point for deployment.
- **`asgi.py`** — ASGI entry point for async deployment.

### `interviews/` (main application)

- **`models.py`** — Defines all database models: `User`, `Category`, `Question`, `Exam`, `ExamQuestion`, and `Result`.
- **`views.py`** — Contains all view functions: authentication (login, logout, register), exam creation, exam session, asynchronous exam submission, result display, history, and statistics.
- **`urls.py`** — URL routing for the interviews app, including the API endpoint for exam submission.
- **`admin.py`** — Registers all models with Django's admin interface, allowing administrators to manage users, categories, questions, exams, and results.
- **`apps.py`** — App configuration.

### `interviews/templates/interviews/`

- **`layout.html`** — Base template with navigation bar, Bootstrap CSS, and shared structure inherited by all other templates.
- **`index.html`** — Home page showing available categories and entry points for authenticated and unauthenticated users.
- **`login.html`** — Login form.
- **`register.html`** — Registration form.
- **`new_exam.html`** — Form where the user selects categories and the number of questions to generate a new exam.
- **`exam.html`** — The exam session page. Displays one question at a time in flashcard style with a live timer, progress bar, and Next/Previous navigation. Submits answers asynchronously via JavaScript fetch.
- **`result.html`** — Displays the exam result including score percentage, number of correct and incorrect answers, and a question-by-question review showing what the user answered and what the correct answer was.
- **`history.html`** — Table showing all completed exams for the current user, with date, categories, score, and time taken.
- **`stats.html`** — Per-category performance statistics displayed as a bar chart using Chart.js, plus a summary table.

### `interviews/static/interviews/`

- **`styles.css`** — Custom CSS for layout, card styling, progress bar, timer badge, and mobile responsiveness.


## How to Run

### Local development

1. Clone the repository:
```
git clone https://github.com/me50/FineiasJudas
cd MockInterview
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Apply migrations:
```
python manage.py migrate
```

4. Create a superuser to access the admin panel:
```
python manage.py createsuperuser
```

5. Run the development server:
```
python manage.py runserver
```

6. Visit `http://127.0.0.1:8000/` in your browser.

7. Go to `http://127.0.0.1:8000/admin/` to add categories and questions before starting an exam.

### Adding questions

Questions must be added through the Django admin interface at `/admin/`. For each question, provide:
- The category (e.g. Python, Django, JavaScript, SQL, HTML)
- The question text
- Four answer options (A, B, C, D)
- The correct option (a single letter: a, b, c, or d)
- Difficulty level (easy, medium, or hard)
- Optionally, an explanation shown after the exam

## Additional Information

- The application uses Django's built-in `AbstractUser` to extend the default user model. The `AUTH_USER_MODEL` setting in `settings.py` must be set to `'interviews.User'` for migrations to work correctly.
- The exam submission endpoint (`/api/submit`) expects a JSON body and is called exclusively via JavaScript fetch — it is not a standard form submission.
- The Stats page only shows categories for which the user has answered at least one question. Categories with no history are hidden.
- The application is mobile-responsive using Bootstrap 4's grid system and custom CSS media queries.
- Chart.js is loaded from a CDN on the Stats page only, to avoid loading it on every page.
