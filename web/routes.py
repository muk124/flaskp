import secrets
import os
from flask import render_template, url_for, flash, redirect
from web import app,db, bcrypt
from web.forms import registrationform,loginform, updateaccountform
from web.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


posts=[ { 'author':'Muktesh', 'title':'first blog post', 'content':'first content', 'date_passed':'3rd-August-2019'}] 

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html',posts=posts)     

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=registrationform()
    if(form.validate_on_submit()):
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created, you may now Log In','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unscusseful', 'danger')
    return render_template('login.html',title='login', form=form)
    
    

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
    
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn
    
@app.route('/Profile', methods=['GET', 'POST'])
@login_required
def Profile():
    form = updateaccountform()
    if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
    image_file = url_for('static', filename= 'profile_pics/' + current_user.image_file)
    return render_template('account.html',title='Profile', image_file = image_file, form = form)
    