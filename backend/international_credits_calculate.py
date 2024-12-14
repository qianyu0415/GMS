from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def calculate_international_credits(student_table):
    """
    计算国际化课程总学分。

    :param student_table: 学生课程表名称
    :return: 国际化课程总学分
    """
    try:
        # 国际化课程表名
        international_course_table = "international"

        # 查询国际化课程的所有课程名
        course_query = text(f"SELECT course_name FROM {international_course_table};")
        with engine.connect() as connection:
            courses = connection.execute(course_query).mappings().fetchall()
        
        # 提取课程名，如果没有课程，返回0
        if not courses:
            print("国际化课程表为空，无法计算学分。")
            return 0

        # 提取课程名到列表
        course_names = [course['course_name'] for course in courses]
        
        # 构建查询条件，使用IN子句动态插入课程名
        placeholders = ', '.join([f":course_name_{i}" for i in range(len(course_names))])
        query = text(f"""
            SELECT SUM(credits) AS total_international_credits
            FROM `{student_table}`
            WHERE course_name IN ({placeholders})
              AND (final_grade >= 60 OR final_grade = '免修');
        """)

        # 构建动态参数字典
        params = {f"course_name_{i}": course_names[i] for i in range(len(course_names))}
        
        # 执行查询
        with engine.connect() as connection:
            result = connection.execute(query, params).mappings().fetchone()
        
        # 提取结果
        if result is None or result['total_international_credits'] is None:
            return 0
        return float(result['total_international_credits'])

    except Exception as e:
        print(f"发生错误：{e}")
        return 0


# 测试用例  
# def main():
#     student_table = '乔宇凡_2021113352_计算机科学与技术'
#     international_course_table = 'international'
    
#     total_credits = calculate_international_credits(student_table, international_course_table)
#     print(f"国际化课程总学分为：{total_credits}")

# if __name__ == '__main__':
#     main()