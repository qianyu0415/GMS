from sqlalchemy import text
from db_config import get_engine

def extract_major(student_table):
    """
    从学生表名中提取专业名称。
    格式为：姓名_学号_专业
    """
    try:
        return student_table.split('_')[2]
    except IndexError:
        print(f"无法从表名中提取专业：{student_table}")
        return None

def calculate_outmajor_credits(student_table):
    """
    计算外专业课程的总学分。
    规则：
    - 其他专业：外专业课程 + ('生物化学B', '分子生物学')
    - 生物信息学：必须选 ('生物化学B', '分子生物学')

    :param student_table: 学生课程表名称
    :return: 外专业课程总学分
    """
    # 提取专业名称
    major = extract_major(student_table)
    if not major:
        print(f"无法确定学生专业：{student_table}")
        return 0

    try:
        # 创建数据库引擎
        engine = get_engine()

        # 通用查询
        if major == "生物信息学":
            query = text(f"""
                SELECT SUM(credits) AS total_outmajor_credits
                FROM `{student_table}`
                WHERE course_name IN ('生物化学B', '分子生物学')
                  AND (final_grade >= 60 OR final_grade = '免修');
            """)
        else:
            query = text(f"""
                SELECT SUM(credits) AS total_outmajor_credits
                FROM `{student_table}`
                WHERE (course_category = '外专业课程' OR course_name IN ('生物化学B', '分子生物学'))
                  AND credits >= 2
                  AND (final_grade >= 60 OR final_grade = '免修');
            """)

        # 执行查询
        with engine.connect() as connection:
            result = connection.execute(query).mappings().fetchone()

        # 提取结果
        if result is None or result['total_outmajor_credits'] is None:
            return 0
        return float(result['total_outmajor_credits'])

    except Exception as e:
        print(f"发生错误：{e}")
        return 0

# # 测试代码
# if __name__ == "__main__":
#     # 示例学生表
#     student_table = '余弦_2021112893_生物信息学'
#     credits = calculate_outmajor_credits(student_table)
#     print(f"{student_table} 的外专业课程总学分为：{credits}")

#     student_table = '乔宇凡_2021113352_计算机科学与技术'
#     credits = calculate_outmajor_credits(student_table)
#     print(f"{student_table} 的外专业课程总学分为：{credits}")
