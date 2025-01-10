from find_required_course import process_courses    # 必修课
from find_core_course import process_core_course    # 核心课
# 专业对应核心、必修、限选表
from major2table import get_core_course_table,get_limited_course_table,get_required_course_table,get_elective_course_table
from limited_credits_calculate import process_calculate_limited  # 专业限选课
from logic_credits import calculate_numerical_logic_credits # 数字逻辑课
from short_term_training_credits_calculate import calculate_short_term_training_credits # 企业短期实训
from international_credits_calculate import calculate_international_credits # 国际化课程
from major_selected_calculate import calculate_major_selected_credits #专业选修课
from outmajor_credits_calculate import calculate_outmajor_credits # 外专业课程
from culture_credits_caculate_copy import calculate_culture_credits # 素质核心、素质选修、MOOC
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
    遍历所有学生表，计算学分差值并将其覆盖存储到 `credit_results` 表中。
    """
    try:
        # 获取所有表
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES;")).fetchall()
        
        # 筛选符合学生表规则的表名，同时排除包含 'limited_course' 的表名
        student_tables = [
            row[0]
            for row in result
            if len(row[0].split('_')) == 3
            and 'limited_course' not in row[0]
            and 'required_course' not in row[0]
            and 'core_course' not in row[0]
            and 'major_selected' not in row[0]
        ]
        
        for student_table in student_tables:
            logging.info(f"开始处理学生表: {student_table}")
            
            try:
                # 检查表名是否符合 "学生名_学号_专业" 格式
                student_name, student_id, major = student_table.split('_')
                logging.info(f"学生: {student_name}, 学号: {student_id}, 专业: {major}")
            except ValueError:
                logging.warning(f"跳过无效表名: {student_table}")
                continue

            # 对于每个学生，创建独立的数据库连接
            with engine.connect() as connection:
                # 查询专业的学分要求
                query = text("""
                    SELECT *
                    FROM credits_db.credit_distribution
                    WHERE major = :major
                """)
                major_requirements = connection.execute(query, {"major": major}).mappings().fetchone()
                print("dd",major_requirements)
                if not major_requirements:
                    logging.warning(f"未找到专业 {major} 的学分要求，跳过学生 {student_name}")
                    continue

                # 继续处理学分计算的逻辑
                required_course_table = get_required_course_table(major)
                core_course_table = get_core_course_table(major)
                limited_course_table = get_limited_course_table(major, student_name)
                elective_course_table = get_elective_course_table(major)

                if required_course_table and core_course_table and limited_course_table:
                    # 计算各项学分
                    total_required_credits = process_courses(student_table, required_course_table) # 必修不分春秋
                    core_credits = process_core_course(student_table, core_course_table) # 专业核心
                    numerical_logic_credits = calculate_numerical_logic_credits(student_table) # 数字逻辑
                    limited_credits = process_calculate_limited(student_table, limited_course_table) # 专业限选
                    short_term_training_credits = calculate_short_term_training_credits(student_table) # 短期实训
                    international_credits = calculate_international_credits(student_table) # 国际化课程
                    elective_credits = calculate_major_selected_credits(student_table,elective_course_table) # 专业选修
                    outmajor_credits = calculate_outmajor_credits(student_table) # 外专业
                    total_core_credits, total_choose_credits,culture_mooc_total_credits = calculate_culture_credits(student_table) # 文化素质核心、文化素质选修、核心+选修+mooc
                    innovation_credits = calculate_innovation_credits(student_table) # 创新



                    # 计算学分差值并覆盖原有列
                    values = {
                        "student_name": student_name,
                        "student_id": student_id,
                        "major": major,
                        "total_required_credits": total_required_credits - (major_requirements["total_required_credits"] or 0),
                        # "autumn_total_required_credits": autumn_total_required_credits - (major_requirements["autumn_total_required_credits"] or 0),
                        "core_credits": core_credits - (major_requirements["core_credits"] or 0),
                        "numerical_logic_credits": numerical_logic_credits - (major_requirements["numerical_logic_credits"] or 0),
                        "limited_credits": limited_credits - (major_requirements["limited_credits"] or 0),
                        "short_term_training_credits": short_term_training_credits - (major_requirements["short_term_training_credits"] or 0),
                        "international_credits": international_credits - (major_requirements["international_credits"] or 0),
                        "elective_credits": elective_credits - (major_requirements["elective_credits"] or 0),
                        "outmajor_credits": outmajor_credits - (major_requirements["outmajor_credits"] or 0),
                        "culture_core_credits": total_core_credits - (major_requirements["culture_core_credits"] or 0),
                        "culture_choose_credits": total_choose_credits - (major_requirements["culture_choose_credits"] or 0),
                        "culture_mooc_total_credits": (culture_mooc_total_credits or 0) - (major_requirements.get("culture_mooc_total_credits", 0)),                    
                        "innovation_credits": innovation_credits - (major_requirements["innovation_credits"] or 0),
                    }
                    # 插入或更新数据库
                    insert_query = text(""" 
                        INSERT INTO credits_db.credit_results (
                            student_name, student_id, major, total_required_credits,
                            core_credits, numerical_logic_credits, limited_credits, short_term_training_credits,
                            international_credits, elective_credits, outmajor_credits, culture_core_credits,
                            culture_choose_credits,culture_mooc_total_credits, innovation_credits
                        ) VALUES (
                            :student_name, :student_id, :major, :total_required_credits, 
                            :core_credits, :numerical_logic_credits, :limited_credits, :short_term_training_credits,
                            :international_credits, :elective_credits, :outmajor_credits, :culture_core_credits,
                            :culture_choose_credits,:culture_mooc_total_credits, :innovation_credits
                        )
                        ON DUPLICATE KEY UPDATE
                            total_required_credits = :total_required_credits,

                            core_credits = :core_credits,
                            numerical_logic_credits = :numerical_logic_credits,
                            limited_credits = :limited_credits,
                            short_term_training_credits = :short_term_training_credits,
                            international_credits = :international_credits,
                            elective_credits = :elective_credits,
                            outmajor_credits = :outmajor_credits,
                            culture_core_credits = :culture_core_credits,
                            culture_choose_credits = :culture_choose_credits,
                            culture_mooc_total_credits = :culture_mooc_total_credits,
                            innovation_credits = :innovation_credits
                    """)

                    try:
                        connection.execute(insert_query, values)
                        connection.commit()  # 提交事务
                        logging.info("数据插入成功")
                        
                    except Exception as e:
                        connection.rollback()  # 出现异常时回滚事务
                        logging.error(f"数据插入失败: {e}")

            logging.info(f"学生表 {student_table} 处理完成。")

    except Exception as e:
        logging.error(f"发生错误：{e}")

# # 执行函数
# calculate_credits_for_all_students()
