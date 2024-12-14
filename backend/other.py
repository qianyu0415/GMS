from find_required_course import process_courses    # 必修课
from find_core_course import process_core_course    # 核心课
# 专业对应核心、必修、限选表
from major2table import get_core_course_table,get_limited_course_table,get_required_course_table
from limited_credits_calculate import process_calculate_limited  # 专业限选课
from logic_credits import calculate_numerical_logic_credits # 数字逻辑课
from short_term_training_credits_calculate import calculate_short_term_training_credits # 企业短期实训
from international_credits_calculate import calculate_international_credits # 国际化课程
from major_selected_calculate import calculate_major_selected_credits #专业选修课
from outmajor_credits_calculate import calculate_outmajor_credits # 外专业课程
from culture_credits_calculate import calculate_culture_credits # 素质核心、素质选修、MOOC
from innovation_credits_calculate import calculate_innovation_credits # 创新学分

# 获取学生表中专业的函
def get_major(student_table):
    parts = student_table.split('_')
    if len(parts) == 3:
        return parts[2]  # 返回专业
    return None

# 获取学生表中姓名的函数
def get_name(student_table):
    parts = student_table.split('_')
    if len(parts) == 3:
        return parts[0]
    return None

# 根据专业获取对应的必修课表
# def get_required_course_table(major):
#     if major in ["计算机科学与技术", "物联网工程", "数据科学与大数据技术", "人工智能", "生物信息学"]:
#         return 'required_course_1'
#     elif major == "软件工程":
#         return 'required_course_2'
#     elif major in ["信息安全", "网络空间安全"]:
#         return 'required_course_3'
#     return None

# 获取专业对应的核心课表
# def get_core_course_table(major):
#     if major == "计算机科学与技术":
#         return 'core_course_1'
#     elif major == "数据科学与大数据技术":
#         return 'core_course_2'
#     elif major == "人工智能":
#         return 'core_course_3'
#     elif major == "网络空间安全":
#         return 'core_course_4'
#     elif major == "信息安全":
#         return 'core_course_5'
#     elif major == "软件工程":
#         return 'core_course_6'
#     elif major == "物联网工程":
#         return 'core_course_7'
#     elif major == "生物信息学":
#         return 'core_course_8'
#     return None

# 数字逻辑课程学分计算
# def calculate_numerical_logic_credits(cursor, student_table):
#     query = f"""
#         SELECT SUM(credits) AS total_numerical_logic_credits
#         FROM {student_table}
#         WHERE course_name = '数字逻辑与数字系统设计'
#           AND final_grade >= 60;
#     """
#     cursor.execute(query)
#     result = cursor.fetchone()
#     return float(result['total_numerical_logic_credits'] or 0)

# 专业限选课程学分计算（春季、秋季分开）
# def calculate_limited_credits(cursor, student_table):
#     spring_query = f"""
#         SELECT SUM(credits) AS spring_limited_credits
#         FROM {student_table}
#         WHERE course_nature = '限选'
#           AND course_category = '其他'
#           AND course_name NOT IN ('企业短期实训', '数字逻辑与数字系统设计', '专业实践')
#           AND final_grade >= 60
#           AND academic_year LIKE '%春季%';
#     """
#     cursor.execute(spring_query)
#     spring_limited_credits = float(cursor.fetchone()['spring_limited_credits'] or 0)

#     autumn_query = f"""
#         SELECT SUM(credits) AS autumn_limited_credits
#         FROM {student_table}
#         WHERE course_nature = '限选'
#           AND course_category = '其他'
#           AND course_name NOT IN ('企业短期实训', '数字逻辑与数字系统设计', '专业实践')
#           AND final_grade >= 60
#           AND academic_year LIKE '%秋季%';
#     """
#     cursor.execute(autumn_query)
#     autumn_limited_credits = float(cursor.fetchone()['autumn_limited_credits'] or 0)

#     return spring_limited_credits, autumn_limited_credits

# 企业短期实训/专业实践学分计算
# def calculate_short_term_training_credits(cursor, student_table):
#     query = f"""
#         SELECT SUM(credits) AS total_short_term_training_credits
#         FROM {student_table}
#         WHERE course_name IN ('企业短期实训', '专业实践')
#           AND final_grade >= 60;
#     """
#     cursor.execute(query)
#     result = cursor.fetchone()
#     return float(result['total_short_term_training_credits'] or 0)

# 国际化课程学分计算
# def calculate_international_credits(cursor, student_table):
#     query = f"""
#         SELECT SUM(credits) AS total_international_credits
#         FROM {student_table}
#         WHERE course_name IN (
#             '电子商务技术与研究前沿', '服务计算前沿技术', '高级软件测试', '开源软件开发',
#             '人工智能与媒体大数据', '数字媒体的交互设计与开发', '虚空间中的人工智能和计算机视觉技术',
#             '演化计算', '多媒体信息处理与安全', '人工智能在计算机视觉中的应用', '人工智能与机器学习',
#             '人工智能及其应用', '图模型和概率推理'
#         ) AND final_grade >= 60;
#     """
#     cursor.execute(query)
#     result = cursor.fetchone()
#     return float(result['total_international_credits'] or 0)

# 专业选修课学分计算
# def calculate_elective_credits(cursor, student_table):
#     query = f"""
#         SELECT SUM(credits) AS total_elective_credits
#         FROM {student_table}
#         WHERE course_nature = '选修'
#           AND course_category = '其他'
#           AND course_name NOT IN ('生物化学B', '分子生物学', '遗传学B')
#           AND final_grade >= 60;
#     """
#     cursor.execute(query)
#     result = cursor.fetchone()
#     return float(result['total_elective_credits'] or 0)

# 外专业课程学分计算
# def calculate_outmajor_credits(cursor, student_table):
#     query_1 = f"""
#         SELECT SUM(credits) AS total_outmajor_credits_1
#         FROM {student_table}
#         WHERE course_nature = '选修'
#           AND course_category = '外专业课程'
#           AND credits >= 2
#           AND final_grade >= 60;
#     """
#     cursor.execute(query_1)
#     total_outmajor_credits_1 = float(cursor.fetchone()['total_outmajor_credits_1'] or 0)

#     query_2 = f"""
#         SELECT SUM(credits) AS total_outmajor_credits_2
#         FROM {student_table}
#         WHERE course_name IN ('生物化学B', '分子生物学', '遗传学B')
#           AND final_grade >= 60;
#     """
#     cursor.execute(query_2)
#     total_outmajor_credits_2 = float(cursor.fetchone()['total_outmajor_credits_2'] or 0)

#     return total_outmajor_credits_1 + total_outmajor_credits_2

# 素质核心和素质选修学分计算
# def calculate_culture_credits(cursor, student_table):
#     core_query = f"""
#         SELECT SUM(credits) AS total_culture_core_credits
#         FROM {student_table}
#         WHERE course_nature = '任选'
#           AND (course_category = '素质核心' OR course_category = '素质核心（艺术与审美）')
#           AND final_grade >= 60;
#     """
#     cursor.execute(core_query)
#     total_culture_core_credits = float(cursor.fetchone()['total_culture_core_credits'] or 0)

#     choose_query = f"""
#         SELECT SUM(credits) AS total_culture_choose_credits
#         FROM {student_table}
#         WHERE course_nature = '任选'
#           AND course_category = '素质选修'
#           AND final_grade >= 60;
#     """
#     cursor.execute(choose_query)
#     total_culture_choose_credits = float(cursor.fetchone()['total_culture_choose_credits'] or 0)

#     mooc_query = f"""
#         SELECT SUM(credits) AS total_mooc_credits
#         FROM {student_table}
#         WHERE course_nature = '任选'
#           AND (course_category = 'MOOC' OR course_category = '新生研讨')
#           AND final_grade >= 60;
#     """
#     cursor.execute(mooc_query)
#     total_mooc_credits = float(cursor.fetchone()['total_mooc_credits'] or 0)

#     return total_culture_core_credits + total_culture_choose_credits + total_mooc_credits

# 创新创业学分计算
# def calculate_innovation_credits(cursor, student_table):
#     query = f"""
#         SELECT SUM(credits) AS total_innovation_credits
#         FROM {student_table}
#         WHERE course_nature = '任选'
#           AND course_category IN ('创新创业', '创新MOOC', '创新研修')
#           AND final_grade >= 60;
#     """
#     cursor.execute(query)
#     result = cursor.fetchone()
#     return float(result['total_innovation_credits'] or 0)



import logging
from sqlalchemy import text
from db_config import get_engine
import json

# 创建数据库引擎
engine = get_engine()

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def calculate_credits_for_all_students():
    """
    遍历所有学生表，计算学分并插入到 `credit_results` 表中。
    """
    try:
        with engine.connect() as connection:
            # 获取所有表
            result = connection.execute(text("SHOW TABLES;")).fetchall()
            # 筛选符合学生表规则的表名，同时排除包含 'limited_course' 的表名
            student_tables = [
                row[0]  # 直接访问元组中的第一个元素，即表名
                for row in result
                if len(row[0].split('_')) == 3  # 表名分割后恰好有三部分
                and 'limited_course' not in row[0]  # 排除包含 'limited_course' 的表
                and 'required_course' not in row[0]
                and 'core_course' not in row[0]
                and 'major_selected' not in row[0]
            ]
            for student_table in student_tables:  # 确保用 student_tables 而非 result
                logging.info(f"开始处理学生表: {student_table}")
                
                try:
                    # 检查表名是否符合 "学生名_学号_专业" 格式
                    student_name, student_id, major = student_table.split('_')
                    logging.info(f"学生: {student_name}, 学号: {student_id}, 专业: {major}")
                except ValueError:
                    logging.warning(f"跳过无效表名: {student_table}")
                    continue

                # 继续处理学分计算的逻辑
                required_course_table = get_required_course_table(major)
                core_course_table = get_core_course_table(major)
                limited_course_table = get_limited_course_table(major, student_name)

                if required_course_table and core_course_table and limited_course_table:
                    # 计算各项学分
                    spring_required_credits, autumn_required_credits = process_courses(student_table, required_course_table)
                    core_credits = process_core_course(student_table, core_course_table)
                    numerical_logic_credits = calculate_numerical_logic_credits(student_table)
                    limited_credits = process_calculate_limited(student_table, limited_course_table)
                    short_term_training_credits = calculate_short_term_training_credits(student_table)
                    international_credits = calculate_international_credits(student_table)
                    elective_credits = calculate_major_selected_credits(student_table)
                    outmajor_credits = calculate_outmajor_credits(student_table)
                    total_core_credits, total_choose_credits, MOOC = calculate_culture_credits(student_table)
                    innovation_credits = calculate_innovation_credits(student_table)

                    # 将 MOOC 列表转换为 JSON 格式
                    if isinstance(MOOC, list):
                        MOOC = json.dumps([float(x) for x in MOOC])

                    # 处理 None 值，避免插入数据库时产生问题
                    values = {
                        "student_name": student_name,
                        "student_id": student_id,
                        "major": major,
                        "spring_required_credits": spring_required_credits if spring_required_credits is not None else 0.0,
                        "autumn_required_credits": autumn_required_credits if autumn_required_credits is not None else 0.0,
                        "core_credits": core_credits if core_credits is not None else 0.0,
                        "numerical_logic_credits": numerical_logic_credits if numerical_logic_credits is not None else 0.0,
                        "limited_credits": limited_credits if limited_credits is not None else 0.0,
                        "short_term_training_credits": short_term_training_credits if short_term_training_credits is not None else 0.0,
                        "international_credits": international_credits if international_credits is not None else 0.0,
                        "elective_credits": elective_credits if elective_credits is not None else 0.0,
                        "outmajor_credits": outmajor_credits if outmajor_credits is not None else 0.0,
                        "culture_core_credits": total_core_credits if total_core_credits is not None else 0.0,
                        "culture_choose_credits": total_choose_credits if total_choose_credits is not None else 0.0,
                        "MOOC": MOOC,  # 确保 MOOC 是有效的 JSON 格式（字符串）
                        "innovation_credits": innovation_credits if innovation_credits is not None else 0.0,
                    }

                    # 插入或更新数据库
                    insert_query = text(""" 
                        INSERT INTO credit_results (
                            student_name, student_id, major, spring_required_credits, autumn_required_credits,
                            core_credits, numerical_logic_credits,
                            limited_credits, short_term_training_credits,
                            international_credits, elective_credits, outmajor_credits, culture_core_credits,
                            culture_choose_credits, MOOC,
                            innovation_credits
                        ) VALUES (
                            :student_name, :student_id, :major, :spring_required_credits, :autumn_required_credits,
                            :core_credits, :numerical_logic_credits,
                            :limited_credits, :short_term_training_credits,
                            :international_credits, :elective_credits, :outmajor_credits, :culture_core_credits,
                            :culture_choose_credits, :MOOC,
                            :innovation_credits
                        )
                        ON DUPLICATE KEY UPDATE
                            spring_required_credits = :spring_required_credits,
                            autumn_required_credits = :autumn_required_credits,
                            core_credits = :core_credits,
                            numerical_logic_credits = :numerical_logic_credits,
                            limited_credits = :limited_credits,
                            short_term_training_credits = :short_term_training_credits,
                            international_credits = :international_credits,
                            elective_credits = :elective_credits,
                            outmajor_credits = :outmajor_credits,
                            culture_core_credits = :culture_core_credits,
                            culture_choose_credits = :culture_choose_credits,
                            MOOC = :MOOC,
                            innovation_credits = :innovation_credits
                    """)

                    with engine.connect() as connection:
                        trans = connection.begin()  # 开启事务
                        try:
                            connection.execute(insert_query, values)
                            trans.commit()  # 提交事务
                            logging.info("测试数据插入成功")
                        except Exception as e:
                            trans.rollback()  # 出现错误时回滚
                            logging.error(f"测试数据插入失败: {e}")

            logging.info("所有学生学分计算完成并已写入数据库。")
    except Exception as e:
        logging.error(f"发生错误：{e}")

# # 执行函数
# calculate_credits_for_all_students()

