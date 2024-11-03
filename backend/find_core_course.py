import os
from sqlalchemy import create_engine, text

# 数据库连接配置
db_config = 'mysql+pymysql://root:123456@localhost:3306/credits_db'

# 创建数据库连接
engine = create_engine(db_config)

def process_core_course(student_table, core_course):
    """
    处理单个学生表和专业核心课表，返回春季学分、秋季学分和缺失课程列表。
    """
    # 找出未选修的课程，仅输出该专业的核心课程
    missing_query = text(f"""
        SELECT
            rc.course_name,
            rc.credits
        FROM `{core_course}` rc
        LEFT JOIN `{student_table}` s
            ON rc.course_name = s.course_name
        WHERE s.course_name IS NULL 
          AND rc.course_name IS NOT NULL;
    """)

    with engine.connect() as connection:
        result = connection.execute(missing_query).fetchall()

    # 记录未选修课程的名称
    missing_courses = [(row[0], row[1]) for row in result]  # 包含课程名和学分

    # 计算已选的核心课程春季和秋季总学分
    credits_query = text(f"""
        SELECT 
            SUM(CASE WHEN s.academic_year LIKE '%春季%' THEN rc.credits ELSE 0 END) AS spring_credits,
            SUM(CASE WHEN s.academic_year LIKE '%秋季%' THEN rc.credits ELSE 0 END) AS autumn_credits
        FROM `{core_course}` rc
        JOIN `{student_table}` s
            ON rc.course_name = s.course_name
        WHERE s.course_name IS NOT NULL;
    """)

    with engine.connect() as connection:
        credits_result = connection.execute(credits_query).fetchone()

    spring_credits = credits_result.spring_credits if credits_result and credits_result.spring_credits is not None else 0
    autumn_credits = credits_result.autumn_credits if credits_result and credits_result.autumn_credits is not None else 0

    # 只保留缺失课程名用于输出
    missing_course_names = [course[0] for course in missing_courses]

    return spring_credits, autumn_credits, missing_course_names


