import pymysql

# 数据库配置，用于测试
# db_config = {
#     'host': 'localhost',
#     'port': 3306,
#     'user': 'root',
#     'password': '123456',
#     'database': 'credits_db'
# }

# 获取专业对应的限选表
def get_limited_course_table(major):
    major_to_table = {
        "计算机科学与技术": 'limited_course_1',
        "数据科学与大数据技术": 'limited_course_2',
        "人工智能": 'limited_course_3',
        "网络空间安全": 'limited_course_4',
        "信息安全": 'limited_course_5',
        "软件工程": 'limited_course_6',
        "物联网工程": 'limited_course_7',
        "生物信息学": 'limited_course_8'
    }
    return major_to_table.get(major)

# 计算专业限选课程学分
def process_calculate_limited(cursor, student_table, limited_course_table):
    try:
        # 定义查询语句
        query = f"""
            SELECT SUM(s.credits) AS total_credits
            FROM {student_table} s
            JOIN {limited_course_table} m ON s.course_name = m.course_name
            WHERE (s.final_grade >= 60 OR s.final_grade = '免修');
        """
        cursor.execute(query)
        result = cursor.fetchone()
        print(result)

        # 如果结果为空，则总学分为 0
        total_credits = result['total_credits'] if result and result['total_credits'] else 0
        return total_credits

    except Exception as e:
        print(f"发生错误: {e}")
        return None

# 主函数,该部分用于测试
# def main():
#     student_major = '计算机科学与技术'  # 示例专业
#     student_table = '乔宇凡_2021113352_计算机科学与技术'  # 示例学生课程表

#     # 获取对应的专业限选课程表
#     limited_course_table = get_limited_course_table(student_major)
#     if not limited_course_table:
#         print(f"未找到专业 {student_major} 对应的限选表。")
#         return

#     try:
#         # 连接到数据库
#         with pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor) as connection:
#             with connection.cursor() as cursor:
#                 # 计算学分
#                 total_credits = process_calculate_limited(cursor, student_table, limited_course_table)

#                 if total_credits is not None:
#                     print(f"学生专业 {student_major} 修过的限选课程总学分为: {total_credits}")
#                 else:
#                     print("无法计算学分总和。")

#     except Exception as e:
#         print(f"数据库连接或操作时发生错误: {e}")

# # 执行主函数，用于测试
# if __name__ == '__main__':
#     main()
