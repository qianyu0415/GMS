from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def calculate_major_selected_credits(student_table):
    """
    根据学生表与 major_selected_courses 表的连接计算总学分。

    :param student_table: 学生课程表名称
    :return: 总学分
    """
    try:
        # SQL 查询
        query = text(f"""
            SELECT SUM(m.credits) AS total_credits
            FROM major_selected_courses m
            JOIN `{student_table}` s
            ON m.course_name = s.course_name;
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

# # 测试代码
# if __name__ == "__main__":
#     # 示例学生表
#     student_table = '乔宇凡_2021113352_计算机科学与技术'
#     total_credits = calculate_major_credits(student_table)
#     print(f"{student_table} 的总学分为：{total_credits}")
