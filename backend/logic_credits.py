from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def calculate_numerical_logic_credits(student_table):
    """
    计算数字逻辑课程的总学分。
    软件工程无需修数字逻辑课程，最终返回时减去 0 即可。
    """
    query = text(f"""
        SELECT SUM(credits) AS total_numerical_logic_credits
        FROM `{student_table}`
        WHERE course_name IN ('数字逻辑与数字系统设计', '数字逻辑设计')
          AND (final_grade >= 60 OR final_grade = '免修');
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().fetchone()
            # 提取学分值
            return float(result['total_numerical_logic_credits'] or 0)
    except Exception as e:
        print(f"发生错误：{e}")
        return 0
    
# # 测试用例  
# def main():
#     student_table = '乔宇凡_2021113352_计算机科学与技术'
    
#     total_credits = calculate_numerical_logic_credits(student_table)
#     print(f"数字逻辑总学分为：{total_credits}")

# if __name__ == '__main__':
#     main()