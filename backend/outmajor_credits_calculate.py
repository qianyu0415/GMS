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
    - 软件工程：必须在两个表 (major_selected_accounting_finance 和 major_selected_marketing) 中选课，
      且总学分 > 4.5，成功返回 6，否则返回 0。
    - 生物信息学：必须选 ('生物化学B', '分子生物学')。
    - 其他专业：外专业课程 + ('生物化学B', '分子生物学')。

    :param student_table: 学生课程表名称
    :return: 成功返回 6，不成功返回 0。
    """
    # 提取专业名称
    major = extract_major(student_table)
    if not major:
        print(f"无法确定学生专业：{student_table}")
        return 0

    try:
        # 创建数据库引擎
        engine = get_engine()

        # 软件工程专业逻辑
        if major == "软件工程":
            # 查询两个表的学分总和
            query_accounting = text(f"""
                SELECT COUNT(*) AS course_count, SUM(credits) AS accounting_credits
                FROM major_selected_accounting_finance
                WHERE course_name IN (
                    SELECT course_name FROM `{student_table}`
                );
            """)
            query_marketing = text(f"""
                SELECT COUNT(*) AS course_count, SUM(credits) AS marketing_credits
                FROM major_selected_marketing
                WHERE course_name IN (
                    SELECT course_name FROM `{student_table}`
                );
            """)
            with engine.connect() as connection:
                # 获取两个表中的选课数量和学分
                accounting_result = connection.execute(query_accounting).mappings().fetchone()
                marketing_result = connection.execute(query_marketing).mappings().fetchone()

            # 解析查询结果
            accounting_courses = accounting_result['course_count'] or 0
            marketing_courses = marketing_result['course_count'] or 0
            accounting_credits = accounting_result['accounting_credits'] or 0.0
            marketing_credits = marketing_result['marketing_credits'] or 0.0
            total_credits = accounting_credits + marketing_credits

            # 判断条件
            if accounting_courses > 0 and marketing_courses > 0 and total_credits > 4.5:
                return 6  # 成功
            return 0  # 不成功

        # 生物信息学专业逻辑
        elif major == "生物信息学":
            query = text(f"""
                SELECT SUM(credits) AS total_outmajor_credits
                FROM `{student_table}`
                WHERE course_name IN ('生物化学B', '分子生物学')
                  AND (final_grade >= 60 OR final_grade = '免修');
            """)
            with engine.connect() as connection:
                result = connection.execute(query).mappings().fetchone()

            # 提取结果
            if result is None or result['total_outmajor_credits'] is None:
                return 0
            return 6 if float(result['total_outmajor_credits']) >= 4.5 else 0

        # 其他专业逻辑
        else:
            query = text(f"""
                SELECT SUM(credits) AS total_outmajor_credits
                FROM `{student_table}`
                WHERE (course_category = '外专业课程' OR course_name IN ('生物化学B', '分子生物学'))
                  AND credits >= 2
                  AND (final_grade >= 60 OR final_grade = '免修');
            """)
            with engine.connect() as connection:
                result = connection.execute(query).mappings().fetchone()

            # 提取结果
            if result is None or result['total_outmajor_credits'] is None:
                return 0
            return 6 if float(result['total_outmajor_credits']) >= 4.5 else 0

    except Exception as e:
        print(f"发生错误：{e}")
        return 0
    
def validate_software_engineering_requirements(data):
    """
    验证软件工程专业外专业课程是否满足要求。
    """
    # 提取数据中的参数
    student_name = data.get("student_name")
    student_id = data.get("student_id")
    major = data.get("major")
    course_types = data.get("course_types")

    # 检查是否为软件工程专业
    if major != "软件工程":
        return []  # 非软件工程专业不需要验证，返回空列表

    try:
        # 创建数据库引擎
        engine = get_engine()

        # 动态生成学生表名
        student_table = f"{student_name}_{student_id}_{major}"

        # 查询两个表的学分和选课数量
        query_accounting = text(f"""
            SELECT COUNT(*) AS course_count, SUM(credits) AS accounting_credits
            FROM major_selected_accounting_finance
            WHERE course_name IN (
                SELECT course_name
                FROM `{student_table}`
            );
        """)
        query_marketing = text(f"""
            SELECT COUNT(*) AS course_count, SUM(credits) AS marketing_credits
            FROM major_selected_marketing
            WHERE course_name IN (
                SELECT course_name
                FROM `{student_table}`
            );
        """)

        # 连接数据库并执行查询
        with engine.connect() as connection:
            accounting_result = connection.execute(query_accounting).mappings().fetchone()
            marketing_result = connection.execute(query_marketing).mappings().fetchone()

        # 如果查询结果为空，处理为默认值
        accounting_courses = accounting_result['course_count'] or 0
        marketing_courses = marketing_result['course_count'] or 0
        accounting_credits = accounting_result['accounting_credits'] or 0.0
        marketing_credits = marketing_result['marketing_credits'] or 0.0

        # 检查两个表的条件是否满足
        errors = []
        if accounting_courses == 0:
            errors.append("在 major_selected_accounting_finance 表中没有选课，未满足要求。")
        if marketing_courses == 0:
            errors.append("在 major_selected_marketing 表中没有选课，未满足要求。")
        if accounting_courses > 0 and marketing_courses > 0 and (accounting_credits + marketing_credits <= 4.5):
            errors.append(f"两个表中的学分总和不足 4.5（当前总学分：{accounting_credits + marketing_credits}），未满足要求。")

        # 如果存在错误，返回错误信息
        if errors:
            return errors

        # 满足所有条件
        return []

    except Exception as e:
        # 捕获异常并返回详细错误信息
        print(f"发生错误：{e}")
        return [f"数据库查询过程中发生错误，请检查系统配置。错误详情：{e}"]


# # 测试代码
# if __name__ == "__main__":
#     # 示例：软件工程学生
#     student_table = '刘乙钢_2021110706_软件工程'
#     result = calculate_outmajor_credits(student_table)
#     print(f"{student_table} 的外专业课程学分状态：{result}")

