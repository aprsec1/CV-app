from flask_login import UserMixin
import jwt
from CV import app, db, login_manager


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    personal = db.relationship('PersonalInfo', backref='user_personal', lazy=True)
    experience = db.relationship('WorkExperience', backref='user_work', lazy=True)
    certificates = db.relationship('Certification', backref='user_cert', lazy=True)
    education = db.relationship('Education', backref='user_education', lazy=True)

    def generate_confirmation_token(self, expiration=1800):
        return_token = jwt.encode(
            {
                "user_id": self.id
            },
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return return_token

    @staticmethod
    def verify_reset_token(token):
        try:
            user_id = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User(id={self.user_id}, username='{self.username}', email='{self.email}')"

    def get_id(self):
        return self.user_id


class PersonalInfo(db.Model):
    personal_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    birth_date = db.Column(db.Date)
    about = db.Column(db.String(240))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"PersonalInfo(id={self.user_id}, first_name={self.first_name}, last_name={self.last_name}"


class WorkExperience(db.Model):
    work_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"WorkExperience(id={self.user_id}, company_name='{self.company_name}', job_title='{self.job_title}')"


class Certification(db.Model):
    cert_id = db.Column(db.Integer, primary_key=True)
    cert_name = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    date_earned = db.Column(db.DateTime, nullable=False)
    date_expired = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"Certification(id={self.user_id}, cert_name='{self.cert_name}', institution='{self.institution}')"


class Education(db.Model):
    edu_id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(100), nullable=False)
    degree = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    def __repr__(self):
        return f"Education(id={self.user_id}, institution_name='{self.institution_name}', degree='{self.degree}')"
