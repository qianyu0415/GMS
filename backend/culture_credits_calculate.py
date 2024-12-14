from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def get_mooc_credits(student_table):
    """
    从学生表中查询 MOOC 类课程的学分并返回一个列表。
    :param student_table: 学生课程表名称
    :return: MOOC 类课程的学分列表
    """
    try:
        # SQL 查询，用于选择符合条件的 MOOC 类课程及其学分
        query = text(f"""
            SELECT credits
            FROM `{student_table}`
            WHERE course_nature = '任选'
              AND (course_category = 'MOOC' 
                   OR course_category = '新生研讨' 
                   OR course_category = 'MOOC(艺术与审美)')
              AND (final_grade >= 60 OR final_grade = '免修');
        """)

        # 执行查询
        with engine.connect() as connection:
            result = connection.execute(query).fetchall()

        # 提取学分到列表
        credits_list = [row[0] for row in result]  # 注意 fetchall 返回元组
        return credits_list

    except Exception as e:
        print(f"发生错误：{e}")
        return []


def calculate_culture_credits(student_table):
    """
    查询并返回素质核心和素质选修的总学分。
    :param student_table: 学生课程表名称
    :return: 核心学分、选修学分、MOOC 学分列表
    """
    try:
        # 查询素质核心课程学分
        core_query = text(f"""
            SELECT SUM(credits) AS total_core_credits
            FROM `{student_table}`
            WHERE (course_category = '素质核心'
                OR course_category = '素质核心（艺术与审美）'
                OR course_category = '素质核心（四史）')
            AND (final_grade >= 60 OR final_grade = '免修');
        """)
        # 查询素质选修课程学分
        choose_query = text(f"""
            SELECT SUM(credits) AS total_choose_credits
            FROM `{student_table}`
            WHERE course_nature = '任选'
              AND (course_category = '素质选修' 
                   OR course_category = '素质选修（艺术与审美）' 
                   OR course_category = '素质选修（四史）')
              AND (final_grade >= 60 OR final_grade = '免修');
        """)

        with engine.connect() as connection:
            # 素质核心课程学分
            core_result = connection.execute(core_query).fetchone()
            total_culture_core_credits = core_result[0] if core_result[0] else 0

            # 素质选修课程学分
            choose_result = connection.execute(choose_query).fetchone()
            total_culture_choose_credits = choose_result[0] if choose_result[0] else 0

        # 获取 MOOC 课程学分列表
        mooc_credits = get_mooc_credits(student_table)

        # 返回素质核心、素质选修学分及 MOOC 学分列表
        return total_culture_core_credits, total_culture_choose_credits, mooc_credits

    except Exception as e:
        print(f"发生错误：{e}")
        return 0, 0, []


# 测试代码
# if __name__ == "__main__":
#     student_tables = [
#         "乔宇凡_2021113352_计算机科学与技术",
#         "于佳宁_2021111811_物联网工程",
#         "付书煜_2021111824_软件工程",
#     ]

#     for student_table in student_tables:
#         total_core_credits, total_choose_credits, mooc_credits = calculate_culture_credits(student_table)
#         print(f"{student_table} 的素质核心学分：{total_core_credits}")
#         print(f"{student_table} 的素质选修学分：{total_choose_credits}")
#         print(f"{student_table} 的 MOOC 类课程学分列表：{mooc_credits}")
