from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def process_courses(student_table, required_course_table):
    """
    处理单个学生表和课程要求表，返回总必修课学分（不区分春秋学期）。
    包括普通必修课和英语课程。
    """
    # 查询普通必修课程的总学分
    credits_query = text(f"""
        SELECT SUM(s.credits)
        FROM `{required_course_table}` rc
        JOIN `{student_table}` s
        ON rc.course_name = s.course_name AND s.course_name != "体育"
        WHERE s.course_name IS NOT NULL;
    """)

    with engine.connect() as connection:
        credits_result = connection.execute(credits_query).fetchone()

    # 普通必修课总学分
    total_required_credits = credits_result[0] if credits_result and credits_result[0] is not None else 0

    # 查询英语课程的总学分
    english_query = text(f"""
        SELECT SUM(s.credits)
        FROM `{student_table}` s
        WHERE s.course_category = "英语"
        AND s.final_grade >= 60;
    """)

    with engine.connect() as connection:
        english_result = connection.execute(english_query).fetchone()

    # 查询体育
    PE_query = text(f"""
        select sum(s.credits)
        from `{student_table}` s
        where s.course_name = "体育"
        AND s.final_grade >= 60;
        """)
    
    with engine.connect() as connection:
        PE_result = connection.execute(PE_query).fetchone()

    # 体育课程总学分
    total_PE_credits = PE_result[0] if PE_result and PE_result[0] is not None else 0
    # 英语课程总学分
    total_english_credits = english_result[0] if english_result and english_result[0] is not None else 0

    # 计算总必修课学分（普通必修 + 英语）
    total_credits = total_required_credits + total_english_credits + total_PE_credits

    return total_credits

# 测试用例
# total_credits = process_courses('乔宇凡_2021113352_计算机科学与技术', 'required_course_1')
# print(f"Total Required Credits: {total_credits}")
