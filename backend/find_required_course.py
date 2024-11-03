# find_required_course.py
import os
from sqlalchemy import create_engine, text

# 数据库连接配置
db_config = 'mysql+pymysql://root:123456@localhost:3306/credits_db'

# 创建数据库连接
engine = create_engine(db_config)

def process_courses(student_table, required_course_table):
    """
    处理单个学生表和课程要求表，返回春季学分、秋季学分和缺失课程列表。
    """
    # 找出未选修的课程
    missing_query = text(f"""
        SELECT
            rc.course_name,
            rc.academic_year,
            rc.credits
        FROM `{required_course_table}` rc
        LEFT JOIN `{student_table}` s
        ON rc.course_name = s.course_name AND rc.academic_year = s.academic_year
        WHERE s.course_name IS NULL AND rc.course_name IS NOT NULL AND rc.academic_year IS NOT NULL;
    """)

    with engine.connect() as connection:
        result = connection.execute(missing_query).fetchall()

    # 记录未选修课程的名称和学年
    missing_courses = [(row[0], row[1]) for row in result]

    # 计算已选课程的春季和秋季总学分
    credits_query = text(f"""
        SELECT 
            SUM(CASE WHEN rc.academic_year LIKE '%春季%' THEN rc.credits ELSE 0 END) AS spring_credits,
            SUM(CASE WHEN rc.academic_year LIKE '%秋季%' THEN rc.credits ELSE 0 END) AS autumn_credits
        FROM `{required_course_table}` rc
        JOIN `{student_table}` s
        ON rc.course_name = s.course_name AND rc.academic_year = s.academic_year
        WHERE s.course_name IS NOT NULL;
    """)

    with engine.connect() as connection:
        credits_result = connection.execute(credits_query).fetchone()

    spring_credits = credits_result[0] if credits_result and credits_result[0] is not None else 0
    autumn_credits = credits_result[1] if credits_result and credits_result[1] is not None else 0

    # 查找 `student_table` 表中 `course_category` 为 "英语" 的课程
    english_query = text(f"""
        SELECT academic_year
        FROM `{student_table}`
        WHERE course_category = '英语';
    """)

    with engine.connect() as connection:
        english_academic_years = [row[0] for row in connection.execute(english_query).fetchall()]

    # 移除在相同学年里 "大学外语" 的课程
    missing_courses = [
        (course_name, academic_year)
        for course_name, academic_year in missing_courses
        if not (course_name == '大学外语' and academic_year in english_academic_years)
    ]

    # 只保留课程名用于输出
    missing_course_names = [course[0] for course in missing_courses]

    return spring_credits, autumn_credits, missing_course_names
