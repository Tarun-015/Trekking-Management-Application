# Trekking Management System

## Project Overview

The Trekking Management System is a role-based web application developed using Flask, Python, SQLite, SQLAlchemy, HTML, CSS, and Jinja2.

The system manages treks, trek staff, trekkers, bookings, trek availability, and booking history through separate roles and dashboards.

## Technologies Used

- Python
- Flask
- SQLAlchemy
- SQLite
- HTML
- CSS
- Jinja2
- Bootstrap

## User Roles

### Admin
- Manage treks
- Add, edit and delete treks
- Assign staff to treks
- Approve trek staff
- Manage users and staff
- Blacklist users
- View booking information
- Monitor overall system statistics

### Trek Staff
- Login after admin approval
- View assigned treks
- Manage available slots
- Update trek status
- View participants
- Manage assigned trek information
- Maintain staff profile

### Trekker/User
- Register and login
- View available treks
- Search and filter treks
- Book a trek
- View current bookings
- View booking history
- View profile
- Prevent duplicate bookings and overbooking

## Main Features

- User registration and login
- Role-based authentication
- Admin, Staff and User dashboards
- Trek CRUD operations
- Staff approval system
- Staff assignment to treks
- Trek search and difficulty filtering
- Trek slot management
- Open/Closed trek status
- Booking management
- Duplicate booking prevention
- Slot availability validation
- Booking history
- User blacklisting
- Booking and payment status tracking

## Database

The application uses SQLite with SQLAlchemy.

Main tables/models:

- `User`
- `Trek`
- `Booking`
- `Staff Profile`

Relationships are maintained between users, treks, staff and bookings.

## Project Structure

```text
Trekking-Management-Application/
│
├── app.py
├── config.py
├── models.py
├── auth.py
├── requirements.txt
│
├── instance/
│   └── trekking.db
│
├── templates/
│   ├── admin/
│   ├── staff/
│   └── user/
│
├── static/
│   └── css/
│       └── style.css
│
└── README.md
