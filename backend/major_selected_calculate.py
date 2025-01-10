from sqlalchemy import text
from db_config import get_engine
# 创建数据库引擎
engine = get_engine()

# 计算专业选修（表二）九学分
def calculate_major_selected_credits(student_table,elective_course_table):

    print("student:", student_table)
    print("electivte:", elective_course_table)
    try:
        # SQL 查询
        query = text(f"""
            SELECT SUM(m.credits) AS total_credits
            FROM `{elective_course_table}`m
            JOIN `{student_table}` s
            ON m.course_name = s.course_name
            WHERE (s.final_grade >= 60 OR s.final_grade = '免修');
        """)

        # 执行查询
        with engine.connect() as connection:
            result = connection.execute(query).mappings().fetchone()

        # 提取总学分
        if result is None or result['total_credits'] is None:
            return 0
        return float(result['total_credits'])

    except Exception as e:
        print(f"发生错误：{e}")
        return 0

# # 测试用例
# major = "软件工程"
# limit_course = get_elective_course_table(major)
# print("dd",limit_course)
# calculate_major_selected_credits("任奕杨_2021112514_软件工程",limit_course)

