from flask import Flask
from flask import render_template,request,redirect,url_for,flash,session

from datetime import datetime

# Database and Models
from models.database import db
from models.student import Student
from models.teacher import Teacher
from models.classroom import Classroom
from models.assignment import Assignment

app = Flask(__name__)
app.secret_key = "WCEHACKATHON"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database


with app.app_context():
    db.init_app(app)
    # db.drop_all()
    # db.create_all()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return redirect(url_for("home"))
    email=request.form.get("email")
    password=request.form.get("password")

    user = GetUser(email)
    if isinstance(user, Student) or isinstance(user, Teacher) :
        if user.password == password:
            session["name"] = user.name
            session["email"] = user.email
            session["user_type"] = user.user_type

            flash(f"Login Successful !", "success")
            return redirect(url_for("home"))
        else:
            flash(f"Invalid Password !", "danger")
            return redirect(url_for("home"))

    else:
        return user

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="GET":
        return redirect(url_for("home"))

    email=request.form.get("email")
    user_type=request.form.get("user_type")
    name=request.form.get("name")
    password=request.form.get("password")
    verify_password=request.form.get("verify_password")

    user = GetUser(email)
    if isinstance(user, Student) or isinstance(user, Teacher) :
        flash(f"User with email {email} already exists!", "danger")
        return redirect(url_for("home"))
    else:
        if verify_password == password:
            if user_type =="student":
                user = Student(name,email,password)
            if user_type =="teacher":
                user = Teacher(name,email,password)
            db.session.add(user)
            db.session.commit()

            session["name"] = user.name
            session["email"] = user.email
            session["user_type"] = user.user_type

            flash("Registered successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash(f"Invalid Password !", "danger")
            return redirect(url_for("home"))


@app.route("/logout", methods=["GET", "POST"])
def logout():
    if request.method=="GET":
        return redirect(url_for("home"))

    del session["name"]
    del session["email"]
    del session["user_type"]

    flash(f"Logout Successful !", "success")
    return redirect(url_for("home"))

def AuthorizeUser(user_type=None):
    is_authorized = False

    if session.get("name") is not None and session.get("email") is not None:
        if user_type is None or session.get("user_type") == user_type:
            is_authorized = True

    return is_authorized

def GetUser(email):
    user = None
    user = Student.query.filter_by(email=email).first()

    if user:
        return user

    user = Teacher.query.filter_by(email=email).first()
    if user:
        return user

    flash(f"No such user with email {email}!", "danger")
    return redirect(url_for("home"))


# Classroom Management
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    is_authorized = AuthorizeUser("teacher")
    if is_authorized:
        user = GetUser(session["email"])
        classes = []
        for classroom in user.classrooms:
            print(classroom.name)
            classes.append({
                "name": classroom.name,
                "desc": classroom.description,
                "code": classroom.code,
                "assignment": None
            })

        return render_template("teacher_dashboard.html", classes=classes)

    is_authorized = AuthorizeUser("student")

    if is_authorized:
        user = GetUser(session["email"])
        if request.method == "POST":
            class_code = request.form.get("class_code")

            classroom = Classroom.query.filter_by(code=class_code).first()
            if classroom:
                if classroom not in user.classrooms:
                    user.classrooms.append(classroom)
                    db.session.add(user)
                    db.session.commit()

                    flash(f"Joined classroom successfully!", "success")

            else:
                flash(f"No classroom found with code {class_code}!", "danger")

        classes = []
        for classroom in user.classrooms:
            classes.append({
                "name": classroom.name,
                "desc": classroom.description,
                "code": classroom.code,
                "assignment": None
            })

        return render_template("student_dashboard.html", classes=classes)

    return flash(f"Please login first!", "danger")

@app.route("/classroom/create", methods=["GET", "POST"])
def ClassroomCreate():
    if request.method == "GET":
        return render_template("classroom_create.html")

    is_teacher = AuthorizeUser("teacher")
    if not is_teacher:
        flash(f"Permission denied!", "danger")
        return redirect(url_for("home"))

    name = request.form.get("class_name")
    description = request.form.get("class_desc")

    user = GetUser(session["email"])

    new_classroom = Classroom(name, description, teacher=user)
    db.session.add(new_classroom)
    db.session.commit()

    flash(f"Classroom {name} created successfully!", "success")

    return redirect(url_for("dashboard"))


@app.route("/classroom/<class_code>", methods=["GET"])
def ClassroomMain(class_code):
    is_authorized = AuthorizeUser()
    if not is_authorized:
        flash("Permission denied!", "danger")
        return redirect(url_for("home"))

    classroom = Classroom.query.filter_by(code=class_code).first()
    if not classroom:
        flash("Classroom does not exist!", "danger")
        return redirect(url_for("dashboard"))

    user = GetUser(session["email"])
    if classroom not in user.classrooms:
        flash("Permission denied to class!", "danger")
        return redirect(url_for("dashboard"))

    assignments = Assignment.query.filter_by().first()

    return render_template("classroom_main.html", classroom=classroom, assignments=classroom.assignments, current_time=datetime.now, strftime=lambda x: x.strftime("%a, %d %b %Y at %I:%M %p"))

@app.route("/classroom/<class_code>/assignment/create", methods=["GET", "POST"])
def AssignmentCreate(class_code):
    is_authorized = AuthorizeUser("teacher")
    if not is_authorized:
        flash("Permission denied!", "danger")
        return redirect(url_for("home"))

    if request.method == "GET":
        session["class_code"] = class_code
        return render_template("assignment_create.html")
    else:
        print(class_code)
        classroom = Classroom.query.filter_by(code=class_code).first()
        print(classroom)
        if not classroom:
            flash("Classroom does not exist!", "danger")
            return redirect(url_for("dashboard"))

        user = GetUser(session["email"])
        if classroom not in user.classrooms:
            flash("Permission denied!", "danger")
            return redirect(url_for("dashboard"))

        name = request.form.get("assignment_name")
        description = request.form.get("assignment_desc")
        input_format = request.form.get("assignment_input_format")
        output_format = request.form.get("assignment_output_format")

        input_cases = []
        for k in request.form.keys():
            if "assignment_input_case" in k:
                input_cases.append(request.form.get(k))
        input_cases = "----".join(str(x) for x in input_cases if x)

        output_cases = []
        for k in request.form.keys():
            if "assignment_output_case" in k:
                output_cases.append(request.form.get(k))
        output_cases = "----".join(str(x) for x in output_cases if x)

        constraints = request.form.get("assignment_constraints")
        deadline = request.form.get("assignment_deadline")

        new_assignment = Assignment(name, description, deadline, classroom)
        new_assignment.input_format = input_format
        new_assignment.output_format = output_format
        new_assignment.input_cases = input_cases
        new_assignment.output_cases = output_cases
        new_assignment.constraints = constraints


        db.session.add(new_assignment)
        db.session.commit()

        flash("Assignment created successfully!", "success")
        return redirect(f"/classroom/{class_code}")

@app.route("/assignment/<assignment_code>", methods=["GET", "POST"])
def AssignmentMain(assignment_code):
    is_authorized = AuthorizeUser()
    if not is_authorized:
        flash("Permission denied!", "danger")
        return redirect(url_for("home"))

    assignment = Assignment.query.filter_by(code=assignment_code).first()
    print(assignment)
    if not assignment:
        flash("Assignment not found!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "GET":
        return render_template("assignment_main.html", assignment=assignment, current_time=datetime.now, strftime=lambda x: x.strftime("%a, %d %b %Y at %I:%M %p"))


if __name__ == "__main__":
    app.run(debug=True)

