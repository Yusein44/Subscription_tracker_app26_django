# Subscription Tracker - Django Web App

Subscription Tracker is a custom web application built with Python and Django. It is designed to help users efficiently track personal subscriptions, monitor recurring expenses, and manage their monthly budget.

## Getting Started

To get a local copy up and running, follow these simple steps. The project runs entirely on a Django server.

### Prerequisites & Installation

1. Clone the repository:
`git clone https://github.com/Yusein44/Subscription_tracker_app26_django.git`

2. Navigate to the project directory:
`cd Subscription_tracker_app26_django`

3. Create and activate a virtual environment:
`python -m venv venv`

4. Install the required dependencies:
`pip install -r requirements.txt`
*(If no requirements.txt is provided, simply run: pip install django)*

5. Apply database migrations to set up the database:
`python manage.py migrate`

6. Start the development server:
`python manage.py runserver`

7. Open the link shown in the terminal (usually http://127.0.0.1:8000/).

---

## Technologies Used

* **Framework:** Django (Python)
* **Architecture:** MVT (Model-View-Template)
* **Database:** SQLite (Default)
* **Frontend:** HTML5, CSS (Django Templates)
* **Authentication:** Django Built-in Authentication System

---

## Features

* **User Authentication:** Secure login, registration, and session management.
* **Subscription Management:** Full CRUD operations allowing users to add, read, update, and delete their subscription records (e.g., Netflix, Spotify, Gym).
* **Expense Calculation:** Automated calculation of total monthly and annual recurring costs based on active subscriptions.
* **Dashboard Overview:** A centralized view displaying all active services and total spending at a glance.
* **Personalized Tracking:** Each user has a private dashboard and can only see and manage their own data.

---

## Project Architecture

The project follows the standard Django MVT architecture:

* `models.py`: Custom data models defining the database schema for Users and Subscriptions.
* `views.py`: Business logic for processing requests, calculating expenses, and returning templates.
* `urls.py`: URL routing configuration mapping web addresses to specific views.
* `templates/`: HTML files utilizing Django Template Language (DTL) for dynamic data rendering.
* `admin.py`: Configuration for the built-in Django Admin interface to manage records easily.

---

## Security & Validation

* **CSRF Protection:** Implemented in all forms to prevent Cross-Site Request Forgery.
* **Route Guards:** `@login_required` decorators ensure that unauthorized users cannot access the dashboard or manage subscriptions.
* **Owner Validation:** Database queries are filtered so users can exclusively access their own records.
* **Form Validation:** Ensures required fields (like subscription name and price) are filled correctly before saving to the database.
