from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def calculate_innovation_credits(student_table):
    """
    计算创新创业学分总和。

    :param student_table: 学生课程表名称
    :return: 创新创业总学分
    """
    try:
        # 定义 SQL 查询
        query = text(f"""
            SELECT SUM(credits) AS total_innovation_credits
            FROM `{student_table}`
            WHERE course_nature = '任选'
              AND course_category IN ('创新创业', '创新MOOC', '创新研修', '创新实验')
              AND (final_grade >= 60 OR final_grade = '免修');
        """)

        # 执行查询
        with engine.connect() as connection:
            result = connection.execute(query).fetchone()

        # 提取学分结果
        total_innovation_credits = result[0] if result[0] is not None else 0
        return float(total_innovation_credits)

    except Exception as e:
        print(f"发生错误：{e}")
        return 0


# # 测试代码
# if __name__ == "__main__":
#     student_tables = [
#         "乔宇凡_2021113352_计算机科学与技术",
#         "于佳宁_2021111811_物联网工程",
#         "于哲_2021110826_计算机科学与技术",
#     ]

#     for student_table in student_tables:
#         innovation_credits = calculate_innovation_credits(student_table)
#         print(f"{student_table} 的创新创业总学分为：{innovation_credits}")
