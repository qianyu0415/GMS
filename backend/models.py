from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 定义课程数据模型
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    major_id = db.Column(db.Integer, nullable=False)
    course_name = db.Column(db.String(255), nullable=False)
    course_type = db.Column(db.String(100), nullable=False)

# 定义学分结果模型
class CreditResult(db.Model):
    __tablename__ = 'credit_results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(100), nullable=False)
    spring_required_credits = db.Column(db.Float)
    autumn_required_credits = db.Column(db.Float)
    spring_core_credits = db.Column(db.Float)
    autumn_core_credits = db.Column(db.Float)
    numerical_logic_credits = db.Column(db.Float)
    spring_limited_credits = db.Column(db.Float)
    autumn_limited_credits = db.Column(db.Float)
    short_term_training_credits = db.Column(db.Float)
    international_credits = db.Column(db.Float)
    elective_credits = db.Column(db.Float)
    outmajor_credits = db.Column(db.Float)
    culture_core_credits = db.Column(db.Float)
    culture_choose_credits = db.Column(db.Float)
    culture_total_credits = db.Column(db.Float)
    innovation_credits = db.Column(db.Float)
