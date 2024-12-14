from sqlalchemy import text
from db_config import get_engine
from major2table import get_sub_major,get_limited_course_table
# 创建数据库引擎
engine = get_engine()

def process_calculate_limited(student_table, limited_course_table):
    """
    计算学生修过的限选课程的总学分。
    """
    print("student:", student_table)
    print("limited:", limited_course_table)
    
    query = text(f"""
        SELECT SUM(s.credits) AS total_credits
        FROM {student_table} s
        JOIN {limited_course_table} m ON s.course_name = m.course_name
        WHERE (s.final_grade >= 60 OR s.final_grade = '免修');
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().fetchone()
            print("Query result:", result)
            total_credits = result['total_credits'] if result and result['total_credits'] else 0
            return total_credits
    except Exception as e:
        print(f"发生错误: {e}")
        return None

# 测试用例
# major = "软件工程"
# student = "任奕杨"
# limit_course = get_limited_course_table(major,student)
# print("dd",limit_course)
# process_calculate_limited("任奕杨_2021112514_软件工程",limit_course)
