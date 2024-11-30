import pymysql
from find_required_course import process_courses
from find_core_course import process_core_course
from decimal import Decimal

# 模拟获取学生专业的函数
def get_major(student_table):
    parts = student_table.split('_')
    if len(parts) == 3:
        return parts[2]  # 返回专业
    return None

# 根据专业获取对应的必修课表
def get_required_course_table(major):
    if major in ["计算机科学与技术", "物联网工程", "数据科学与大数据技术", "人工智能", "生物信息学"]:
        return 'required_course_1'
    elif major == "软件工程":
        return 'required_course_2'
    elif major in ["信息安全", "网络空间安全"]:
        return 'required_course_3'
    return None

# 获取专业对应的核心课表
def get_core_course_table(major):
    if major == "计算机科学与技术":
        return 'core_course_1'
    elif major == "数据科学与大数据技术":
        return 'core_course_2'
    elif major == "人工智能":
        return 'core_course_3'
    elif major == "网络空间安全":
        return 'core_course_4'
    elif major == "信息安全":
        return 'core_course_5'
    elif major == "软件工程":
        return 'core_course_6'
    elif major == "物联网工程":
        return 'core_course_7'
    elif major == "生物信息学":
        return 'core_course_8'
    return None

# 连接到数据库并获取学生表信息
def calculate_credits_for_all_students(db_config):
    # 使用上下文管理连接到数据库
    with pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        cursorclass=pymysql.cursors.DictCursor  # 返回字典格式的结果
    ) as connection:
        try:
            with connection.cursor() as cursor:
                # 获取所有符合条件的学生表
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                
                # 学生表信息
                student_tables = []
                for table in tables:
                    table_name = list(table.values())[0]
                    # 假设学生表名是以"_"分隔的格式，且包含3个部分
                    if '_' in table_name and len(table_name.split('_')) == 3:
                        student_tables.append(table_name)
                
                # 用于存储每个表的学分计算结果
                all_credits_result = {}
                
                # 遍历每个学生表并计算学分
                for student_table in student_tables:
                    major = get_major(student_table)
                    required_course_table = get_required_course_table(major)
                    core_course_table = get_core_course_table(major)

                    # 检查是否成功获取必修课和核心课表
                    if required_course_table and core_course_table:
                        try:
                            # process_courses 返回三个值
                            spring_required_credits, autumn_required_credits, missing_courses = process_courses(student_table, required_course_table)
                            
                            # process_core_course 返回三个值
                            spring_core_credits, autumn_core_credits, missing_course_names = process_core_course(student_table, core_course_table)
                        except Exception as e:
                            print(f"跳过表 {student_table}，原因：调用 process_courses 或 process_core_course 时出错：{e}")
                            continue
                    else:
                        print(f"跳过表 {student_table}，原因：无法获取必修课或核心课表")
                        continue

                    # 使用原始的学分计算逻辑
                    try:
                        # 数字逻辑课程学分
                        numerical_logic_query = f"""
                            SELECT SUM(credits) AS total_numerical_logic_credits
                            FROM {student_table}
                            WHERE course_name = '数字逻辑与数字系统设计'
                              AND final_grade >= 60;
                        """
                        cursor.execute(numerical_logic_query)
                        numerical_logic_credits = float(cursor.fetchone()['total_numerical_logic_credits'] or 0)

                        # 专业限选课程学分
                        limited_courses_query = f"""
                            SELECT SUM(credits) AS total_limited_credits
                            FROM {student_table}
                            WHERE course_nature = '限选'
                              AND course_category = '其他'
                              AND course_name NOT IN ('企业短期实训', '数字逻辑与数字系统设计', '专业实践')
                              AND final_grade >= 60;
                        """
                        cursor.execute(limited_courses_query)
                        total_limited_credits = float(cursor.fetchone()['total_limited_credits'] or 0)

                        # 春季限选课程学分
                        spring_limited_query = f"""
                            SELECT SUM(credits) AS spring_limited_credits
                            FROM {student_table}
                            WHERE course_nature = '限选'
                              AND course_category = '其他'
                              AND course_name NOT IN ('企业短期实训', '数字逻辑与数字系统设计', '专业实践')
                              AND final_grade >= 60
                              AND academic_year LIKE '%春季%';
                        """
                        cursor.execute(spring_limited_query)
                        spring_limited_credits = float(cursor.fetchone()['spring_limited_credits'] or 0)

                        # 秋季限选课程学分
                        autumn_limited_query = f"""
                            SELECT SUM(credits) AS autumn_limited_credits
                            FROM {student_table}
                            WHERE course_nature = '限选'
                              AND course_category = '其他'
                              AND course_name NOT IN ('企业短期实训', '数字逻辑与数字系统设计', '专业实践')
                              AND final_grade >= 60
                              AND academic_year LIKE '%秋季%';
                        """
                        cursor.execute(autumn_limited_query)
                        autumn_limited_credits = float(cursor.fetchone()['autumn_limited_credits'] or 0)

                        # 企业短期实训/专业实践学分
                        short_term_training_query = f"""
                            SELECT SUM(credits) AS total_short_term_training_credits
                            FROM {student_table}
                            WHERE course_name IN ('企业短期实训', '专业实践')
                              AND final_grade >= 60;
                        """
                        cursor.execute(short_term_training_query)
                        total_short_term_training_credits = float(cursor.fetchone()['total_short_term_training_credits'] or 0)

                        # 国际化课程学分
                        international_courses_query = f"""
                            SELECT SUM(credits) AS total_international_credits
                            FROM {student_table}
                            WHERE course_name IN (
                                '电子商务技术与研究前沿', '服务计算前沿技术', '高级软件测试', '开源软件开发',
                                '人工智能与媒体大数据', '数字媒体的交互设计与开发', '虚空间中的人工智能和计算机视觉技术',
                                '演化计算', '多媒体信息处理与安全', '人工智能在计算机视觉中的应用', '人工智能与机器学习',
                                '人工智能及其应用', '图模型和概率推理'
                            ) AND final_grade >= 60;
                        """
                        cursor.execute(international_courses_query)
                        total_international_credits = float(cursor.fetchone()['total_international_credits'] or 0)

                        # 专业选修课学分
                        elective_courses_query = f"""
                            SELECT SUM(credits) AS total_elective_credits
                            FROM {student_table}
                            WHERE course_nature = '选修'
                              AND course_category = '其他'
                              AND course_name NOT IN ('生物化学B', '分子生物学', '遗传学B')
                              AND final_grade >= 60;
                        """
                        cursor.execute(elective_courses_query)
                        total_elective_credits = float(cursor.fetchone()['total_elective_credits'] or 0)

                        # 外专业课程学分
                        outmajor_courses_query_1 = f"""
                            SELECT SUM(credits) AS total_outmajor_credits_1
                            FROM {student_table}
                            WHERE course_nature = '选修'
                              AND course_category = '外专业课程'
                              AND credits >= 2
                              AND final_grade >= 60;
                        """
                        cursor.execute(outmajor_courses_query_1)
                        total_outmajor_credits_1 = float(cursor.fetchone()['total_outmajor_credits_1'] or 0)

                        outmajor_courses_query_2 = f"""
                            SELECT SUM(credits) AS total_outmajor_credits_2
                            FROM {student_table}
                            WHERE course_name IN ('生物化学B', '分子生物学', '遗传学B')
                              AND final_grade >= 60;
                        """
                        cursor.execute(outmajor_courses_query_2)
                        total_outmajor_credits_2 = float(cursor.fetchone()['total_outmajor_credits_2'] or 0)
                        total_outmajor_credits = total_outmajor_credits_1 + total_outmajor_credits_2

                        # 素质核心和素质选修学分
                        culture_core_courses_query = f"""
                            SELECT SUM(credits) AS total_culture_core_credits
                            FROM {student_table}
                            WHERE course_nature = '任选'
                              AND (course_category = '素质核心' OR course_category = '素质核心（艺术与审美）')
                              AND final_grade >= 60;
                        """
                        cursor.execute(culture_core_courses_query)
                        total_culture_core_credits = float(cursor.fetchone()['total_culture_core_credits'] or 0)

                        culture_choose_courses_query = f"""
                            SELECT SUM(credits) AS total_culture_choose_credits
                            FROM {student_table}
                            WHERE course_nature = '任选'
                              AND course_category = '素质选修'
                              AND final_grade >= 60;
                        """
                        cursor.execute(culture_choose_courses_query)
                        total_culture_choose_credits = float(cursor.fetchone()['total_culture_choose_credits'] or 0)

                        mooc_courses_query = f"""
                            SELECT SUM(credits) AS total_mooc_credits
                            FROM {student_table}
                            WHERE course_nature = '任选'
                              AND (course_category = 'MOOC' OR course_category = '新生研讨')
                              AND final_grade >= 60;
                        """
                        cursor.execute(mooc_courses_query)
                        total_mooc_credits = float(cursor.fetchone()['total_mooc_credits'] or 0)

                        total_culture_credits = total_culture_core_credits + total_culture_choose_credits + total_mooc_credits

                        # 创新创业学分
                        innovation_courses_query = f"""
                            SELECT SUM(credits) AS total_innovation_credits
                            FROM {student_table}
                            WHERE course_nature = '任选'
                              AND course_category IN ('创新创业', '创新MOOC', '创新研修')
                              AND final_grade >= 60;
                        """
                        cursor.execute(innovation_courses_query)
                        total_innovation_credits = float(cursor.fetchone()['total_innovation_credits'] or 0)

                        # 存储当前学生表的结果，包括原始和新增的学分计算
                        all_credits_result[student_table] = {
                            'spring_required_credits': spring_required_credits,
                            'autumn_required_credits': autumn_required_credits,
                            'spring_core_credits': spring_core_credits,
                            'autumn_core_credits': autumn_core_credits,
                            'numerical_logic_credits': numerical_logic_credits,
                            'spring_limited_credits': spring_limited_credits,
                            'autumn_limited_credits': autumn_limited_credits,
                            'short_term_training_credits': total_short_term_training_credits,
                            'international_credits': total_international_credits,
                            'elective_credits': total_elective_credits,
                            'outmajor_credits': total_outmajor_credits,
                            'culture_core_credits':total_culture_core_credits,
                            'culture_choose_credits':total_culture_choose_credits,
                            'culture_total_credits': total_culture_credits,
                            'innovation_credits': total_innovation_credits
                        }

                        # 插入数据到 credit_results 表
                        insert_query = """
                            INSERT INTO credit_results (
                                student_name, student_id, major, spring_required_credits, autumn_required_credits,
                                spring_core_credits, autumn_core_credits, numerical_logic_credits,
                                spring_limited_credits, autumn_limited_credits, short_term_training_credits,
                                international_credits, elective_credits, outmajor_credits, culture_core_credits,
                                culture_choose_credits, culture_total_credits, innovation_credits
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE 
                                spring_required_credits = VALUES(spring_required_credits),
                                autumn_required_credits = VALUES(autumn_required_credits),
                                spring_core_credits = VALUES(spring_core_credits),
                                autumn_core_credits = VALUES(autumn_core_credits),
                                numerical_logic_credits = VALUES(numerical_logic_credits),
                                spring_limited_credits = VALUES(spring_limited_credits),
                                autumn_limited_credits = VALUES(autumn_limited_credits),
                                short_term_training_credits = VALUES(short_term_training_credits),
                                international_credits = VALUES(international_credits),
                                elective_credits = VALUES(elective_credits),
                                outmajor_credits = VALUES(outmajor_credits),
                                culture_core_credits = VALUES(culture_core_credits),
                                culture_choose_credits = VALUES(culture_choose_credits),
                                culture_total_credits = VALUES(culture_total_credits),
                                innovation_credits = VALUES(innovation_credits)
                        """

                        # 提取学生表名的学生信息并格式化数据
                        try:
                            student_name, student_id, major = student_table.split('_')
                        except ValueError:
                            print(f"跳过表 {student_table}，原因：学生表名格式不正确")
                            continue

                        values = (
                            student_name, student_id, major,
                            float(spring_required_credits), float(autumn_required_credits),
                            float(spring_core_credits), float(autumn_core_credits),
                            float(numerical_logic_credits), float(spring_limited_credits),
                            float(autumn_limited_credits), float(total_short_term_training_credits),
                            float(total_international_credits), float(total_elective_credits),
                            float(total_outmajor_credits), float(total_culture_core_credits),
                            float(total_culture_choose_credits), float(total_culture_core_credits + total_culture_choose_credits),
                            float(total_innovation_credits)
                        )

                        # 执行插入或更新
                        cursor.execute(insert_query, values)

                    except Exception as e:
                        print(f"跳过表 {student_table}，原因：{e}")
                        continue
                
                # 提交插入操作
                connection.commit()

        except Exception as e:
            print(f"发生错误：{e}")

# 数据库配置文件
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'credits_db'
}

# 计算所有学生表的各项学分并插入数据库
calculate_credits_for_all_students(db_config)
