from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean, DateTime, and_, select
from sqlalchemy.exc import IntegrityError
import os
from dotenv import load_dotenv
from forms import ImageUploadForm, NewPasswordForm, Registration, Login, AddTask, CompleteTaskForm, ResetPassword
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired 
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import uuid
import time
import logging



app = Flask(__name__)
load_dotenv()

#! Image upload in DB
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'profile_pics')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



logging.basicConfig(
    filename='app.log',          
    level=logging.INFO,           
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # Date/time format
)


# #! .env Infomation
MY_EMAIL = os.getenv('MY_EMAIL')

#! Secret Key
app.config["SECRET_KEY"] = os.getenv("FLASK_KEY")

#!!!
def generate_serializer():
    return URLSafeTimedSerializer(app.config["SECRET_KEY"])


#! Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

#! Redirects to login page with a flash
@login_manager.unauthorized_handler
def unauthorized_callback():
    flash("Please log in to access that page.", "warning")
    return redirect(url_for('login') + '?next=' + request.path)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


#! My Database 
class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI", "sqlite:///todo.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    date_joined: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    profile_pic: Mapped[str] = mapped_column(String(250), nullable=True)
    tasks_added: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tasks = relationship("Task", back_populates="user")


class Task(db.Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="tasks")

    task: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


with app.app_context():
    db.create_all()

#! Mail Scheduler
class Config:
    SCHEDULER_API_ENABLED = True    

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route("/") 
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    return render_template("index.html", current_year=datetime.now().year)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = Registration()
    if form.validate_on_submit():
        password_hash = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=12)
        try:
            new_user = User(
                email = form.email.data,
                name = form.name.data,
                password = password_hash,
                date_joined = datetime.now()
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            return redirect(url_for("dashboard"))
        except IntegrityError:
            flash("This email already exists")
            return redirect(url_for("register"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = Login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        stmt = select(User).where(User.email == email)
        user = db.session.scalar(stmt)

        if not user:
            flash("User with this email does not exists", "error")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password, kindly try again", "error")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("login.html", form=form)



@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = ResetPassword()    
    if form.validate_on_submit(): 
        email = form.email.data
        user = db.session.execute(db.select(User). where(User.email == email)).scalar()       

        if user:
            serializer = generate_serializer()
            token = serializer.dumps(user.email, salt="password-reset")
            reset_link = url_for("new_password", token=token, _external=True)
            
            # !Send Mail
            html_body = render_template("password-reset.html", user_name=user.name, reset_link=reset_link)  
            message = Mail(
                from_email=MY_EMAIL,
                to_emails=user.email,
                subject='🔐 Password Reset',
                html_content=html_body
            )
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response)
            except Exception as e:
                print(e)
        flash("A password reset link has been sent.", "success")
        return redirect(url_for("reset_password"))
    return render_template("reset-password.html", form=form)



@app.route("/reset-password/<token>", methods=["GET", "POST"])
def new_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = NewPasswordForm()
    serializer = generate_serializer()

    try:
        email = serializer.loads(token, salt="password-reset", max_age=1800)  # 30 minutes
    except SignatureExpired:
        flash("This reset link has expired. Please request a new one.", "error")
        return redirect(url_for("reset_password"))
    except BadSignature:
        flash("Invalid or tampered reset link.", "error")
        return redirect(url_for("reset_password"))


    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=12)

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            user.password = hashed_password
            db.session.commit()
            flash("Your password has been reset", "success")
            return redirect(url_for("login"))
        else:
            flash("User not found.", "error")
            return redirect(url_for("reset_password"))
    return render_template("new-password.html", form=form, token=token)


    
@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    form = AddTask()
    if form.validate_on_submit():
        my_task = form.add_task.data
        date = form.due_date.data
        now = datetime.now()

        if date < now:
            flash("Due date cannot be in the past", "error")  
            return redirect(url_for("dashboard"))  
        else:
            new_task = Task(
                user_id=current_user.id,
                task = my_task,
                due_date = date,
                created_at = now,
            )
            db.session.add(new_task)

            current_user.tasks_added += 1

            db.session.commit()   
            flash("Task sucessfully added", "success")     
            return redirect(url_for("dashboard"))   
    stmt = select(Task).where(Task.user_id == current_user.id)
    task_row = db.session.scalars(stmt).all()
    complete_forms = {task.id: CompleteTaskForm() for task in task_row}
    first_name = current_user.name.split(" ")[0]
    return render_template("dashboard.html", active_page="dashboard", name=first_name, form=form, user = current_user, tasks=task_row, complete_forms=complete_forms)


@app.route("/profile")
@login_required
def user_profile():
    return render_template("user-profile.html", user = current_user, active_page="profile", form=ImageUploadForm())


#! File upload
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    form = ImageUploadForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = f"{current_user.id}_{int(time.time())}_{uuid.uuid4().hex}_{secure_filename(image.filename)}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Delete old profile pic file if it exists
        old_filename = current_user.profile_pic
        if old_filename:
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        image.save(upload_path)

        current_user.profile_pic = filename
        db.session.commit()

        flash("Profile picture updated!", "success")
        return redirect(url_for('user_profile'))
    else:
        flash("Images only!", "error")      
    return redirect(url_for('user_profile'))
    


@app.route("/support")
def support():
    return render_template("support.html")


@app.route("/delete/<int:task_id>")
@login_required
def delete(task_id):
    task = db.get_or_404(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", "error") 
    return redirect(url_for('dashboard'))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit(task_id):
    user_task = db.get_or_404(Task, task_id)
    edit_form = AddTask(
        user_id=user_task.user_id,
        task = user_task.task,
        due_date = user_task.due_date,
        created_at = user_task.created_at,
    )
    if edit_form.validate_on_submit():
        user_task.task = edit_form.add_task.data
        user_task.due_date = edit_form.due_date.data
        db.session.commit() 
        flash("Task sucessfully updated", "success")
        return redirect(url_for('dashboard')) 
    return redirect(url_for('dashboard'))


@app.route("/pinned/<int:task_id>")
@login_required
def pinned(task_id):
    user_task = db.get_or_404(Task, task_id)
    
    user_task.is_pinned = True
    db.session.commit() 
    return redirect(url_for('dashboard'))  


@app.route("/unpinned/<int:task_id>", methods=["GET", "POST"])
@login_required
def unpinned(task_id):
    user_task = db.get_or_404(Task, task_id)

    user_task.is_pinned = False
    db.session.commit() 
    return redirect(url_for('dashboard'))  



@app.route("/preview-email")
def preview_email():
    return render_template("task-reminder.html", user_name=current_user.name, due_date=current_user.email) 


        
def send_completion_email(user_email, user_name, task_title, completed_at): 
    with app.app_context():
        html_body = render_template(
            "task-complete.html",
            user_name=user_name,
            task_title=task_title,
            completed_at=completed_at.strftime('%Y-%m-%d, %H:%M')
        )            
        
        message = Mail(
                from_email=MY_EMAIL,
                to_emails=user_email,
                subject='🎉 Task Completed',
                html_content=html_body
            )
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)     
            return f'✅ Email sent! Status: {response.status_code}'        
        except Exception as e:
            return f'❌ Error: {str(e)}'
        


@app.route("/complete/<int:task_id>", methods=["GET", "POST"])
@login_required
def complete_task(task_id):
    user_task = db.get_or_404(Task, task_id)

    user_task.is_completed = True
    user_task.completed_at = datetime.now() 

    current_user.tasks_completed += 1

    db.session.commit()

    # Schedule email 10 seconds later
    job_id = f"email_{current_user.id}_{task_id}"
    scheduler.add_job(
        id=job_id,
        func=send_completion_email,
        args=[current_user.email, current_user.name, user_task.task, user_task.completed_at],
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=10),
        replace_existing=True
    )
    flash("Task marked as complete", "success")
    return redirect(url_for("dashboard"))



#! Task Reminder
@scheduler.task('interval', id='reminder_job', minutes=1,  max_instances=1)
def scheduled_reminder():
    with app.app_context():
        now = datetime.now()
        soon = now + timedelta(minutes=15)
        
        upcoming_tasks = Task.query.filter(
            and_(
                Task.due_date <= soon,
                Task.due_date > now,
                Task.is_completed == False,
                Task.reminder_sent == False
            )
        ).all()

        for task in upcoming_tasks:
            user = task.user
            html_body = render_template("task-reminder.html", user_name=user.name, due_date=task.due_date, task_title=task.task)

            message = Mail(
                from_email=MY_EMAIL,
                to_emails=user.email,
                subject='⏰ Task Reminder',
                html_content=html_body
            )

            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)

                if response.status_code in [200, 202]:
                    task.reminder_sent = True
                    db.session.add(task)  # 👈 Ensure task is added to session
                    db.session.commit()
                    print(f'✅ Email sent to {user.email}! Status: {response.status_code}')
                else:
                    print(f'❌ Email not sent to {user.email}. Status: {response.status_code}')

            except Exception as e:
                db.session.rollback()
                logging.error(f"❌ Failed to send email to {user.email}: {e}")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))



@app.route("/robots.txt")
def robots_txt():
    return app.send_static_file("robots.txt")


