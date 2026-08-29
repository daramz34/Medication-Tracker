# D-Med Tracker 💊

A medication tracking REST API built with FastAPI and PostgreSQL that helps users manage their medications, track daily intake, maintain medication streaks, and receive automated email reminders.

## Why I Built This

I wanted to stop building projects simply because they were common backend exercises and instead build something around a real problem.

After getting sick and needing to take prescribed medication, I realized that I often lose track of when I need to take my medication and how many days I have been taking it.

That led me to build **D-Med Tracker**.

The idea is simple: users can record their medication, dosage, start date, and treatment duration. The application then tracks their daily intake, calculates their medication streak, monitors their progress, and sends reminders to help them stay consistent.

## Features

- 🔐 JWT-based user authentication
- 👤 User registration and login
- 💊 Create, view, update, and delete medications
- 📅 Track daily medication intake
- 🚫 Prevent duplicate medication logs for the same day
- 🔥 Track medication streaks
- 📊 Track:
  - Current streak
  - Longest streak
  - Total medications taken
  - Total missed doses
  - Total skipped doses
  - Completion percentage
- 📋 View today's medication logs
- 📖 View medication log history
- 🔄 Update medication status
- ⏰ Automated medication reminders
- 📧 Welcome emails when users register
- 📧 Medication completion emails
- ⚙️ Background scheduled tasks using APScheduler
- 🛡️ Security headers middleware
- 🌐 CORS configuration
- 🗄️ PostgreSQL database
- 🧩 SQLAlchemy ORM
- ✅ Pydantic validation

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | REST API framework |
| PostgreSQL | Database |
| SQLAlchemy | ORM |
| Pydantic | Data validation and serialization |
| JWT | Authentication |
| Bcrypt | Password hashing |
| APScheduler | Background scheduled tasks |
| SMTP / Gmail | Email notifications |
| Python | Backend language |

## How It Works

The basic flow of the application is:

1. A user creates an account.
2. The user's password is securely hashed before being stored.
3. The user logs in and receives a JWT access token.
4. The authenticated user adds their medication and treatment duration.
5. The system calculates the medication's end date.
6. The user records whether they took, missed, or skipped their medication.
7. The system updates their medication streak and completion percentage.
8. APScheduler runs background jobs to check for medication reminders and completed treatment courses.
9. Email notifications are sent when appropriate.

## Streak System

The streak system tracks medication consistency.

When a user logs an intake as:

- **Taken** → current streak increases and total taken increases.
- **Missed** → current streak resets and total missed increases.
- **Skipped** → current streak resets and total skipped increases.

The application also keeps track of the user's **longest streak** and calculates their overall medication completion percentage.

## API Endpoints

### Authentication

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and receive JWT token | No |

### Medications

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/api/v1/medications/` | Create medication | Yes |
| GET | `/api/v1/medications/` | Get user's medications | Yes |
| GET | `/api/v1/medications/{med_id}` | Get medication by ID | Yes |
| PATCH | `/api/v1/medications/{med_id}` | Update medication | Yes |
| DELETE | `/api/v1/medications/{med_id}` | Delete medication | Yes |
| PATCH | `/api/v1/medications/{med_id}/status` | Update medication status | Yes |

### Medication Logs

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| POST | `/api/v1/logs/` | Log medication intake | Yes |
| GET | `/api/v1/logs/today` | Get today's medication logs | Yes |
| GET | `/api/v1/logs/{med_id}` | Get medication history | Yes |

### Streaks

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/api/v1/streaks/{med_id}` | Get medication streak statistics | Yes |

## Automated Email System

The application uses SMTP to send several types of emails:

### Welcome Email

Sent when a new user successfully registers.

### Medication Reminder

The background scheduler checks active medications with reminders enabled and sends an email when the scheduled reminder hour is reached.

### Completion Email

When a medication reaches its end date, the scheduler marks it as completed and sends the user a completion email.

## Background Scheduler

APScheduler handles automated tasks without requiring the user to manually trigger them.

The application runs:

- A reminder check every hour.
- A medication completion check every day at midnight.

## Project Structure

```text
Medication_tracker/
├── main.py
├── models.py
├── schemas.py
├── crud.py
├── database.py
├── enums.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   └── dependencies.py
│
├── api/
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           ├── auth.py
│           ├── medications.py
│           ├── logs.py
│           └── streaks.py
│
└── service/
    ├── email.py
    └── scheduler.py