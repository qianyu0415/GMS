import os
from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import pymysql
from models import db, CreditResult
from sqlalchemy import text
from course_checker import check_missing_courses  # 查找缺失课程
from other import calculate_credits_for_all_students  # 导入计算学分的函数
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

import re
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
            # 替换 student_name 中的空格为 '-'，并确保表名中无非法字符
            table_name = re.sub(r'[^\w\-一-龥]', '', f"{student_name.replace(' ', '-')}_{student_id}_{major}")
            table_name = table_name[:64]  # 限制表名长度

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
                print(f"创建表成功: {table_name}")
            except Exception as e:
                print(f"创建表 {table_name} 时出错: {e}")
                continue  # 如果创建表失败，跳过此学生

            # 插入学生的选课信息
            for _, row in student_data.iterrows():
                # 检查并处理 NaN 值
                row = row.fillna('')  # 替换所有 NaN 为空字符串

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
                        'credits': row['学分'] if not pd.isna(row['学分']) else 0,  # 将 NaN 替换为 0
                        'major': row['专业']
                    })
                except Exception as e:
                    print(f"插入数据到 {table_name} 时出错: {e}")
                    continue

    # 提交更改
    try:
        db.session.commit()

        # 调用学分计算函数，传递数据库配置
        db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '123456',
            'database': 'credits_db'
        }

        # 日志记录以跟踪学分计算状态
        print("开始学分计算...")
        calculate_credits_for_all_students()
        print("学分计算完成")

        return jsonify({'message': '学生选课信息已成功存储在数据库中，并完成学分计算。'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"提交更改时出错: {e}"}), 500





# 删除所有学生表
import logging
logging.basicConfig(level=logging.INFO)

@app.route('/delete_all_student_tables', methods=['GET'])
def delete_all_student_tables():
    try:
        with db.engine.connect() as connection:
            # 查询并删除符合条件的学生表
            get_tables_query = text("SHOW TABLES LIKE '%\\_%__________\\_%'")
            result = connection.execute(get_tables_query)
            tables_to_delete = [row[0] for row in result.fetchall()]
            for table_name in tables_to_delete:
                drop_table_query = text(f"DROP TABLE IF EXISTS `{table_name}`")
                connection.execute(drop_table_query)

            # 删除 credit_results 表中的所有记录
            delete_credit_results_query = text("DELETE FROM credit_results")
            connection.execute(delete_credit_results_query)
            print("Successfully executed DELETE FROM credit_results.")
            connection.commit()  # 使用 connection.commit() 明确提交事务

        return jsonify({'message': '所有符合格式的学生表及 credit_results 表中的记录已成功删除。'}), 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': f"删除学生表或 credit_results 记录时出错: {e}"}), 500

    
# 路由：检查缺失课程（必修课、专业核心课所差科目）
@app.route('/check_missing_courses', methods=['POST'])
def handle_check_missing_courses():
    data = request.json
    result, status_code = check_missing_courses(data)
    return jsonify(result), status_code

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
                'student_id': result.student_id,
                'major': result.major,
                # 春季秋季的必修未统计
                'total_required_credits': result.total_required_credits or 0,
                # 专业核心课
                'core_credits': result.core_credits or 0,
                # 数字逻辑3分
                'numerical_logic_credits': result.numerical_logic_credits or 0,
                # 春秋限选未统计
                'limited_credits': result.limited_credits or 0,
                # 企业短期实训&夏季实践：2分
                'short_term_training_credits': (result.short_term_training_credits or 0) ,
                # 国际化课程1分
                'international_credits': (result.international_credits or 0) ,
                # 专业选修课总分9分
                'elective_credits': (result.elective_credits or 0) ,
                # 外专业课程6分
                'outmajor_credits': (result.outmajor_credits or 0) ,
                # 素质核心4分
                'culture_core_credits': result.culture_core_credits or 0,
                # 素质选修5分
                'culture_choose_credits': result.culture_choose_credits or 0,
                # 素质核心 + 素质选秀 + mooc
                'culture_mooc_total_credits': result.culture_mooc_total_credits or 0,
                # 创新学分4分
                'innovation_credits': (result.innovation_credits or 0) 
            })

        return jsonify(result_list), 200
    except Exception as e:
        app.logger.error(f"数据获取失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 启动 Flask 应用
if __name__ == '__main__':
    with app.app_context():  # 确保数据库操作在应用上下文中执行
        db.create_all()  # 创建数据库表
    app.run(debug=True)
