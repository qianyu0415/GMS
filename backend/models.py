from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

class CreditResult(db.Model):
    __tablename__ = 'credit_results'
    
    student_name = db.Column(db.String(100), primary_key=True, nullable=False)
    student_id = db.Column(db.String(15), primary_key=True, nullable=False)
    major = db.Column(db.String(100), primary_key=True, nullable=False)
    spring_required_credits = db.Column(db.Float)
    autumn_required_credits = db.Column(db.Float)
    core_credits = db.Column(db.Float)
    numerical_logic_credits = db.Column(db.Float)
    limited_credits = db.Column(db.Float)
    short_term_training_credits = db.Column(db.Float)
    international_credits = db.Column(db.Float)
    elective_credits = db.Column(db.Float)
    outmajor_credits = db.Column(db.Float)
    culture_core_credits = db.Column(db.Float)
    culture_choose_credits = db.Column(db.Float)
    MOOC = db.Column(db.JSON)  # 使用 JSON 类型存储列表
    innovation_credits = db.Column(db.Float)

# 删除并重新创建表
def reset_credit_results_table():
    with db.engine.connect() as connection:
        # 删除旧表
        connection.execute(text("DROP TABLE IF EXISTS credit_results"))
        # 创建新表
        db.create_all()

if __name__ == "__main__":
    # 绑定数据库 URI
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/credits_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        reset_credit_results_table()
        print("表 credit_results 已重新创建")
