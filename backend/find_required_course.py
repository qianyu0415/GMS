# find_required_course.py
from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def process_courses(student_table, required_course_table):
    """
    处理单个学生表和课程要求表，返回春季、秋季必修课学分
    首先先把对应专业的required和学生表相连进行选择
    因为英语比较特殊（required里面都是“大学外语”），所以单独计算
    返回时加载一起
    """
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

    # 定义查询逻辑
    english_query = text(f"""
        SELECT
            SUM(CASE WHEN s.academic_year LIKE "%春季%" THEN s.credits ELSE 0 END) AS spring_credits,
            SUM(CASE WHEN s.academic_year LIKE "%秋季%" THEN s.credits ELSE 0 END) AS autumn_credits
        FROM `{student_table}` s
        WHERE s.course_category = "英语"
        AND s.final_grade >= 60;
    """)

    # 执行查询并提取结果
    with engine.connect() as connection:
        result = connection.execute(english_query).fetchone()

    # 解析查询结果
    english_spring_credits = result[0] if result and result[0] is not None else 0
    english_autumn_credits = result[1] if result and result[1] is not None else 0



    return spring_credits+english_spring_credits, autumn_credits+english_autumn_credits

# 测试用例
# spring_credits, autumn_credits = process_courses('乔宇凡_2021113352_计算机科学与技术', 'required_course_1')
# print(f"Spring Credits: {spring_credits}, Autumn Credits: {autumn_credits}")