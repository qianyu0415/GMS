from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def process_core_course(student_table, core_course):
    """
    处理单个学生表和专业核心课表，不需要春秋学分，只需要总学分
    """

    # 计算已选的核心课程春季和秋季总学分
    # credits_query = text(f"""
    #     SELECT 
    #         SUM(CASE WHEN s.academic_year LIKE '%春季%' THEN rc.credits ELSE 0 END) AS spring_credits,
    #         SUM(CASE WHEN s.academic_year LIKE '%秋季%' THEN rc.credits ELSE 0 END) AS autumn_credits
    #     FROM `{core_course}` rc
    #     JOIN `{student_table}` s
    #         ON rc.course_name = s.course_name
    #     WHERE s.course_name IS NOT NULL;
    # """)
    credits_query = text(f"""
            SELECT 
                SUM(s.credits)
            FROM `{core_course}` rc
            JOIN `{student_table}` s
                ON rc.course_name = s.course_name
            WHERE s.course_name IS NOT NULL;
        """)

    with engine.connect() as connection:
            credits_result = connection.execute(credits_query).fetchone()

    # 提取总学分
    total_credits = credits_result[0] if credits_result and credits_result[0] is not None else 0

    return total_credits

# 测试用例
# total = process_core_course('乔宇凡_2021113352_计算机科学与技术', 'core_course_1')
# print("dd",total)

