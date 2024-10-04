from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 创建 Flask 应用
app = Flask(__name__)

# 设置 MySQL 数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/credits_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义课程数据模型
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    major_id = db.Column(db.Integer, nullable=False)
    course_name = db.Column(db.String(255), nullable=False)
    course_type = db.Column(db.String(100), nullable=False)

# 初始化数据库表
def create_courses_table():
    db.create_all()
    print("Courses table created successfully!")

# 插入课程数据
def insert_courses():
    courses_mapping = {
        1: ["处理器设计与实践", "计算机科学/计算机工程专业方向实践", "计算机科学与工程程序设计实践", "计算机体系结构A", "计算理论", "计算系统设计与实现"],
        2: ["大数据程序设计实践", "大数据分析A", "大数据计算基础A", "大数据软件开发与实践", "大数据挖掘", "大数据综合实践"],
        3: ["模式识别与机器学习A", "人工智能程序设计实践", "人工智能软件开发与实践", "人工智能数学基础", "知识表示与推理", "智能系统设计与实践"],
        4: ["互联网基础设施安全A", "软件安全与逆向分析", "网络攻防技术", "网络空间安全设计与实践I", "网络空间安全设计与实践II", "信息安全程序设计实践"],
        5: ["密码学原理", "网络与系统安全A", "信息安全程序设计实践", "信息安全设计与实践I", "信息安全设计与实践II", "信息内容安全A"],
        6: ["开源软件开发实践", "软件测试与质量保障", "软件工程专业导论", "软件构造", "软件过程与项目管理", "软件架构与中间件A", "需求分析与系统设计", "云原生技术实践"],
        7: ["物联网程序设计实践", "物联网软件开发与实践", "物联网系统A", "信号与系统", "信息物理系统-理论与建模A", "智能物联网系统设计与实践"],
        8: ["基因组信息学", "生物大数据程序设计实践", "生物大数据软件升发与实践", "生物信息学", "生物信息学专业方向实践", "系统生物学"]
    }

    for major_id, courses in courses_mapping.items():
        for course in courses:
            new_course = Course(major_id=major_id, course_name=course, course_type='专业核心')
            db.session.add(new_course)
    db.session.commit()
    print("Courses inserted successfully!")

# 启动应用并执行
if __name__ == '__main__':
    with app.app_context():  # 确保在 app 上下文中执行
        create_courses_table()  # 创建表
        insert_courses()        # 插入数据
