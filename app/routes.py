from flask import Blueprint,Flask,redirect,render_template,request,url_for,flash,session
from . import db
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required,login_user,logout_user

main = Blueprint('main', __name__)


@main.route('/') 
def home():
    if session.get('user'):
        user_exists = User.query.filter_by(username=session['user']).first()
        if not user_exists:
            # User was deleted from database, so clear session
            session.clear()
    user=session.get('user','')
    return render_template('home.html',username=user)    



@main.route('/data')
def data():
    profiles = User.query.all()
    return render_template('data.html',profiles=profiles)



# // Add Profile //

@main.route('/register',methods=['GET','POST'])
def register():
   
    if request.method == 'POST':
        username = request.form['username'].capitalize()
        email = request.form['email']
        password = request.form['password']
        hash_pass=generate_password_hash(password)
        new_user = User(username=username, email=email,password=hash_pass)
       
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('register.html')
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
   
    return render_template('register.html')



# // Delete Profile//

@main.route('/delete/<int:id>')
def delete_profile(id):
    user_to_delete = User.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    # flash('User deleted successfully!', 'success')
    return redirect(url_for('main.data'))



# @main.route('/home')
# # @login_required
# def home(): 
#     return render_template('home.html')



# // Login //

@main.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].capitalize()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            session['user'] = username
            # flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Check your credentials.', 'danger')
    return render_template('login.html')




# // Admin Login //

@main.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        admin_username = request.form.get('admin_username')
        admin_password = request.form.get('admin_password')
        
        if admin_username == 'Admin' and admin_password == 'Adminpass':
            return redirect(url_for('main.data'))
        
        else:
            flash('Invalid admin credentials.', 'danger')

    return render_template('admin.html') 


# //FORGOT PASS ROUTE//

@main.route('/forgotpass',methods=['GET','POST'])
def forgotpass():
    if request.method == 'POST':
        email = request.form.get('Email')
        new_pass = request.form['new_pass']
        user = User.query.filter_by(email=email).first()
        if user:
            user.password =generate_password_hash(new_pass)
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Email not found. Please check and try again.', 'danger')
    return render_template('forgotpass.html')
        

@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user', None)
    return redirect(url_for('main.home'))