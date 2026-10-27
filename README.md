# Apex Exam Portal

A web-based online examination platform built with **Django** and **MySQL**. Teachers create and publish MCQ exams, students sit timed tests, and results are graded automatically.

> **Status:** Work in progress (MVP under active development).

---

## Features

### Implemented
- **Role-based authentication**: login/logout with redirect to a dashboard based on role (Admin, Teacher, Student)
- **Admin-only account creation**: no public sign-up
- **Custom user model** with password validation and inactive-account rejection
- **Reusable access control**: one role-check mixin applied to every protected view
- **Teacher exam management**: create, edit, delete and list exams
- **Question management**: multiple-choice questions with options
- **Publish / unpublish** exams
- **Bootstrap-styled UI** with separate teacher and student dashboards

### Planned
- Timed exam participation for students
- Automatic grading
- Results and score history
- Admin dashboard

---

## Tech Stack

| Layer      | Technology                      |
|------------|---------------------------------|
| Backend    | Python, Django                  |
| Database   | MySQL                           |
| Frontend   | Django templates + Bootstrap    |
| Versioning | Git & GitHub                    |

---

## Project Structure

```
apex-exam-portal/
├── config/          # Project settings, URLs, WSGI/ASGI
├── accounts/        # Custom User model, login/logout, role permissions
├── exams/           # Exams, questions, options, teacher views
├── templates/       # Base template and page templates
├── manage.py
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- MySQL Server 8+
- Git

### 1. Clone the repository
```bash
git clone https://github.com/naywin-thukha/apex-exam-portal.git
cd apex-exam-portal
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up the database
Log in to MySQL and run:
```sql
CREATE DATABASE apex_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'apex_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON apex_db.* TO 'apex_user'@'localhost';
FLUSH PRIVILEGES;
```

Then update the `DATABASES` section in `config/settings.py` with your credentials.

### 5. Apply migrations
```bash
python manage.py migrate
```

### 6. Create an admin account
```bash
python manage.py createsuperuser
```

### 7. Run the server
```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ and log in.

---

## Usage

1. Log in as **Admin** and create Teacher and Student accounts.
2. Log in as a **Teacher** to create an exam, add questions with options, and publish it.
3. Students log in to see their dashboard and available exams.

---

## Running Tests

```bash
python manage.py test
```

---

## Roles

| Role    | Can do                                                        |
|---------|---------------------------------------------------------------|
| Admin   | Create and manage user accounts                               |
| Teacher | Create, edit, delete, publish exams and questions             |
| Student | View dashboard, take published exams (in progress)            |

---

## Roadmap

- [x] Environment, Django and MySQL setup
- [x] Custom user model and exam models
- [x] Authentication and role-based access
- [x] Base UI and dashboards
- [x] Teacher exam and question management
- [ ] Student exam participation (timed)
- [ ] Auto-grading and results
- [ ] Admin dashboard
- [ ] Deployment for exam day

---

## Author

**Nay Win Thukha**: [@naywin-thukha](https://github.com/naywin-thukha)
