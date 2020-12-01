from flask import Flask, render_template, request, flash, session, redirect
from PayTm import Checksum
from flask_mysqldb import MySQL
import smtplib
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_sqlalchemy import SQLAlchemy
import json
import random

app = Flask(__name__)
app.secret_key = "This is Secret Key"

# con = pymysql.connect(user="raviacademy", password="javatohbaaphein@2020", host="db4free.net", port=3306,
#                       database="course_website")

# app.config['MYSQL_HOST'] = 'db4free.net'
# app.config['MYSQL_USER'] = 'raviacademy'
# app.config['MYSQL_PASSWORD'] = 'javatohbaaphein@2020'
# app.config['MYSQL_DB'] = 'course_website'
# app.config['MYSQL_PORT'] = 3306

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'course_website'

mysql = MySQL(app)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://raviacademy:javatohbaaphein%402020@db4free.net:3306/course_website'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/course_website'
db = SQLAlchemy(app)


with open('admin.json', 'r') as c:
    params = json.load(c)["sign_in"]


student = None
student_name = None
global vid_sno, admission_slug, f_email, slug, title
MERCHANT_KEY = 'Q3Tz5XNdK6hC4J6S'


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    slug = db.Column(db.String(21), nullable=False)
    videos = db.Column(db.Integer, nullable=True)
    bg_image = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=True)
    live = db.Column(db.Integer, nullable=True)


class Videos(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    poster = db.Column(db.String(80), nullable=False)
    video = db.Column(db.String(120), nullable=False)
    course_sno = db.Column(db.String(120), nullable=False)


class Admission(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    students = db.Column(db.String(80), nullable=False)
    courses = db.Column(db.Integer, nullable=False)


class Views(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(80), nullable=False)
    video_sno = db.Column(db.Integer, nullable=False)
    course_sno = db.Column(db.Integer, nullable=False)
    viewsr = db.Column(db.Integer, nullable=False)


class Subscribe(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    subscribers = db.Column(db.String(80), nullable=False)


class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Integer, nullable=False)


class Forgotpass(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(80), nullable=False)
    otp = db.Column(db.Integer, nullable=False)


class Live(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    islive = db.Column(db.String(80), nullable=False)


@app.route("/")
def index():
    courses = Posts.query.filter_by(live=1).all()
    return render_template('index.html', courses=courses)


@app.route("/course")
def course_single():
    posts = Posts.query.filter_by(live=1).all()
    return render_template('course.html', posts=posts)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_name']:
        all_posts = Posts.query.all()
        all_videos = Videos.query.order_by(Videos.course_sno).all()
        return render_template('dashboard_edit.html', all_posts=all_posts, all_videos=all_videos)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == params['admin_name'] and password == params['admin_password']:
            session['user'] = username
            all_posts = Posts.query.all()
            all_videos = Videos.query.order_by(Videos.course_sno).all()
            return render_template('dashboard_edit.html', all_posts=all_posts, all_videos=all_videos)
    return render_template('dashboard.html')


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == 'POST':
            current_title = request.form['title']
            current_content = request.form.get('content')
            current_slug = request.form['slug']
            current_videos = request.form['videos']
            current_bg_image = request.form['bg_image_name']
            current_price = request.form['price']
            current_live = request.form['live']

            if sno == '0':
                post = Posts(title=current_title, content=current_content, date=datetime.now(), slug=current_slug,
                             videos=current_videos, bg_image=current_bg_image, price=current_price, live=current_live)
                db.session.add(post)
                db.session.commit()

                if current_live == "1":
                    sub = Subscribe.query.filter_by().all()
                    for i in sub:
                        email_user = 'oplondhe@gmail.com'
                        email_password = 'Bhargavi@2012'
                        email_send = i.subscribers

                        msg = MIMEMultipart()
                        msg['From'] = email_user
                        msg['To'] = email_send
                        msg['Subject'] = f"New Course Available : {current_title}"

                        body = f"\tThe new course '{current_title}' is now available on website !!!\nIt's a course of "\
                               f"'{current_videos} videos' about:\n'{current_content}' \nPrice: ₹  {current_price}\n\n"\
                               f"Take a look at the course\n127.0.0.1:5000/course/{current_slug}"
                        msg.attach(MIMEText(body, 'plain'))

                        text = msg.as_string()
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(email_user, email_password)

                        server.sendmail(email_user, email_send, text)
                        server.quit()
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = current_title
                post.content = current_content
                post.slug = current_slug
                post.videos = current_videos
                post.bg_image = current_bg_image
                post.price = current_price
                post.live = current_live
                db.session.commit()
                return redirect("/edit/" + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', post=post, sno=sno)
    return render_template('dashboard.html')


@app.route("/videos/<string:sno>", methods=['GET', 'POST'])
def videos(sno):
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == 'POST':
            vid_title = request.form['title']
            vid_poster = request.form['poster']
            vid_video = request.form['video']
            vid_course = request.form['course']

            if sno == '0':
                video = Videos(title=vid_title, poster=vid_poster, video=vid_video, course_sno=vid_course)
                db.session.add(video)
                db.session.commit()
            else:
                video = Videos.query.filter_by(sno=sno).first()
                video.title = vid_title
                video.poster = vid_poster
                video.video = vid_video
                video.course_sno = vid_course
                db.session.commit()
                return redirect("/videos/" + sno)

        video = Videos.query.filter_by(sno=sno).first()
        return render_template('videos.html', video=video, sno=sno)
    return render_template('dashboard.html')


@app.route("/show_videos/<string:sno>", methods=['GET', 'POST'])
def show_videos(sno):
    if 'user' in session and session['user'] == params['admin_name']:
        course_name = Posts.query.filter_by(sno=sno).first()
        course_videos = Videos.query.filter_by(course_sno=sno).all()
        return render_template('show_videos_admin.html', course_videos=course_videos, course=course_name)
    return render_template('dashboard.html')


@app.route("/play_video_admin/<string:sno>")
def play_video_admin(sno):
    if 'user' in session and session['user'] == params['admin_name']:
        vid = Videos.query.filter_by(sno=sno).first()
        course = Posts.query.filter_by(sno=vid.course_sno).first()
        return render_template('play_video_admin.html', vid=vid, course=course)
    return redirect("/myacc")


@app.route("/img_uploader", methods=['GET', 'POST'])
def img_uploader():
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == 'POST':
            img = request.files['img']
            img.save(os.path.join(params['upload_image'], secure_filename(img.filename)))
            all_posts = Posts.query.all()
            all_videos = Videos.query.order_by(Videos.course_sno).all()
            return render_template('dashboard_edit.html', all_posts=all_posts, all_videos=all_videos)
    return render_template('dashboard.html')


@app.route("/video_uploader", methods=['GET', 'POST'])
def video_uploader():
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == 'POST':
            vid = request.files['vid']
            vid.save(os.path.join(params['upload_video'], secure_filename(vid.filename)))
            all_posts = Posts.query.all()
            all_videos = Videos.query.order_by(Videos.course_sno).all()
            return render_template('dashboard_edit.html', all_posts=all_posts, all_videos=all_videos)
    return render_template('dashboard.html')


@app.route("/img_uploader1", methods=['GET', 'POST'])
def img_uploader1():
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == 'POST':
            img = request.files['img']
            img.save(os.path.join(params['upload_image'], secure_filename(img.filename)))
            return "Image Uploaded Successfully"
    return render_template('dashboard.html')


@app.route("/video_uploader1", methods=['GET', 'POST'])
def video_uploader1():
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == 'POST':
            vid = request.files['vid']
            vid.save(os.path.join(params['upload_video'], secure_filename(vid.filename)))
            return "Video Uploaded Successfully"
    return render_template('dashboard.html')


@app.route("/allcourse")
def all_courses():
    posts = Posts.query.filter_by(live=1).all()
    return render_template('allcourse.html', posts=posts)


@app.route("/delete_post/<string:sno>")
def delete_post(sno):
    if 'user' in session and session['user'] == params['admin_name']:
        del_post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(del_post)
        db.session.commit()
        del_post_vid = Videos.query.filter_by(course_sno=sno).all()
        for i in range(len(del_post_vid)):
            db.session.delete(del_post_vid[i])
            db.session.commit()
        db.session.commit()
        return redirect("/dashboard")
    return render_template('dashboard.html')


@app.route("/delete_vid/<string:sno>")
def delete_vid(sno):
    if 'user' in session and session['user'] == params['admin_name']:
        del_post_vid = Videos.query.filter_by(sno=sno).first()
        db.session.delete(del_post_vid)
        db.session.commit()
        return redirect("/dashboard")
    return render_template('dashboard.html')


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/admission")
def admission():
    if 'student' in session:
        course_title = Posts.query.filter_by(slug=admission_slug).first()
        user = Users.query.filter_by(username=session['student']).first()
        data_dict = {
            'MID': 'VMjwTa47205061452223',
            'ORDER_ID': f'{course_title.sno}{random.randrange(0000000, 9999999)}',
            'TXN_AMOUNT': str(course_title.price),
            'CUST_ID': f'{user.sno}',
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:5000/payment'
        }
        data_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, MERCHANT_KEY)
        return render_template('paytm.html', data_dict=data_dict)
    else:
        flash("To admit a course you must log in first")
        return redirect('/')


@app.route("/payment", methods=['POST'])
def payment():
    form = request.form
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            course_title = Posts.query.filter_by(slug=admission_slug).first()
            assign_course = Admission(students=session['student'], courses=course_title.sno)
            db.session.add(assign_course)
            db.session.commit()

            get_course_videos = Videos.query.filter_by(course_sno=course_title.sno).all()
            for i in get_course_videos:
                generate_view_counter = Views(student=session['student'], video_sno=i.sno, course_sno=course_title.sno,
                                              viewsr=7)
                db.session.add(generate_view_counter)
                db.session.commit()
            return redirect("/myacc")
        else:
            print("Some error occurred while payment")
    return render_template("status.html", response=response_dict)


@app.route("/change_pass_req")
def change_pass_req():
    if 'student' in session:
        return render_template("change_pass.html")
    return redirect("/")


@app.route("/change_pass", methods=['GET', 'POST'])
def change_pass():
    if request.method == 'GET':
        render_template('change_pass.html')
    elif request.method == 'POST':
        password = request.form
        np = password['np']
        cp = password['cp']

        if np == cp:
            flash("Password Updated! Log in using new Password")
            email_user = 'oplondhe@gmail.com'
            email_password = 'Bhargavi@2012'
            email_send = session['student']

            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_send
            msg['Subject'] = "Password Changed"

            body = f"Hello {session['name']} , As per your order we have changed your old password to the new one " \
                   f"which you have just entered. Security is the First priority so, if its not you who changed the " \
                   f"password, kindly contact us...."
            msg.attach(MIMEText(body, 'plain'))

            text = msg.as_string()
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_user, email_password)

            server.sendmail(email_user, email_send, text)
            server.quit()

            user = Users.query.filter_by(username=session['student']).first()
            user.password = np
            db.session.commit()

            return redirect("/student_logout")
        else:
            return redirect("/change_pass_req")
    else:
        return redirect("/")


@app.route("/forgot_pass_email", methods=['GET', 'POST'])
def forgot_pass():
    if request.method == 'GET':
        return render_template("forgot_pass_email.html")
    elif request.method == 'POST':
        global f_email
        f_email = request.form['email']
        user = Users.query.filter_by(username=f_email).first()
        if user is None:
            return render_template("forgot_pass_email.html")
        else:
            otp = random.randint(000000, 999999)
            check_otp = Forgotpass.query.filter_by(user=f_email).first()
            if check_otp is None:
                print('hjg')
                send_otp = Forgotpass(user=f_email, otp=otp)
                db.session.add(send_otp)
            else:
                send_otp = Forgotpass.query.filter_by(user=f_email).first()
                send_otp.otp = otp

            db.session.commit()

            email_user = 'oplondhe@gmail.com'
            email_password = 'Bhargavi@2012'
            email_send = f_email

            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_send
            msg['Subject'] = f"Your OTP for getting Password for username {f_email}"

            body = f"Hello {user.name}, Your OTP is {otp} don't share it with anyone"
            msg.attach(MIMEText(body, 'plain'))

            text = msg.as_string()
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_user, email_password)

            server.sendmail(email_user, email_send, text)
            server.quit()
            return render_template("forgot_pass.html", email=f_email)
    else:
        return redirect("/")


@app.route("/get_pass", methods=["POST"])
def get_pass():
    otp = request.form['otp']
    check_otp = Forgotpass.query.filter_by(user=f_email).first()
    user = Users.query.filter_by(username=f_email).first()

    if otp == check_otp.otp:
        email_user = 'oplondhe@gmail.com'
        email_password = 'Bhargavi@2012'
        email_send = f_email

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = "Your Password"

        body = f"Hello {user.name}, Your password was :- \n\n{user.password}\n\nDelete this message as soon as " \
               f"possible and don't share your password with anyone......."
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)

        server.sendmail(email_user, email_send, text)
        server.quit()

        del_otp = Forgotpass.query.filter_by(user=f_email).first()
        db.session.delete(del_otp)
        db.session.commit()

        return redirect("/")
    return redirect("/")


@app.route("/student_logout")
def student_logout():
    session.pop('student')
    return redirect("/")


@app.route("/myacc")
def my_acc():
    if 'student' in session:
        zero = None
        my_courses = []
        admitted = Admission.query.filter_by(students=session['student']).all()

        for i in admitted:
            all_vid = Views.query.filter_by(course_sno=i.courses).all()
            for j in all_vid:
                if j.student == session['student']:
                    if j.viewsr != 0:
                        zero = 1
                    else:
                        zero = 0
                if zero == 0:
                    del_admission = Admission.query.filter_by(courses=i.courses).all()
                    for k in del_admission:
                        if k.students == session['student']:
                            db.session.delete(k)
                            db.session.commit()
                    del_view = Views.query.filter_by(course_sno=i.courses).all()
                    for k in del_view:
                        if k.student == session['student']:
                            db.session.delete(k)
                            db.session.commit()
        updated_admitted = Admission.query.filter_by(students=session['student']).all()
        for i in updated_admitted:
            courses = Posts.query.filter_by(sno=i.courses).first()
            my_courses.append(courses)
        posts = Posts.query.filter_by(live=1).all()
                       
        return render_template('myacc.html', admitted=admitted, courses=my_courses, posts=posts, name=session['name'])
    return redirect("/")


@app.route("/my_course/<string:sno>")
def my_course(sno):
    if 'student' in session:
        course = Posts.query.filter_by(sno=sno).first()
        my_videos = Videos.query.filter_by(course_sno=sno).all()
        return render_template("show_videos.html", course=course, course_videos=my_videos)
    return redirect('/myacc')


@app.route("/play_video/<string:sno>")
def play_video(sno):
    if 'student' in session:
        vid = Videos.query.filter_by(sno=sno).first()
        course = Posts.query.filter_by(sno=vid.course_sno).first()
        view1 = Views.query.filter_by(video_sno=sno).all()
        for i in view1:
            if i.student == session['student']:
                global vid_sno
                vid_sno = i.sno
                if i.viewsr != 0:
                    return render_template('play_video.html', vid=vid, course=course, view=i)
                else:
                    return "You exceed the maximum limit to watch this video"
    return redirect("/myacc")


@app.route("/setview", methods=['GET', 'POST'])
def set_view():
    if 'student' in session:
        view = Views.query.filter_by(sno=vid_sno).first()
        view.viewsr = int(view.viewsr) - 1
        db.session.commit()
        return redirect("/myacc")
    return redirect("/")


@app.route("/subscribe", methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        stud = request.form['email']
        sub = Subscribe(subscribers=stud)
        db.session.add(sub)
        db.session.commit()
        return "Your E-mail id is registered as a Subscriber, we will notify you whenever its time for new stuff !!!"


@app.route("/admissions")
def admissions():
    if 'user' in session and session['user'] == params['admin_name']:
        ad = Admission.query.all()
        courses = Posts.query.all()
        return render_template("admissions.html", ad=ad, courses=courses)
    return redirect("/")


@app.route("/subscribers")
def subscribers():
    if 'user' in session and session['user'] == params['admin_name']:
        subs = Subscribe.query.all()
        return render_template("subscribers.html", subs=subs)
    return redirect("/")


@app.route("/searched", methods=['GET', 'POST'])
def searched():
    if request.method == 'POST':
        exists = False
        result = []
        posts = Posts.query.all()
        for i in posts:
            if request.form['search'] in i.title:
                exists = True
                result.append(i)
        if exists:
            return render_template("search.html", results=result)
        else:
            return "No such Course Exist, We'll surely add it afterwards !!!"


@app.route("/start_live")
def start_live():
    if 'user' in session and session['user'] == params['admin_name']:
        is_live = Live.query.filter_by(sno=1).first()
        if is_live.islive == 1:
            return render_template("stop_live.html")
        else:
            return render_template("live.html")
    return redirect("/")


@app.route("/live", methods=['GET', 'POST'])
def live():
    if 'user' in session and session['user'] == params['admin_name']:
        if request.method == 'POST':
            receivers = []

            is_live = Live.query.filter_by(sno=1).first()
            is_live.islive = 1
            db.session.commit()

            global slug, title
            slug = request.form['slug']
            title = request.form['title']

            subs = Subscribe.query.all()
            for i in subs:
                if i.subscribers not in receivers:
                    receivers.append(i.subscribers)
            users = Users.query.all()
            for i in users:
                if i.username not in receivers:
                    receivers.append(i.username)

            for i in receivers:
                email_user = 'oplondhe@gmail.com'
                email_password = 'Bhargavi@2012'
                email_send = i

                msg = MIMEMultipart()
                msg['From'] = email_user
                msg['To'] = email_send
                msg['Subject'] = f"New Live Session started : {title}"

                body = f"\tThe new live session '{title}' is started , go ahead and watch it. \n\n" \
                       f"Click on the link below:\n\n" \
                       f"127.0.0.1:5000/show_live"
                msg.attach(MIMEText(body, 'plain'))

                text = msg.as_string()
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_user, email_password)

                server.sendmail(email_user, email_send, text)
                server.quit()
            return render_template("stop_live.html")
    return redirect("/")


@app.route("/stop_live")
def stop_live():
    if 'user' in session and session['user'] == params['admin_name']:
        is_live = Live.query.filter_by(sno=1).first()
        is_live.islive = 0
        db.session.commit()
        return redirect("/start_live")


@app.route("/show_live")
def show_live():
    is_live = Live.query.filter_by(sno=1).first()
    if is_live.islive == 1:
        return render_template("live_video.html", slug=slug, title=title)
    else:
        return "Live session ended, We'll notify you when new one starts"


@app.route("/login", methods=['Get', 'POST'])
def login():
    if request.method == 'GET':
        return redirect("/")
    if request.method == "POST":
        flag = 0
        details = request.form
        username = details['email']
        password = details['password']

        if username == "" or username is None:
            flash("Email field cannot be empty !!!")
            return render_template('index.html')
        elif password == "" or password is None:
            flash("Password field cannot be empty !!!")
            return render_template('index.html')
        else:
            users = Users.query.all()
            db.session.commit()

            for i in users:
                if i.username == username:
                    if password == i.password:
                        session['student'] = username
                        session['name'] = i.name
                        return redirect("/myacc")
                    else:
                        flash("Wrong Password")
                        flag = 3
                else:
                    if flag != 3:
                        flag = 1

            if flag == 1:
                flash("You Don't have an Existing account, You can create new Account in Sign Up section")
                return render_template('index.html')

            return redirect('/')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return redirect("/")
    if request.method == "POST":
        details = request.form
        name = details['name']
        email = details['email']
        password = details['password']
        c_password = details['c_pass']

        if email == "" or email is None:
            flash("Email cannot be  Empty!!!")
            return render_template('index.html')
        elif password == "" or password is None:
            flash("Password cannot be Empty!!!")
            return render_template('index.html')
        elif name == "" or name is None:
            flash("Name cannot be Empty!!!")
            return render_template('index.html')
        elif password == "" or name is None:
            flash("Name cannot be Empty!!!")
            return render_template('index.html')
        elif c_password != password:
            flash("Password did not match")
            return render_template('index.html')
        else:
            users = Users.query.all()

            for i in users:
                if i.username == email:
                    flash("You have an existing account, go ahead and login")
                    return render_template('index.html')
                else:
                    add_user = Users(username=email, password=password, name=name)
                    db.session.add(add_user)
                    db.session.commit()
                    flash("Account Created Successfully, Now you can Log in your account")

                    email_user = 'oplondhe@gmail.com'
                    email_password = 'Bhargavi@2012'
                    email_send = email

                    msg = MIMEMultipart()
                    msg['From'] = email_user
                    msg['To'] = email_send
                    msg['Subject'] = "Regarding registering your Account on our Website"

                    body = f"Thank you {name}, \n\nYour account is successfully created on our Website now you can " \
                           f"proceed further and search for the content you want \n\nHappy Programming"
                    msg.attach(MIMEText(body, 'plain'))

                    text = msg.as_string()
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email_user, email_password)

                    server.sendmail(email_user, email_send, text)
                    server.quit()

            return redirect('/')


@app.route("/contact", methods=['POST'])
def contact():
    if request.method == "POST":
        details = request.form
        f_name = details['fname']
        l_name = details['lname']
        subject = details['subject']
        email = details['email']
        message = details['msg']

        email_user = 'oplondhe@gmail.com'
        email_password = 'Bhargavi@2012'
        email_send = 'oplondhe@gmail.com'

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = subject

        body = f"{message} \n Yours truly\n{f_name} {l_name}\n{email}"
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)

        server.sendmail(email_user, email_send, text)
        server.quit()

        email_user = 'oplondhe@gmail.com'
        email_password = 'Bhargavi@2012'
        email_send = email

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = subject

        body = f"Thank you {f_name} {l_name} !!! ,  for helping us about {subject}, we will take an action " \
               f"regarding your message from mail id {email}"
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)

        server.sendmail(email_user, email_send, text)
        server.quit()

        flash("Your message is successfully sent to the owner of the Website")
        return render_template("index.html")


@app.route("/course/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    flag = False
    global admission_slug
    admission_slug = post_slug
    course = Posts.query.filter_by(slug=post_slug).first()
    posts = Posts.query.filter_by(live=1).all()
    if 'student' in session:
        admitted_courses = Admission.query.filter_by(courses=course.sno).all()
        for i in admitted_courses:
            if i.students == session['student']:
                flag = True
                break
        if flag:
            return render_template('admitted.html', course=course, posts=posts)

        else:
            return render_template('course.html', course=course, posts=posts)
    return render_template('course.html', course=course, posts=posts)


@app.route("/courses_contact", methods=['POST'])
def courses_contact():
    if request.method == "POST":
        details = request.form
        f_name = details['fname']
        l_name = details['lname']
        subject = details['subject']
        email = details['email']
        message = details['msg']

        email_user = 'oplondhe@gmail.com'
        email_password = 'Bhargavi@2012'
        email_send = 'oplondhe@gmail.com'

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = subject

        body = f"{message} \n\n\n\n Yours truly\n{f_name} {l_name}\n{email}"
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)

        server.sendmail(email_user, email_send, text)
        server.quit()

        email_user = 'oplondhe@gmail.com'
        email_password = 'Bhargavi@2012'
        email_send = email

        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = subject

        body = f"Thank you {f_name} {l_name} !!! ,  for helping us about {subject}, we will take an action " \
               f"regarding your message from mail id {email}"
        msg.attach(MIMEText(body, 'plain'))

        text = msg.as_string()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)

        server.sendmail(email_user, email_send, text)
        server.quit()

        flash("Your message is successfully sent to the owner of the Website")
        return render_template("course.html")


app.run(debug=True)
