import os
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import pymysql
from models import db, CreditResult
from sqlalchemy import text
from course_checker import check_missing_courses  # 查找缺失课程
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



# 检查文件扩展名是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 初始化学生表
@app.route('/upload', methods=['POST'])
def upload_file():
    # 确保有文件上传
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400

    file = request.files['file']

    # 确保文件是 Excel 文件
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': '请上传有效的 Excel 文件'}), 400

    # 保存文件到临时目录
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # 读取 Excel 数据
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return jsonify({'error': f'读取 Excel 文件失败: {str(e)}'}), 500

    # 使用 SQLAlchemy 的连接进行数据库操作
    with db.engine.connect() as connection:
        # 遍历每个学生，创建动态表并插入数据
        for (student_id, student_name, major), student_data in df.groupby(['学号', '姓名', '专业']):
            # 规范化表名，避免以数字开头
            table_name = f"{student_name}_{student_id}_{major}"

            # 创建学生表的 SQL 查询
            create_table_query = text(f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                course_name VARCHAR(100) NOT NULL,
                academic_year VARCHAR(20),
                course_nature VARCHAR(20),
                course_category VARCHAR(20),
                final_grade VARCHAR(20),
                retake_remark VARCHAR(20),
                credits DECIMAL(3, 1),
                major VARCHAR(20)
            );
            """)

            try:
                connection.execute(create_table_query)
            except Exception as e:
                print(f"创建表 {table_name} 时出错: {e}")
                continue  # 如果创建表失败，跳过此学生

            # 插入学生的选课信息
            for index, row in student_data.iterrows():
                insert_query = text(f"""
                INSERT INTO `{table_name}` (course_name, academic_year, course_nature, course_category, final_grade, retake_remark, credits, major)
                VALUES (:course_name, :academic_year, :course_nature, :course_category, :final_grade, :retake_remark, :credits, :major);
                """)
                try:
                    connection.execute(insert_query, {
                        'course_name': row['课程名称'],
                        'academic_year': row['学年学期'],
                        'course_nature': row['课程性质'],
                        'course_category': row['课程类别'],
                        'final_grade': row['最终成绩'],
                        'retake_remark': row.get('补考重修标记', ''),
                        'credits': row['学分'],
                        'major': row['专业']
                    })
                except Exception as e:
                    print(f"插入数据到 {table_name} 时出错: {e}")
                    continue  # 如果插入数据失败，跳过此行

    # 提交更改
    try:
        db.session.commit()
        return jsonify({'message': '学生选课信息已成功存储在数据库中。'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"提交更改时出错: {e}"}), 500

# 删除所有学生表
@app.route('/delete_all_student_tables', methods=['POST'])
def delete_all_student_tables():
    try:
        # 使用更严格的条件来筛选符合命名格式的表
        with db.engine.connect() as connection:
            # 查询符合 student_name_student_id_major 格式的表
            # 假设 student_id 为 10 位数字
            get_tables_query = text("SHOW TABLES LIKE '%\_%__________\_%'")
            result = connection.execute(get_tables_query)
            tables_to_delete = [row[0] for row in result.fetchall()]

            # 删除找到的所有表
            for table_name in tables_to_delete:
                drop_table_query = text(f"DROP TABLE IF EXISTS `{table_name}`")
                connection.execute(drop_table_query)
        
        return jsonify({'message': '所有符合格式的学生表已成功删除。'}), 200

    except Exception as e:
        return jsonify({'error': f"删除学生表时出错: {e}"}), 500
    
# 路由：检查缺失课程
@app.route('/check_missing_courses', methods=['POST'])
def handle_check_missing_courses():
    data = request.json
    result, status_code = check_missing_courses(data)
    return jsonify(result), status_code

# # 处理多个 Excel 文件上传和解析
# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         app.logger.error('没有文件上传')
#         return jsonify({'error': '没有文件上传'}), 400

#     files = request.files.getlist('file')  # 获取多个文件
#     if len(files) == 0:
#         app.logger.error('没有选择文件')
#         return jsonify({'error': '没有选择文件'}), 400

#     results = []  # 存储所有文件处理的结果

#     for file in files:
#         if not allowed_file(file.filename):
#             app.logger.error('不支持的文件格式: %s', file.filename)
#             return jsonify({'error': f'不支持的文件格式: {file.filename}'}), 400

#         # 保存文件到上传目录
#         filename = file.filename
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)

#         app.logger.info(f"文件保存成功: {file_path}")

#         # 解析文件名确定专业
#         current_major = extract_major_from_filename(filename)
#         if current_major is None:
#             app.logger.error('无法识别专业，文件名: %s', filename)
#             return jsonify({'error': f'无法识别专业，文件名: {filename}'}), 400

#         # 读取并处理 Excel 文件
#         try:
#             df = pd.read_excel(file_path)

#             # 通过 current_major 获取该专业对应的核心课程
#             result = calculate_credits(df, current_major)

#             # 从前端获取 student_name 和 major
#             student_name = request.form.get('student_name', '未命名学生')
#             major = request.form.get('major', '未命名专业')

#             # 将结果存储到数据库
#             credit_entry = CreditResult(
#                 student_name=student_name,
#                 major=major,
#                 spring_required_credits=result['春季必修学分'],
#                 autumn_required_credits=result['秋季必修学分'],
#                 spring_core_credits=result['春季核心课程学分'],
#                 autumn_core_credits=result['秋季核心课程学分'],
#                 numerical_logic_credits=result['数字逻辑学分'],
#                 spring_limited_credits=result['春季限选学分'],
#                 autumn_limited_credits=result['秋季限选学分'],
#                 short_term_training_credits=result['企业短期实训/专业实践学分'],
#                 international_credits=result['国际化课程学分'],
#                 elective_credits=result['专业选修学分'],
#                 outmajor_credits=result['外专业学分'],
#                 culture_core_credits=result['素质核心学分'],
#                 culture_choose_credits=result['素质选修学分'],
#                 culture_total_credits=result['文化素质教育学分'],
#                 innovation_credits=result['创新创业学分']
#             )

#             db.session.add(credit_entry)
#             db.session.commit()

#             # 添加处理结果到结果列表
#             results.append({filename: result})

#         except Exception as e:
#             app.logger.error('文件解析失败: %s', str(e))
#             return jsonify({'error': str(e)}), 500

#     # 返回所有文件的处理结果
#     return jsonify(results)

@app.route('/data', methods=['GET'])
def get_data():
    try:
        # 从数据库中查询所有 CreditResult 数据
        credit_results = CreditResult.query.all()
        
        # 将查询结果转换为 JSON 格式
        result_list = []
        for result in credit_results:
            result_list.append({
                'student_name': result.student_name,
                'student_id': result.student_id,  # 使用 student_id 而不是 id
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

# @app.route('/delete', methods=['POST', 'OPTIONS'])
# def delete_record():
#     if request.method == 'OPTIONS':
#         return '', 200
#     try:
#         data = request.get_json()
#         print(f"接收到的数据: {data}")  # 打印接收到的请求数据
#         student_name = data.get('student_name')
#         major = data.get('major')

#         if not student_name or not major:
#             return jsonify({'error': 'Student name and major are required'}), 400

#         # 查找要删除的记录
#         record = CreditResult.query.filter_by(student_name=student_name, major=major).first()
#         if record is None:
#             return jsonify({'error': 'Record not found'}), 404

#         # 删除记录
#         db.session.delete(record)
#         db.session.commit()
#         return jsonify({'message': 'Record deleted successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# 批量删除路由也需要添加 OPTIONS 方法
# @app.route('/delete_batch', methods=['POST', 'OPTIONS'])
# def delete_records():
#     if request.method == 'OPTIONS':
#         return '', 200
#     try:
#         data = request.get_json()
#         print(f"接收到的数据: {data}")  # 打印接收到的请求数据
#         records = data.get('records')  # 接收前端传来的多个记录
        
#         if not records:
#             return jsonify({'error': 'No records to delete'}), 400

#         for record in records:
#             student_name = record.get('student_name')
#             major = record.get('major')

#             if not student_name or not major:
#                 return jsonify({'error': f'Student name and major are required for {record}'}), 400

#             # 查找并删除记录
#             db_record = CreditResult.query.filter_by(student_name=student_name, major=major).first()
#             if db_record:
#                 db.session.delete(db_record)
#             else:
#                 print(f"No record found for student {student_name} with major {major}")

#         db.session.commit()  # 提交一次性提交所有删除操作
#         return jsonify({'message': 'Records deleted successfully'}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/search', methods=['GET'])
# def search_records():
#     query = request.args.get('query', '')
    
#     # 根据关键词在数据库中进行模糊查询
#     results = CreditResult.query.filter(
#         (CreditResult.student_name.like(f'%{query}%')) | 
#         (CreditResult.major.like(f'%{query}%'))
#     ).all()

#     # 将查询结果转换为 JSON 格式返回
#     records = [{
#         'student_name': result.student_name,
#         'major': result.major,
#         'spring_required_credits': result.spring_required_credits,
#         'autumn_required_credits': result.autumn_required_credits,
#         'spring_core_credits': result.spring_core_credits,
#         'autumn_core_credits': result.autumn_core_credits,
#         'numerical_logic_credits': result.numerical_logic_credits,
#         'spring_limited_credits': result.spring_limited_credits,
#         'autumn_limited_credits': result.autumn_limited_credits,
#         'short_term_training_credits': result.short_term_training_credits,
#         'international_credits': result.international_credits,
#         'elective_credits': result.elective_credits,
#         'outmajor_credits': result.outmajor_credits,
#         'culture_core_credits': result.culture_core_credits,
#         'culture_choose_credits': result.culture_choose_credits,
#         'culture_total_credits': result.culture_total_credits,
#         'innovation_credits': result.innovation_credits
#     } for result in results]

    # return jsonify(records)
# 启动 Flask 应用
if __name__ == '__main__':
    with app.app_context():  # 确保数据库操作在应用上下文中执行
        db.create_all()  # 创建数据库表
    app.run(debug=True)
