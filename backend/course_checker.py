from flask import Flask, request
from sqlalchemy import create_engine, text
from major2table import get_core_course_table,get_required_course_table
app = Flask(__name__)

# 数据库配置
db_config = 'mysql+pymysql://root:123456@localhost:3306/credits_db'
engine = create_engine(db_config)

# 检查表是否存在
def table_exists(connection, table_name):
    check_query = text(f"SHOW TABLES LIKE '{table_name}'")
    result = connection.execute(check_query).fetchone()
    return result is not None

# 获取专业对应的必修课表或核心课表
# def get_course_table(major, course_type):
#     if course_type == "required":
#         if major in ["计算机科学与技术", "物联网工程", "数据科学与大数据技术", "人工智能", "生物信息学"]:
#             return 'required_course_1'
#         elif major == "软件工程":
#             return 'required_course_2'
#         elif major in ["信息安全", "网络空间安全"]:
#             return 'required_course_3'
#     elif course_type == "core":
#         if major == "计算机科学与技术":
#             return 'core_course_1'
#         elif major == "数据科学与大数据技术":
#             return 'core_course_2'
#         elif major == "人工智能":
#             return 'core_course_3'
#         elif major == "网络空间安全":
#             return 'core_course_4'
#         elif major == "信息安全":
#             return 'core_course_5'
#         elif major == "软件工程":
#             return 'core_course_6'
#         elif major == "物联网工程":
#             return 'core_course_7'
#         elif major == "生物信息学":
#             return 'core_course_8'
#     return None

# 根据前端传入的信息生成 student_table 名称
def generate_student_table(student_name, student_id, major):
    return f"{student_name}_{student_id}_{major}"

# 处理核心课程表，返回缺失的核心课程名称列表
def process_core_course(student_table, core_course):
    missing_query = text(f"""
        SELECT rc.course_name
        FROM `{core_course}` rc
        LEFT JOIN `{student_table}` s
            ON rc.course_name = s.course_name
        WHERE (s.course_name IS NULL OR s.final_grade < 60)
          AND rc.course_name IS NOT NULL;
    """)
    with engine.connect() as connection:
        result = connection.execute(missing_query).fetchall()

    return [row[0] for row in result]

# 处理必修课程表，返回缺失的必修课程名称列表，包含大学外语的逻辑

def process_required_course(student_table, required_course_table):
    # 找出未选修或未达标的课程
    missing_query = text(f"""
        SELECT DISTINCT rc.course_name, rc.academic_year
        FROM {required_course_table} rc
        LEFT JOIN {student_table} s
            ON rc.course_name = s.course_name 
        WHERE (s.course_name IS NULL OR s.final_grade < 60) 
        AND rc.course_name IS NOT NULL;
    """)

    with engine.connect() as connection:
        result = connection.execute(missing_query).fetchall()

    missing_courses = list(set((row[0], row[1]) for row in result))

    # 查找 student_table 中 course_category 为 "英语" 的学年
    english_query = text(f"""
        SELECT DISTINCT academic_year
        FROM {student_table}
        WHERE course_category = '英语';
    """)

    with engine.connect() as connection:
        english_academic_years = set(row[0] for row in connection.execute(english_query).fetchall())

    # 过滤掉在相同学年内有英语课程的“大学外语”课程
    missing_courses = [
        (course_name, academic_year)
        for course_name, academic_year in missing_courses
        if not (course_name == '大学外语' and academic_year in english_academic_years)
    ]

    # 体育课
    PE_courses_query = text(f"""
        SELECT DISTINCT rc.course_name, rc.academic_year
        FROM {required_course_table} rc
        LEFT JOIN {student_table} s
            ON rc.course_name = s.course_name
            AND rc.academic_year = s.academic_year
        WHERE (s.course_name IS NULL OR s.final_grade < 60)
        AND rc.course_name = '体育';  -- 筛选出体育课
    """)

    with engine.connect() as connection:
        PE_courses_result = connection.execute(PE_courses_query).fetchall()

    PE_courses = list(set((row[0], row[1]) for row in PE_courses_result))

    # 将体育课添加到缺失课程列表中
    missing_courses.extend(PE_courses)

    # 去重并排序（可选）
    missing_courses = sorted(list(set(missing_courses)), key=lambda x: (x[1], x[0]))

    return missing_courses

# 选择MOOC课程

# 处理学生课程信息，根据课程类别调用相应的处理函数
def check_missing_courses(data):
    student_name = data.get("student_name")
    student_id = data.get("student_id")
    major = data.get("major")
    course_types = data.get("course_type")

    # 检查必填参数
    if not all([student_name, student_id, major, course_types]):
        return {'error': '缺少必填参数'}, 400

    student_table = generate_student_table(student_name, student_id, major)
    missing_courses_result = {}

    with engine.connect() as connection:
        if not table_exists(connection, student_table):
            return {'error': f"学生表 {student_table} 不存在，无法处理。"}, 400

        for course_type in course_types:
            # 根据课程类别选择对应的表格
            print("dd",course_type)
            if "spring_required" in course_type:
                course_table = get_required_course_table(major)
                missing_courses = process_required_course(student_table, course_table)
                print("Missing Courses:", missing_courses)
                missing_courses_result.setdefault('专业必修课', []).extend(missing_courses)
            elif "core" in course_type:
                course_table = get_core_course_table(major)
                missing_courses = process_core_course(student_table, course_table)
                missing_courses_result.setdefault('专业核心课', []).extend(missing_courses)

    return missing_courses_result, 200
