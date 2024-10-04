import os
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pymysql
from credits_calculator import calculate_credits  # 导入学分计算逻辑
from models import db, CreditResult, Course

# 使用 pymysql 替代 MySQLdb
pymysql.install_as_MySQLdb()

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 设置 MySQL 数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/credits_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # 初始化 SQLAlchemy 对象

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

# 设置上传文件存储目录
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 定义专业字典映射
majors_mapping = {
    "计科": 1,
    "大数据": 2,
    "人工智能": 3,
    "网安": 4,
    "信安": 5,
    "软工": 6,
    "物联网": 7,
    "生信": 8
}

# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 提取文件名中的专业信息
def extract_major_from_filename(filename):
    for major_name, major_code in majors_mapping.items():
        if major_name in filename:
            return major_code
    return None

# 处理 Excel 文件上传和解析
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('没有文件上传')
        return jsonify({'error': '没有文件上传'}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error('没有选择文件')
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        app.logger.error('不支持的文件格式: %s', file.filename)
        return jsonify({'error': '不支持的文件格式'}), 400

    # 保存文件到上传目录
    filename = file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    app.logger.info(f"文件保存成功: {file_path}")

    # 解析文件名确定专业
    current_major = extract_major_from_filename(filename)
    if current_major is None:
        app.logger.error('无法识别专业，文件名: %s', filename)
        return jsonify({'error': '无法识别专业，请确保文件名包含专业关键词'}), 400

    # 读取 Excel 文件
    try:
        df = pd.read_excel(file_path)

        # 通过 current_major 获取该专业对应的核心课程
        result = calculate_credits(df, current_major)

        # 从前端获取 student_name 和 major
        student_name = request.form.get('student_name', '未命名学生')
        major = request.form.get('major', '未命名专业')

        # 将结果存储到数据库
        credit_entry = CreditResult(
            student_name=student_name,
            major=major,
            spring_required_credits=result['春季必修学分'],
            autumn_required_credits=result['秋季必修学分'],
            spring_core_credits=result['春季核心课程学分'],
            autumn_core_credits=result['秋季核心课程学分'],
            numerical_logic_credits=result['数字逻辑学分'],
            spring_limited_credits=result['春季限选学分'],
            autumn_limited_credits=result['秋季限选学分'],
            short_term_training_credits=result['企业短期实训/专业实践学分'],
            international_credits=result['国际化课程学分'],
            elective_credits=result['专业选修学分'],
            outmajor_credits=result['外专业学分'],
            culture_core_credits=result['素质核心学分'],
            culture_choose_credits=result['素质选修学分'],
            culture_total_credits=result['文化素质教育学分'],
            innovation_credits=result['创新创业学分']
        )

        db.session.add(credit_entry)
        db.session.commit()

        return jsonify(result)
    except Exception as e:
        app.logger.error('文件解析失败: %s', str(e))
        return jsonify({'error': str(e)}), 500

# 启动 Flask 应用
if __name__ == '__main__':
    with app.app_context():  # 确保数据库操作在应用上下文中执行
        db.create_all()  # 创建数据库表
    app.run(debug=True)
