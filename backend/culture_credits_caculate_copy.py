from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

from decimal import Decimal

def get_mooc_credits(student_table):
    """
    从学生表中查询 MOOC 类课程的学分并返回一个列表及其总和。
    :param student_table: 学生课程表名称
    :return: 一个元组 (MOOC 类课程的学分列表, 学分总和)
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
            result = connection.execute(query).mappings().fetchall()

        # 提取学分到列表
        credits_list = [float(row['credits']) for row in result]  # 将 Decimal 转为 float

        total_credits = sum(credits_list)  # 计算学分总和


        # 返回学分列表和总和
        return credits_list, total_credits

    except Exception as e:
        print(f"发生错误：{e}")
        return [], 0



def calculate_culture_credits(student_table):
    """
    计算素质核心和素质选修的总学分，并从 MOOC 学分中进行补充。
    :param student_table: 学生课程表名称
    :return: 总学分（素质核心 + 素质选修 + MOOC），以及最终的 MOOC 学分列表
    """
    try:
        # 查询素质核心课程学分
        core_query = text(f"""
            SELECT SUM(credits)
            FROM `{student_table}`
            WHERE (course_category = '素质核心'
                OR course_category = '素质核心（艺术与审美）'
                OR course_category = '素质核心（四史）')
            AND (final_grade >= 60 OR final_grade = '免修');
        """)
        # 查询素质选修课程学分
        choose_query = text(f"""
            SELECT SUM(credits)
            FROM `{student_table}`
            WHERE course_nature = '任选'
              AND (course_category = '素质选修' 
                   OR course_category = '素质选修（艺术与审美）' 
                   OR course_category = '素质选修（四史）')
              AND (final_grade >= 60 OR final_grade = '免修');
        """)

        with engine.connect() as connection:
            # 素质核心课程学分
            core_result = connection.execute(core_query).mappings().fetchall()
            total_culture_core_credits = float(core_result[0]['SUM(credits)']) if core_result[0]['SUM(credits)'] else 0

            # 素质选修课程学分
            choose_result = connection.execute(choose_query).mappings().fetchall()
            total_culture_choose_credits = float(choose_result[0]['SUM(credits)']) if choose_result[0]['SUM(credits)'] else 0
        # print("未补充之前的",total_culture_core_credits,total_culture_choose_credits)

        # 获取 MOOC 课程学分列表和总和
        mooc_credits, mooc_total = get_mooc_credits(student_table)
        # 素质课程总学分（未分配mooc之前的）
        total_culture_credits = total_culture_core_credits + total_culture_choose_credits + mooc_total
        # print("total",total_culture_credits)


        # 按照规则补充学分
        remaining_mooc_credits = sorted(mooc_credits, reverse=True)  # 按从大到小排序，优先使用大的学分
        # print(f"初始 MOOC 学分池：{remaining_mooc_credits}")

        # 补充素质核心课程学分到 5 分
        required_core_credits = max(0, 5 - total_culture_core_credits)
        for i, credit in enumerate(remaining_mooc_credits):
            if required_core_credits <= 0:
                break
            if credit <= required_core_credits:
                total_culture_core_credits += credit
                required_core_credits -= credit
                remaining_mooc_credits[i] = 0  # 使用完置为 0
            else:
                total_culture_core_credits += required_core_credits
                remaining_mooc_credits[i] -= required_core_credits
                required_core_credits = 0

        # 清除已使用的 MOOC 学分
        remaining_mooc_credits = [credit for credit in remaining_mooc_credits if credit > 0]

        # 补充素质选修课程学分到 4 分
        required_choose_credits = max(0, 4 - total_culture_choose_credits)
        for i, credit in enumerate(remaining_mooc_credits):
            if required_choose_credits <= 0:
                break
            if credit <= required_choose_credits:
                total_culture_choose_credits += credit
                required_choose_credits -= credit
                remaining_mooc_credits[i] = 0  # 使用完置为 0
            else:
                total_culture_choose_credits += required_choose_credits
                remaining_mooc_credits[i] -= required_choose_credits
                required_choose_credits = 0

        # 清除已使用的 MOOC 学分
        remaining_mooc_credits = [credit for credit in remaining_mooc_credits if credit > 0]


        # 返回学分结果(分配之后的核心、选修，未分配的核心+选修+mooc)
        return total_culture_core_credits, total_culture_choose_credits, total_culture_credits

    except Exception as e:
        print(f"发生错误：{e}")
        return 0, 0, 0, []

# # 测试代码
# if __name__ == "__main__":
#     student_tables = [
#         "任婷婷_2021111018_计算机科学与技术",
#         "任宇飞_2021113130_计算机科学与技术",
#         "任荣剑_2021113036_信息安全",
#         "任鼎_2021112380_信息安全",
#         "何宜庚_2021110775_数据科学与大数据技术",
#         "何栩晟_2021113634_计算机科学与技术",
#         "何正海_2021111502_软件工程",
#         "余弦_2021112893_生物信息学",
#         "侯志一_2021110853_计算机科学与技术",
#         "傅瑞_2021110667_数据科学与大数据技术",
#         "冯梓硕_2021111392_信息安全",
#     ]
#     for student_table in student_tables:
#         core_credits, choose_credits, total_credits, remaining_mooc = calculate_culture_credits(student_table)
#         print(f"{student_table} 的素质课程学分为：核心={core_credits}，选修={choose_credits}，总计={total_credits}")
#         print(f"剩余的 MOOC 学分池：{remaining_mooc}")