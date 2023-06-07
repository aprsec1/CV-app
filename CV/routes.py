from CV import app, db, bcrypt, mail
from flask import render_template, url_for, request, redirect, flash
from flask_login import login_user, current_user, logout_user, login_required
from CV.forms import LoginForm, UpdateAccountForm, ResetPasswordForm, RequestResetForm, PersonalForm, UserForm, \
    WorkExperienceForm, CertificationForm, EducationForm
from CV.models import User, WorkExperience, Certification, Education, PersonalInfo
from PIL import Image
import secrets, os
from flask_mail import Message
from datetime import datetime

with app.app_context():
    db.create_all()

@app.route("/")
@app.route("/home")
def homepage():
    user_profiles = User.query.all()
    return render_template('home.html', user_profiles=user_profiles)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = User.query.filter_by(user_id=user_id).first_or_404()
    personal = PersonalInfo.query.filter_by(user_id=user_id).first_or_404()
    work1 = WorkExperience.query.filter_by(user_id=user_id)
    certs = Certification.query.filter_by(user_id=user_id)
    educations = Education.query.filter_by(user_id=user_id)
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('user_profile.html', user=user, personal=personal, work1=work1, certs=certs, educations=educations, image_file=image_file)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('account'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('homepage'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename) # was f_name - _ underscore ignorira varijablu
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125) # stavi sve slike u 125x125
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    form1 = PersonalForm()
    personal_info = PersonalInfo.query.filter_by(user_id=current_user.user_id).first()
    if form1.validate_on_submit():
        if personal_info:
            personal_info.first_name = form1.first_name.data
            personal_info.last_name = form1.last_name.data
            personal_info.address = form1.address.data
            personal_info.birth_date = datetime.combine(form1.birth_date.data, datetime.min.time())
            personal_info.about = form1.about.data
        else:
            personal_info = PersonalInfo(
                user_id=current_user.user_id,
                first_name=form1.first_name.data,
                last_name=form1.last_name.data,
                address=form1.address.data,
                birth_date=datetime.combine(form1.birth_date.data, datetime.min.time()),
                about=form1.about.data
            )
            db.session.add(personal_info)
        db.session.commit()
        flash('Your personal information has been updated!', 'success')
        return redirect(url_for('account'))
    if personal_info:
        form1.first_name.data = personal_info.first_name
        form1.last_name.data = personal_info.last_name
        form1.address.data = personal_info.address
        form1.birth_date.data = personal_info.birth_date
        form1.about.data = personal_info.about

    form2 = WorkExperienceForm()
    form_work_experience = WorkExperience()
    if request.method == 'POST' and form2.validate_on_submit():
        form_work_experience.company_name = form2.company_name.data
        form_work_experience.job_title = form2.job_title.data
        form_work_experience.start_date = form2.start_date.data
        form_work_experience.end_date = form2.end_date.data
        form_work_experience.description = form2.description.data

        work_exp = WorkExperience(
            user_id=current_user.user_id,
            company_name=form_work_experience.company_name,
            job_title=form_work_experience.job_title,
            start_date=form_work_experience.start_date,
            end_date=form_work_experience.end_date,
            description=form_work_experience.description
        )
        db.session.add(work_exp)
        db.session.commit()
        flash('Your work experiences have been updated!', 'success')
        return redirect(url_for('account'))

    work_x = WorkExperience.query.filter_by(user_id=current_user.user_id)

    form3 = EducationForm()
    form_education = Education()
    if request.method == 'POST' and form3.validate_on_submit():
        form_education.institution_name = form3.institution_name.data
        form_education.degree = form3.degree.data
        form_education.start_date = form3.start_date.data
        form_education.end_date = form3.end_date.data
        form_education.description = form3.description.data

        education = Education(
            user_id=current_user.user_id,
            institution_name=form_education.institution_name,
            degree=form_education.degree,
            start_date=form_education.start_date,
            end_date=form_education.end_date,
            description=form_education.description
        )
        db.session.add(education)
        db.session.commit()
        flash('Your education have been updated!', 'success')
        return redirect(url_for('account'))

    edu_x = Education.query.filter_by(user_id=current_user.user_id)

    form4 = CertificationForm()
    form_cert = Certification()
    if request.method == 'POST' and form4.validate_on_submit():
        form_cert.cert_name = form4.cert_name.data
        form_cert.institution = form4.institution.data
        form_cert.date_earned = form4.date_earned.data
        form_cert.date_expired = form4.date_expired.data

        certs = Certification(
            user_id=current_user.user_id,
            cert_name=form_cert.cert_name,
            institution=form_cert.institution,
            date_earned=form_cert.date_earned,
            date_expired=form_cert.date_expired,
        )
        db.session.add(certs)
        db.session.commit()
        flash('Your education have been updated!', 'success')
        return redirect(url_for('account'))

    cert_x = Certification.query.filter_by(user_id=current_user.user_id)

    return render_template('account.html', title='Account', image_file=image_file, form=form, form1=form1,
                           form2=form2, form3=form3, form4=form4, work_x=work_x, edu_x=edu_x, cert_x=cert_x)


def send_reset_email(user):
    token = user.generate_confirmation_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simpy ignore this email and no changes will be made.
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
        flash('An email has been sent with instructions to reset your password', 'info')
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
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/delete_work_experience/<int:work_id>', methods=['GET', 'POST'])
def delete_work_experience(work_id):
    work2 = WorkExperience.query.get_or_404(work_id)
    db.session.delete(work2)
    db.session.commit()
    flash('Work experience has been deleted!', 'success')
    return redirect(url_for('account'))


@app.route('/update_work_experience/<int:work_id>', methods=['GET', 'POST'])
def update_work_experience(work_id):
    work3 = WorkExperience.query.get_or_404(work_id)
    form_update = WorkExperienceForm()
    if request.method == 'POST' and form_update.validate_on_submit():
        work3.company_name = form_update.company_name.data
        work3.job_title = form_update.job_title.data
        work3.start_date = form_update.start_date.data
        work3.end_date = form_update.end_date.data
        work3.description = form_update.description.data
        db.session.commit()
        flash('Work experience has been updated!', 'success')
        return redirect(url_for('account'))

    if work3:
        form_update.company_name.data = work3.company_name
        form_update.job_title.data = work3.job_title
        form_update.start_date.data = work3.start_date
        form_update.end_date.data = work3.end_date
        form_update.description.data = work3.description
    return render_template('update_work_experience.html', form=form_update, work=work3)


@app.route('/delete_education/<int:edu_id>', methods=['GET', 'POST'])
def delete_education(edu_id):
    edu1 = Education.query.get_or_404(edu_id)
    db.session.delete(edu1)
    db.session.commit()
    flash('Work experience has been deleted!', 'success')
    return redirect(url_for('account'))


@app.route('/update_education/<int:edu_id>', methods=['GET', 'POST'])
def update_education(edu_id):
    edu2 = Education.query.get_or_404(edu_id)
    edu_update = EducationForm()
    if request.method == 'POST' and edu_update.validate_on_submit():
        edu2.institution_name = edu_update.institution_name.data
        edu2.degree = edu_update.degree.data
        edu2.start_date = edu_update.start_date.data
        edu2.end_date = edu_update.end_date.data
        edu2.description = edu_update.description.data
        db.session.commit()
        flash('Work experience has been updated!', 'success')
        return redirect(url_for('account'))

    if edu2:
        edu_update.institution_name.data = edu2.institution_name
        edu_update.degree.data = edu2.degree
        edu_update.start_date.data = edu2.start_date
        edu_update.end_date.data = edu2.end_date
        edu_update.description.data = edu2.description
    return render_template('update_education.html', form=edu_update, edu=edu2)


@app.route('/delete_certification/<int:cert_id>', methods=['GET', 'POST'])
def delete_certification(cert_id):
    cert1 = Certification.query.get_or_404(cert_id)
    db.session.delete(cert1)
    db.session.commit()
    flash('Your certificate has been deleted!', 'success')
    return redirect(url_for('account'))


@app.route('/update_certification/<int:cert_id>', methods=['GET', 'POST'])
def update_certification(cert_id):
    cert2 = Certification.query.get_or_404(cert_id)
    cert_update = CertificationForm()
    if request.method == 'POST' and cert_update.validate_on_submit():
        cert2.cert_name = cert_update.cert_name.data
        cert2.institution = cert_update.institution.data
        cert2.date_earned = cert_update.date_earned.data
        cert2.date_expired = cert_update.date_expired.data
        db.session.commit()
        flash('Your certificate has been updated!', 'success')
        return redirect(url_for('account'))

    if cert2:
        cert_update.cert_name.data = cert2.cert_name
        cert_update.institution.data = cert2.institution
        cert_update.date_earned.data = cert2.date_earned
        cert_update.date_expired.data = cert2.date_expired
    return render_template('update_certification.html', form=cert_update, cert=cert2)