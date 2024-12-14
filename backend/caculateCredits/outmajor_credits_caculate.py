#计算外专业课程
#其他专业：外专业+('生物化学B', '分子生物学')
#生物信息专业：必须选('生物化学B', '分子生物学')

def calculate_outmajor_credits(cursor, student_table):
    #其他专业两种情况
    query_1 = f"""
        SELECT SUM(credits) AS total_outmajor_credits_1
        FROM {student_table} s
        WHERE (s.course_category = '外专业课程' OR s.course_name IN ('生物化学B', '分子生物学'))
          AND s.credits >= 2
          AND (s.final_grade >= 60 OR s.final_grade = '免修');
    """
    cursor.execute(query_1)
    total_outmajor_credits_1 = float(cursor.fetchone()['total_outmajor_credits_1'] or 0)
    #生物信息专业
    query_2 = f"""
        SELECT SUM(credits) AS total_outmajor_credits_2
        FROM {student_table}
        WHERE course_name IN ('生物化学B', '分子生物学')
          AND (s.final_grade >= 60 OR s.final_grade = '免修');
    """
    cursor.execute(query_2)
    total_outmajor_credits_2 = float(cursor.fetchone()['total_outmajor_credits_2'] or 0)

    return total_outmajor_credits_1 + total_outmajor_credits_2
