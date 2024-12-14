#计算选修课学分：素质选修和素质核心，mooc按选修处理，先放在核心，再放到选修

import pymysql

#得到课程-学分对应的对象数组
def getMoocCourses_credits(cursor,student_table):
    try:
        mooc_query = f"""
            SELECT course_name, credits
            FROM {student_table}
            WHERE course_nature = '任选'
              AND (course_category = 'MOOC' OR course_category = '新生研讨' OR course_category = 'MOOC(艺术与审美)')
              AND (final_grade >= 60 OR final_grade = '免修');
        """
        cursor.execute(mooc_query)
        mooc_courses = cursor.fetchall()
        return mooc_courses
    except Exception as e:
            print(f"发生错误：{e}")
            return 0
    
#这个方案暂时弃用，因为感觉像01背包
def calculate_culture_credits(cursor, student_table):
    try:
        # 查询素质核心课程学分
        core_query = f"""
            SELECT course_name, credits
            FROM {student_table}
            WHERE (course_category = '素质核心' OR course_category = '素质核心（艺术与审美）' OR course_category = '素质核心（四史）')
              AND (final_grade >= 60 OR final_grade = '免修');
        """
        cursor.execute(core_query)
        core_courses = cursor.fetchall()
        total_culture_core_credits = sum(course['credits'] for course in core_courses)

        # 查询素质选修课程学分
        choose_query = f"""
            SELECT course_name, credits
            FROM {student_table}
            WHERE course_nature = '任选'
              AND (course_category = '素质选修' OR course_category = '素质选修（艺术与审美）' OR course_category = '素质选修（四史）')
              AND (final_grade >= 60 OR final_grade = '免修');
        """
        cursor.execute(choose_query)
        choose_courses = cursor.fetchall()
        total_culture_choose_credits = sum(course['credits'] for course in choose_courses)

        # 查询MOOC课程学分，因为需要按照具体课程进行补充
        mooc_courses = getMoocCourses_credits(cursor,student_table)
        total_mooc_credits = sum(course['credits'] for course in mooc_courses)

        # 计算素质核心和素质选修的补充情况
        remaining_core_credits = 4 - total_culture_core_credits  # 素质核心需要补充的学分
        remaining_choose_credits = 5 - total_culture_choose_credits  # 素质选修需要补充的学分

        # 按课程逐一补充MOOC学分
        mooc_courses_sorted = sorted(mooc_courses, key=lambda x: x['credits'], reverse=True)  # 按学分从大到小排序
        for course in mooc_courses_sorted:
            course_credits = course['credits']

            # 首先补充到素质核心课程
            if remaining_core_credits > 0:
                #当前mooc课程学分<=核心差的学分
                if course_credits <= remaining_core_credits:
                    #核心总学分增加，差的学分减少
                    total_culture_core_credits += course_credits
                    remaining_core_credits -= course_credits
                #当前课程大于时
                else:
                    total_culture_core_credits += remaining_core_credits
                    remaining_core_credits = 0
                    total_culture_choose_credits += (course_credits - remaining_core_credits)

            # 如果还有剩余的MOOC学分，补充到素质选修课程
            elif remaining_choose_credits > 0:
                if course_credits <= remaining_choose_credits:
                    total_culture_choose_credits += course_credits
                    remaining_choose_credits -= course_credits
                else:
                    total_culture_choose_credits += remaining_choose_credits
                    remaining_choose_credits = 0
                    # 这个 MOOC 的多余学分就不再使用

        # 返回总学分
        return total_culture_core_credits + total_culture_choose_credits + total_mooc_credits

    except Exception as e:
        print(f"发生错误：{e}")
        return 0
