from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 定义学分结果模型
class CreditResult(db.Model):
    __tablename__ = 'credit_results'
    
    student_name = db.Column(db.String(100), primary_key=True, nullable=False)
    student_id = db.Column(db.String(15), primary_key=True, nullable=False)
    major = db.Column(db.String(100), primary_key=True, nullable=False)
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
