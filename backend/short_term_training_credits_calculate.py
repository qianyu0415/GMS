from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

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


def calculate_short_term_training_credits(student_table):
    """
    根据学生表名动态计算企业短期实训和专业实践学分。
    软件工程专业仅计算 '企业短期实训'，其他专业计算 '企业短期实训' 和 '专业实践'。
    """
    major = extract_major(student_table)
    if not major:
        print(f"无效的学生表名：{student_table}")
        return 0

    # 根据专业选择计算逻辑
    if major == "软件工程":
        query = text(f"""
            SELECT SUM(credits) AS total_short_term_training_credits
            FROM `{student_table}`
            WHERE course_name = '企业短期实训'
              AND (final_grade >= 60 OR final_grade = '免修');
        """)
    else:
        query = text(f"""
            SELECT SUM(credits) AS total_short_term_training_credits
            FROM `{student_table}`
            WHERE course_name IN ('企业短期实训', '专业实践')
              AND (final_grade >= 60 OR final_grade = '免修');
        """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().fetchone()
            return float(result['total_short_term_training_credits'] or 0)
    except Exception as e:
        print(f"发生错误：{e}")
        return 0
    
# if __name__ == "__main__":
#     # 测试软件工程专业
#     student_table = '乔宇凡_2021113352_计算机科学与技术'
#     credits = calculate_short_term_training_credits(student_table)
#     print(f"{student_table} 的企业短期实训总学分为：{credits}")

#     # 测试其他专业
#     student_table = '任奕杨_2021112514_软件工程'
#     credits = calculate_short_term_training_credits(student_table)
#     print(f"{student_table} 的企业短期实训和专业实践总学分为：{credits}")
