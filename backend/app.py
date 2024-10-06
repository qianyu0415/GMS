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

# 处理多个 Excel 文件上传和解析
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('没有文件上传')
        return jsonify({'error': '没有文件上传'}), 400

    files = request.files.getlist('file')  # 获取多个文件
    if len(files) == 0:
        app.logger.error('没有选择文件')
        return jsonify({'error': '没有选择文件'}), 400

    results = []  # 存储所有文件处理的结果

    for file in files:
        if not allowed_file(file.filename):
            app.logger.error('不支持的文件格式: %s', file.filename)
            return jsonify({'error': f'不支持的文件格式: {file.filename}'}), 400

        # 保存文件到上传目录
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        app.logger.info(f"文件保存成功: {file_path}")

        # 解析文件名确定专业
        current_major = extract_major_from_filename(filename)
        if current_major is None:
            app.logger.error('无法识别专业，文件名: %s', filename)
            return jsonify({'error': f'无法识别专业，文件名: {filename}'}), 400

        # 读取并处理 Excel 文件
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

            # 添加处理结果到结果列表
            results.append({filename: result})

        except Exception as e:
            app.logger.error('文件解析失败: %s', str(e))
            return jsonify({'error': str(e)}), 500

    # 返回所有文件的处理结果
    return jsonify(results)

@app.route('/data', methods=['GET'])
def get_data():
    try:
        # 从数据库中查询所有 CreditResult 数据
        credit_results = CreditResult.query.all()
        
        # 将查询结果转换为 JSON 格式
        result_list = []
        for result in credit_results:
            result_list.append({
                'id': result.id,  # 添加 id 字段
                'student_name': result.student_name,
                'major': result.major,
                'spring_required_credits': result.spring_required_credits,
                'autumn_required_credits': result.autumn_required_credits,
                'spring_core_credits': result.spring_core_credits,
                'autumn_core_credits': result.autumn_core_credits,
                'numerical_logic_credits': result.numerical_logic_credits,
                'spring_limited_credits': result.spring_limited_credits,
                'autumn_limited_credits': result.autumn_limited_credits,
                'short_term_training_credits': result.short_term_training_credits,
                'international_credits': result.international_credits,
                'elective_credits': result.elective_credits,
                'outmajor_credits': result.outmajor_credits,
                'culture_core_credits': result.culture_core_credits,
                'culture_choose_credits': result.culture_choose_credits,
                'culture_total_credits': result.culture_total_credits,
                'innovation_credits': result.innovation_credits
            })

        return jsonify(result_list)
    except Exception as e:
        app.logger.error(f"数据获取失败: {str(e)}")
        return jsonify({'error': str(e)}), 500
@app.route('/delete', methods=['POST', 'OPTIONS'])
def delete_record():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        print(f"接收到的数据: {data}")  # 打印接收到的请求数据
        student_name = data.get('student_name')
        major = data.get('major')

        if not student_name or not major:
            return jsonify({'error': 'Student name and major are required'}), 400

        # 查找要删除的记录
        record = CreditResult.query.filter_by(student_name=student_name, major=major).first()
        if record is None:
            return jsonify({'error': 'Record not found'}), 404

        # 删除记录
        db.session.delete(record)
        db.session.commit()
        return jsonify({'message': 'Record deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 批量删除路由也需要添加 OPTIONS 方法
@app.route('/delete_batch', methods=['POST', 'OPTIONS'])
def delete_records():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json()
        print(f"接收到的数据: {data}")  # 打印接收到的请求数据
        records = data.get('records')  # 接收前端传来的多个记录
        
        if not records:
            return jsonify({'error': 'No records to delete'}), 400

        for record in records:
            student_name = record.get('student_name')
            major = record.get('major')

            if not student_name or not major:
                return jsonify({'error': f'Student name and major are required for {record}'}), 400

            # 查找并删除记录
            db_record = CreditResult.query.filter_by(student_name=student_name, major=major).first()
            if db_record:
                db.session.delete(db_record)
            else:
                print(f"No record found for student {student_name} with major {major}")

        db.session.commit()  # 提交一次性提交所有删除操作
        return jsonify({'message': 'Records deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/search', methods=['GET'])
def search_records():
    query = request.args.get('query', '')
    
    # 根据关键词在数据库中进行模糊查询
    results = CreditResult.query.filter(
        (CreditResult.student_name.like(f'%{query}%')) | 
        (CreditResult.major.like(f'%{query}%'))
    ).all()

    # 将查询结果转换为 JSON 格式返回
    records = [{
        'student_name': result.student_name,
        'major': result.major,
        'spring_required_credits': result.spring_required_credits,
        'autumn_required_credits': result.autumn_required_credits,
        'spring_core_credits': result.spring_core_credits,
        'autumn_core_credits': result.autumn_core_credits,
        'numerical_logic_credits': result.numerical_logic_credits,
        'spring_limited_credits': result.spring_limited_credits,
        'autumn_limited_credits': result.autumn_limited_credits,
        'short_term_training_credits': result.short_term_training_credits,
        'international_credits': result.international_credits,
        'elective_credits': result.elective_credits,
        'outmajor_credits': result.outmajor_credits,
        'culture_core_credits': result.culture_core_credits,
        'culture_choose_credits': result.culture_choose_credits,
        'culture_total_credits': result.culture_total_credits,
        'innovation_credits': result.innovation_credits
    } for result in results]

    return jsonify(records)
# 启动 Flask 应用
if __name__ == '__main__':
    with app.app_context():  # 确保数据库操作在应用上下文中执行
        db.create_all()  # 创建数据库表
    app.run(debug=True)
