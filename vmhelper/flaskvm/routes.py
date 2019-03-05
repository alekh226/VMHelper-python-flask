import os
import secrets
import pygal
from PIL import Image
from flask import render_template, url_for, flash, redirect,request,send_file
from flaskvm.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm,ResetPasswordForm, RequestResetForm,GetReportForm
from flaskvm import app, bcrypt, db, mail
from flaskvm.models import User, Post,Plan,Activity
from flask_login import login_user,current_user,logout_user, login_required
from flask_mail import Message
from flaskvm.final_sent import sentimental_analysis


@app.route("/")
@app.route("/home")
def home():
    #page = request.args.get('page', 1, type=int)
    #posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    #flash(f'This is {current_user}','success')
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.submit.data :
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            plan='demo'
            request1= Plan.query.filter_by(plan_name=plan).first()
            user = User(username= form.username.data, email= form.email.data,password=hashed_password,active_plan=plan,request_left=request1.max_request)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
        elif form.basic.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            plan='basic'
            request1= Plan.query.filter_by(plan_name=plan).first()
            user = User(username= form.username.data, email= form.email.data,password=hashed_password,active_plan=plan,request_left=request1.max_request)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
        elif form.pro.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            plan='pro'
            request1= Plan.query.filter_by(plan_name=plan).first()
            user = User(username= form.username.data, email= form.email.data,password=hashed_password,active_plan=plan,request_left=request1.max_request)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
        elif form.premium.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
            plan='premium'
            request1= Plan.query.filter_by(plan_name=plan).first()
            user = User(username= form.username.data, email= form.email.data,password=hashed_password,active_plan=plan,request_left=request1.max_request)
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex= secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex+ f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account" , methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.submit.data:
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username=form.username.data
            current_user.email=form.email.data
            db.session.commit()
            flash('Your Profile has been updated','success')
            return redirect(url_for('account'))
        elif form.submit_plan.data:
            current_user.active_plan = form.plan.data
            current_user.request_left += Plan.query.filter_by(plan_name=form.plan.data).first().max_request
            db.session.commit()
            flash('Your Profile has been updated','success')
            return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data=current_user.username
        form.email.data= current_user.email
    image_file= url_for('static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form =form)



def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)




@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/home#contact")
def contact():
    return redirect("http://127.0.0.1:5000/home#contact")

@app.route("/home#about")
def about():
    return redirect("http://127.0.0.1:5000/home#about")

@app.route("/home#pricing")
def pricing():
    return redirect("http://127.0.0.1:5000/home#pricing")

@app.route("/home#services")
def services():
    return redirect("http://127.0.0.1:5000/home#services")

@app.route("/getreport", methods=['GET', 'POST'])
@login_required
def getreport():
    form= GetReportForm()
    if current_user.is_authenticated:
        if request.method == 'POST':
          if form.validate_on_submit():
            if form.submit1.data :
                if current_user.request_left > 0:
                    current_user.request_left = current_user.request_left-1
                    db.session.commit()
                    brand= form.brand.data
                    location = form.location.data
                    return redirect(url_for('showreport', brand=brand,location=location))
                else:
                    flash('Plan Expired! please update the plan','danger')
                    return redirect(url_for('account'))
          else:
            return render_template('get_report.html', title='Get Report', form = form)

             
        elif request.method == 'GET':
            return render_template('get_report.html', title='Get Report', form = form)
    else :
        flash('You dont have access to this place. please login first','danger')
        return redirect(url_for('home'))

@app.route("/showreport")
@login_required
def showreport():
    if current_user.is_authenticated:
        brand= request.args.get('brand')
        location = request.args.get('location')
        activity= Activity(brand=brand,location=location,user_id=current_user.id)
        db.session.add(activity)
        db.session.commit()
        sent = sentimental_analysis(brand,location)
        sent.analyse()
        tweets = sent.get_tweets()
        tweets_inf = sent.get_tweets_inf()
        positive_count=sent.get_positive_tweets_count()
        negative_count=sent.get_negative_tweets_count()
        neutral_count=sent.get_neutral_tweets_count()
        total_count = positive_count+negative_count+neutral_count
        pubdate=[]
        polarity=[]
        for item in tweets :
            pubdate.append(item['pubdate'])
            polarity.append(item['polarity'])
        graph = pygal.Line()
        graph.title = 'Change in popularity of brand over time.'
        graph.x_labels = pubdate
        graph.add('Polarity',  polarity)
        graph_data = graph.render_data_uri()



        graph1= pygal.Pie()
        graph1.title = 'Analysis Report'
        graph1.add('Positive Users',  positive_count)
        graph1.add('Negative Users',  negative_count)
        graph1.add('Neutral Users', neutral_count)
        graph_data1 = graph1.render_data_uri()

        #flash(f'searched for {brand+" "+location}!', 'success')
        return render_template('show_report.html',title='Show Report',brand=brand,location=location, tweets=tweets,tweets_inf=tweets_inf, graph_data=graph_data
            ,positive_count=positive_count,negative_count=negative_count,neutral_count=neutral_count,total_count=total_count,graph_data1=graph_data1)
     
    else :
        flash('You dont have access to this place. please login first','danger')
        return redirect(url_for('home'))


@app.route("/downloadp")
@login_required
def download_p():
    if current_user.is_authenticated:
        return send_file('static/analysed_tweets_p.csv',
                     mimetype='text/csv',
                     attachment_filename='positive users.csv',
                     as_attachment=True)

    else :
        flash('You dont have access to this place. please login first','danger')
        return redirect(url_for('home'))
@app.route("/downloadn")
@login_required
def download_n():
    if current_user.is_authenticated:
        return send_file('static/analysed_tweets_n.csv',
                     mimetype='text/csv',
                     attachment_filename='neutral users.csv',
                     as_attachment=True)

    else :
        flash('You dont have access to this place. please login first','danger')
        return redirect(url_for('home'))

@app.route("/downloadi")
@login_required
def download_inf():
    if current_user.is_authenticated:
        return send_file('static/analysed_tweets_inf.csv',
                     mimetype='text/csv',
                     attachment_filename='inf_users.csv',
                     as_attachment=True)

    else :
        flash('You dont have access to this place. please login first','danger')
        return redirect(url_for('home'))