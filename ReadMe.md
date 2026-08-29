# D-Med Tracker 💊

A medication tracking web application built with FastAPI and PostgreSQL that helps users manage their medications, track daily intake, maintain medication streaks, and receive automated email reminders.

## Why I Built This

I wanted to stop building projects simply because they were common backend exercises and instead build something around a real problem.

After getting sick and needing to take prescribed medication, I realized that I often lose track of when I need to take my medication and how many days I have been taking it.

That led me to build D-Med Tracker.

The idea is simple: users can record their medication, dosage, start date, and treatment duration. The application then tracks their daily intake, calculates their medication streak, monitors their progress, and sends reminders to help them stay consistent.

## Features

- 🔐 JWT-based user authentication
- 👤 User registration and login
- 💊 Create, view, update, and delete medications
- 📅 Track daily medication intake (taken, missed, skipped)
- 🚫 Prevent duplicate medication logs for the same day
- 🔥 Track medication streaks
- 📊 Track: current streak, longest streak, total taken, total missed, total skipped, completion percentage
- 📋 View today's medication logs
- 📖 View medication log history
- 🔄 Update medication status (active, completed, abandoned)
- ⏰ Automated medication reminders with 2-minute detection window
- 🛡️ Duplicate email prevention via `last_reminder_sent` tracking
- 📧 Welcome emails on registration
- 📧 Medication reminder emails
- 📧 Medication completion emails
- 🎨 Color-coded log buttons (green = taken, red = missed, yellow = skipped)
- 📝 Medication descriptions visible on the medications page
- 🛡️ Security headers middleware
- 🌐 CORS configuration
- 🗄️ PostgreSQL database with cascade deletion on foreign keys
- 🧩 SQLAlchemy ORM
- ✅ Pydantic validation
- 🌐 Deployed on Railway

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
| Gmail SMTP (smtplib) | Email notifications (original implementation) |
| Brevo (Sendinblue) | Email notifications (current — migrated for better deliverability) |
| Railway | Deployment and hosting |
| Python | Backend language |

## How It Works

1. A user creates an account and receives a welcome email.
2. The user's password is securely hashed before being stored.
3. The user logs in and receives a JWT access token.
4. The authenticated user adds their medication and treatment duration.
5. The system calculates the medication's end date.
6. The user records whether they took, missed, or skipped their medication.
7. The system updates their medication streak and completion percentage.
8. APScheduler runs background jobs every minute to check for medication reminders.
9. Email reminders are sent when the scheduled time is reached.
10. APScheduler checks daily at midnight for medications that have reached their end date, marks them as completed, and sends a completion email.

## Streak System

The streak system tracks medication consistency.

When a user logs an intake as:

- **Taken** → current streak increases and total taken increases
- **Missed** → current streak resets and total missed increases
- **Skipped** → current streak resets and total skipped increases

The application also tracks the user's longest streak and calculates their overall medication completion percentage.

## Email System

### Email Providers Used

| Provider | Status | Notes |
|---|---|---|
| Gmail SMTP (smtplib) | Original | Worked but risky — Google can block automated sends |
| Resend | Attempted | Free tier only allows sending to your own email |
| Brevo (Sendinblue) | Current | 300 free emails/day, no domain verification required |

### Email Types

**Welcome Email** — Sent when a new user successfully registers.

**Medication Reminder** — The background scheduler checks active medications with reminders enabled and sends an email when the scheduled time is reached. A 2-minute detection window prevents missed reminders, and a `last_reminder_sent` database column prevents duplicate emails.

**Completion Email** — When a medication reaches its end date, the scheduler marks it as completed and sends the user a completion email.

## Background Scheduler

APScheduler handles automated tasks without requiring the user to manually trigger them.

| Job | Schedule | What It Does |
|---|---|---|
| Reminder check | Every 1 minute | Checks if any active medication's reminder time matches the current time (within 2-minute window) |
| Completion check | Daily at midnight | Marks medications past their end date as completed and sends completion emails |

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and receive JWT token | No |

### Medications

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/v1/medications/` | Create medication | Yes |
| GET | `/api/v1/medications/` | Get user's medications | Yes |
| GET | `/api/v1/medications/{med_id}` | Get medication by ID | Yes |
| PATCH | `/api/v1/medications/{med_id}` | Update medication | Yes |
| DELETE | `/api/v1/medications/{med_id}` | Delete medication | Yes |
| PATCH | `/api/v1/medications/{med_id}/status` | Update medication status | Yes |

### Medication Logs

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/api/v1/logs/` | Log medication intake | Yes |
| GET | `/api/v1/logs/today` | Get today's medication logs | Yes |
| GET | `/api/v1/logs/{med_id}` | Get medication history | Yes |

### Streaks

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| GET | `/api/v1/streaks/{med_id}` | Get medication streak statistics | Yes |

## Project Structure

medication_tracker/ 
      ├── main.py 
      ├── models.py 
      ├── schemas.py 
      ├── crud.py 
      ├── database.py 
      ├── enums.py 
      ├── requirements.txt 
      ├── core/ │ 
             ├── config.py │ ├── security.py │ └── dependencies.py │ 
      ├── routes/ │ ├── auth.py │ ├── medications.py │ ├── logs.py │ └── streaks.py │ 
      ├── service/ │ ├── email.py │ └── scheduler.py │ 
      ├── static/ │ ├── styles.css │ ├── api.js │ └── app.js 
      │ └── templates/ ├── index.html ├── login.html ├── dashboard.html ├── medications.html ├── medication_detail.html └── settings.html



## Development Decisions & Lessons Learned

| Problem | Solution |
|---|---|
| Gmail SMTP blocked by Google | Migrated to Brevo (300 free emails/day) |
| Resend free tier only sends to own email | Switched to Brevo which allows sending to any recipient |
| Reminder emails sent 3–4 times | Added `last_reminder_sent` DB column with 50-minute cooldown |
| Exact-minute matching missed reminders | Added 2-minute detection window |
| Delete medication crashed (IntegrityError) | Added `ON DELETE CASCADE` to foreign keys |
| Scheduler ran in UTC, reminders in WAT | Configured timezone-aware datetime handling with WAT offset |


