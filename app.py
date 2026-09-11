from flask import Flask, render_template, request, redirect, session
from config import Config
from models import db, User, Trek, Booking
from auth import admin_required, staff_required, user_required
from datetime import datetime, date

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# Check current login session
@app.route("/check")
def check():

    user_id = session.get("user_id")
    role = session.get("role")

    return f"User ID = {user_id}<br>Role = {role}"


# Logout the current user
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# Redirect home page to login
@app.route("/")
def home():

    return redirect("/login")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            if user.status == "blacklisted":

                return render_template(
                    "message.html",
                    title="Access Denied",
                    message="Your account has been blacklisted.",
                    back_url="/login"
                )

            session["user_id"] = user.id
            session["role"] = user.role

            if user.role == "admin":

                return redirect("/admin/dashboard")

            elif user.role == "staff":

                if user.status == "approved":

                    return redirect("/staff/dashboard")

                return render_template(
                    "message.html",
                    title="Waiting For Approval",
                    message="Your account is waiting for admin approval.",
                    back_url="/login"
                )

            return redirect("/user/dashboard")

        return render_template(
            "message.html",
            title="Login Failed",
            message="Invalid Email or Password.",
            back_url="/login"
        )

    return render_template("login.html")


# Register a new user
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            return render_template(
                "message.html",
                title="Registration Failed",
                message="Email already exists.",
                back_url="/register"
            )

        if role == "staff":
            status = "pending"
        else:
            status = "active"

        new_user = User(
            name=name,
            email=email,
            password=password,
            role=role,
            status=status
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# Create default admin account
@app.route("/create_admin")
def create_admin():

    admin = User.query.filter_by(
        email="admin@gmail.com"
    ).first()

    if admin:
        return "Admin Already Exists"

    admin = User(
        name="Admin",
        email="admin@gmail.com",
        password="admin123",
        role="admin",
        status="approved"
    )

    db.session.add(admin)
    db.session.commit()

    return "Admin Created"

# Admin dashboard
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    total_treks = Trek.query.count()

    total_users = User.query.filter_by(
        role="user"
    ).count()

    total_staff = User.query.filter_by(
        role="staff"
    ).count()

    pending_staff = User.query.filter_by(
        role="staff",
        status="pending"
    ).count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin/dashboard.html",
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        pending_staff=pending_staff,
        total_bookings=total_bookings
    )


# Add a new trek
@app.route("/admin/add_trek", methods=["GET", "POST"])
@admin_required
def add_trek():

    if request.method == "POST":

        name = request.form["name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        slots = request.form["slots"]

        start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()

        description = request.form["description"]
        staff_id = request.form["staff_id"]

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=slots,
            start_date=start_date,
            end_date=end_date,
            description=description,
            status="Open",
            staff_id=staff_id
        )

        db.session.add(trek)
        db.session.commit()

        return redirect("/admin/treks")

    staffs = User.query.filter_by(
        role="staff",
        status="approved"
    ).all()

    return render_template(
        "admin/add_trek.html",
        staffs=staffs
    )


# View all treks
@app.route("/admin/treks")
@admin_required
def admin_treks():

    search = request.args.get("search", "")

    treks = Trek.query

    if search:

        if search.isdigit():

            treks = treks.filter(
                Trek.id == int(search)
            )

        else:

            treks = treks.filter(
                Trek.name.contains(search)
            )

    treks = treks.all()

    # Store number of bookings for each trek
    booking_counts = {}

    for trek in treks:

        booking_counts[trek.id] = Booking.query.filter_by(
            trek_id=trek.id
        ).count()

    return render_template(
        "admin/treks.html",
        treks=treks,
        booking_counts=booking_counts,
        search=search
    )

# Edit trek details
@app.route("/admin/edit_trek/<int:id>", methods=["GET", "POST"])
@admin_required
def edit_trek(id):

    trek = Trek.query.get(id)

    staffs = User.query.filter_by(
        role="staff",
        status="approved"
    ).all()

    if request.method == "POST":

        trek.name = request.form["name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = request.form["duration"]
        trek.available_slots = request.form["slots"]

        trek.start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()

        trek.end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()

        trek.description = request.form["description"]
        trek.staff_id = request.form["staff_id"]
        trek.status = request.form["status"]

        db.session.commit()

        return redirect("/admin/treks")

    return render_template(
        "admin/edit_trek.html",
        trek=trek,
        staffs=staffs
    )


# Delete a trek
@app.route("/admin/delete_trek/<int:id>")
@admin_required
def delete_trek(id):

    trek = Trek.query.get(id)

    db.session.delete(trek)
    db.session.commit()

    return redirect("/admin/treks")


# View all users and staff
# View all users and search by name or ID
@app.route("/admin/users")
@admin_required
def admin_users():

    search = request.args.get("search", "")

    users = User.query

    if search:

        if search.isdigit():

            users = users.filter(
                User.id == int(search)
            )

        else:

            users = users.filter(
                User.name.contains(search)
            )

    users = users.all()

    return render_template(
        "admin/users.html",
        users=users,
        search=search
    )


# Approve a staff member
@app.route("/admin/approve_staff/<int:id>")
@admin_required
def approve_staff(id):

    staff = User.query.get(id)

    staff.status = "approved"

    db.session.commit()

    return redirect("/admin/users")


# Blacklist a user or staff member
@app.route("/admin/blacklist/<int:id>")
@admin_required
def blacklist(id):

    user = User.query.get(id)

    user.status = "blacklisted"

    db.session.commit()

    return redirect("/admin/users")

# Staff dashboard
@app.route("/staff/dashboard")
@staff_required
def staff_dashboard():

    staff_id = session["user_id"]

    treks = Trek.query.filter_by(
        staff_id=staff_id
    ).all()

    total_treks = len(treks)

    open_treks = Trek.query.filter_by(
        staff_id=staff_id,
        status="Open"
    ).count()

    completed_treks = Trek.query.filter_by(
        staff_id=staff_id,
        status="Completed"
    ).count()

    participants = Booking.query.join(Trek).filter(
        Trek.staff_id == staff_id
    ).count()
    
    return render_template(
    "staff/dashboard.html",
    treks=treks,
    total_treks=total_treks,
    open_treks=open_treks,
    completed_treks=completed_treks,
    participants=participants
    )


# View users registered for a trek
@app.route("/staff/users/<int:id>")
@staff_required
def staff_users(id):

    trek = Trek.query.get_or_404(id)

    # Prevent staff from viewing other staff's treks
    if trek.staff_id != session["user_id"]:
        return "Access Denied"

    bookings = Booking.query.filter_by(
        trek_id=id
    ).all()

    return render_template(
        "staff/users.html",
        bookings=bookings,
        trek=trek
    )


# Update assigned trek
@app.route("/staff/edit_trek/<int:id>", methods=["GET", "POST"])
@staff_required
def staff_edit_trek(id):

    trek = Trek.query.get_or_404(id)

    # Prevent staff from editing other staff's treks
    if trek.staff_id != session["user_id"]:
        return "Access Denied"

    if request.method == "POST":

        trek.available_slots = request.form["slots"]
        trek.status = request.form["status"]

        db.session.commit()

        return redirect("/staff/dashboard")

    return render_template(
        "staff/edit_trek.html",
        trek=trek
    )


# Update staff profile
@app.route("/staff/profile", methods=["GET", "POST"])
@staff_required
def staff_profile():

    staff = User.query.get(session["user_id"])

    if request.method == "POST":

        staff.name = request.form["name"]
        staff.email = request.form["email"]
        staff.password = request.form["password"]

        db.session.commit()

        return redirect("/staff/dashboard")

    return render_template(
        "staff/profile.html",
        user=staff
    )
    
    # User dashboard
@app.route("/user/dashboard")
@user_required
def user_dashboard():

    search = request.args.get("search", "")
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")

    treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.available_slots > 0
    )

    if search:

        treks = treks.filter(
            Trek.name.contains(search)
        )

    if difficulty:

        treks = treks.filter_by(
            difficulty=difficulty
        )

    if location:

        treks = treks.filter_by(
            location=location
        )

    treks = treks.all()
    
    bookings = Booking.query.filter_by(
    user_id=session["user_id"]
    ).all()

    booked_trek_ids = {booking.trek_id for booking in bookings}

    total_bookings = len(bookings)

    completed_treks = Booking.query.filter_by(
        user_id=session["user_id"],
        status="Completed"
    ).count()

    return render_template(
    "user/dashboard.html",
    treks=treks,
    booked_trek_ids=booked_trek_ids,
    search=search,
    difficulty=difficulty,
    location=location,
    total_bookings=total_bookings,
    completed_treks=completed_treks
    )


# Book a trek
@app.route("/user/book/<int:id>")
@user_required
def book_trek(id):

    trek = Trek.query.get_or_404(id)

    if trek.status != "Open":
        return "Booking is closed for this trek."

    if trek.available_slots <= 0:
        return "No slots available."

    already_booked = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=id
    ).first()

    already_booked = Booking.query.filter_by(
    user_id=session["user_id"],
    trek_id=id
    ).first()

    if already_booked:
        return "You have already booked this trek."

    booking = Booking(
        user_id=session["user_id"],
        trek_id=id,
        booking_date=date.today(),
        status="Booked",
        payment_status="Paid"
    )

    trek.available_slots -= 1

    if trek.available_slots == 0:
        trek.status = "Closed"

    db.session.add(booking)
    db.session.commit()

    return redirect("/user/bookings")


# View all bookings
@app.route("/user/bookings")
@user_required
def user_bookings():

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "user/bookings.html",
        bookings=bookings
    )


# View completed treks
@app.route("/user/history")
@user_required
def user_history():

    history = Booking.query.filter_by(
        user_id=session["user_id"],
        status="Completed"
    ).all()

    return render_template(
        "user/history.html",
        history=history
    )


# Update user profile
@app.route("/user/profile", methods=["GET", "POST"])
@user_required
def user_profile():

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]
        user.password = request.form["password"]

        db.session.commit()

        return redirect("/user/dashboard")

    return render_template(
        "user/profile.html",
        user=user
    )
    
    # View all booking records
@app.route("/admin/bookings")
@admin_required
def admin_bookings():

    bookings = Booking.query.all()

    return render_template(
        "admin/bookings.html",
        bookings=bookings
    )


# Mark a booking as completed
@app.route("/admin/complete_booking/<int:id>")
@admin_required
def complete_booking(id):

    booking = Booking.query.get_or_404(id)

    booking.status = "Completed"

    db.session.commit()

    return redirect("/admin/bookings")


# Cancel a booking from admin side
@app.route("/admin/cancel_booking/<int:id>")
@admin_required
def cancel_booking(id):

    booking = Booking.query.get_or_404(id)

    if booking.status != "Cancelled":

        booking.status = "Cancelled"
        booking.payment_status = "Refunded"

        trek = Trek.query.get(booking.trek_id)

        trek.available_slots += 1

        if trek.status == "Closed":
            trek.status = "Open"

        db.session.commit()

    return redirect("/admin/bookings")


# User can cancel their own booking
@app.route("/user/cancel_booking/<int:id>")
@user_required
def user_cancel_booking(id):

    booking = Booking.query.get_or_404(id)

    if booking.user_id != session["user_id"]:
        return "Access Denied"

    if booking.status == "Cancelled":
        return redirect("/user/bookings")

    booking.status = "Cancelled"
    booking.payment_status = "Refunded"

    trek = Trek.query.get(booking.trek_id)

    trek.available_slots += 1

    if trek.status == "Closed":
        trek.status = "Open"

    db.session.commit()

    return redirect("/user/bookings")


# Update trek status automatically
@app.route("/update_trek_status")
@admin_required
def update_trek_status():

    today = date.today()

    treks = Trek.query.all()

    for trek in treks:

        if trek.end_date and trek.end_date < today:
            trek.status = "Completed"

    db.session.commit()

    return redirect("/admin/dashboard")


# Start the Flask application
if __name__ == "__main__":

    app.run(debug=True)