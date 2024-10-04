import pandas as pd
from models import Course

# 从数据库获取专业核心课程
def get_core_courses_by_major(major_id):
    core_courses = Course.query.filter_by(major_id=major_id, course_type='专业核心').all()
    return [course.course_name for course in core_courses]

def calculate_credits(df, current_major):
    # 从数据库获取当前专业的核心课程列表
    major_courses = get_core_courses_by_major(current_major)

    # 1. 必修课程学分计算（不包括专业核心课）
    required_courses = df[(df['课程性质'] == '必修') & (df['最终折算成绩'] >= 60)]
    non_core_required_courses = required_courses[~required_courses["课程名称"].isin(major_courses)]
    
    # 春季必修学分（不包括专业核心课）
    spring_total_required_courses = non_core_required_courses[non_core_required_courses['学年学期'].fillna('').str.contains('春季', case=False)]
    spring_total_required_credits = spring_total_required_courses['学分'].sum()
    
    # 秋季必修学分（不包括专业核心课）
    autumn_total_required_courses = non_core_required_courses[non_core_required_courses['学年学期'].fillna('').str.contains('秋季', case=False)]
    autumn_total_required_credits = autumn_total_required_courses['学分'].sum()
    
    # 2. 核心课程学分计算（来自 major_courses）
    # 春季核心课程学分
    major_spring_courses = required_courses[
        (required_courses['课程名称'].isin(major_courses)) &
        (required_courses['学年学期'].fillna('').str.contains('春季', case=False))
    ]
    major_spring_credits = major_spring_courses['学分'].sum()
    
    # 秋季核心课程学分
    major_autumn_courses = required_courses[
        (required_courses['课程名称'].isin(major_courses)) &
        (required_courses['学年学期'].fillna('').str.contains('秋季', case=False))
    ]
    major_autumn_credits = major_autumn_courses['学分'].sum()

    # 3. 数字逻辑课程学分
    numerical_logic_courses = df[
        (df['课程名称'].isin(['数字逻辑与数字系统设计'])) & 
        (df['最终折算成绩'] >= 60)
    ]
    total_numerical_logic_credits = numerical_logic_courses['学分'].sum()

    # 4. 专业限选课程学分计算
    limited_courses = df[
        (df['课程性质'] == '限选') & 
        (df['课程类别'] == '其他') & 
        (~df['课程名称'].isin(['企业短期实训', '数字逻辑与数字系统设计', '专业实践'])) & 
        (df['最终折算成绩'] >= 60)
    ]

    # 春季限选课程学分
    spring_limited_courses = limited_courses[limited_courses['学年学期'].fillna('').str.contains('春季', case=False)]
    spring_limited_credits = spring_limited_courses['学分'].sum()
    
    # 秋季限选课程学分
    autumn_limited_courses = limited_courses[limited_courses['学年学期'].fillna('').str.contains('秋季', case=False)]
    autumn_limited_credits = autumn_limited_courses['学分'].sum()

    # 5. 企业短期实训/专业实践学分
    short_term_training_courses = df[
        (df['课程名称'].isin(['企业短期实训', '专业实践'])) & 
        (df['最终折算成绩'] >= 60)
    ]
    total_short_term_training_credits = short_term_training_courses['学分'].sum()

    # 6. 国际化课程学分
    international_courses = df[
        (df['课程名称'].isin(['电子商务技术与研究前沿', '服务计算前沿技术', '高级软件测试', '开源软件开发',
                              '人工智能与媒体大数据', '数字媒体的交互设计与开发', '虚空间中的人工智能和计算机视觉技术',
                              '演化计算', '多媒体信息处理与安全', '人工智能在计算机视觉中的应用', '人工智能与机器学习',
                              '人工智能及其应用', '图模型和概率推理'])) & 
        (df['最终折算成绩'] >= 60)
    ]
    total_international_credits = international_courses['学分'].sum()

    # 7. 专业选修课学分
    elective_courses = df[
        (df['课程性质'] == '选修') & 
        (df['课程类别'] == '其他') & 
        (~df['课程名称'].isin(['生物化学B', '分子生物学', '遗传学B'])) & 
        (df['最终折算成绩'] >= 60)
    ]
    total_elective_credits = elective_courses['学分'].sum()

    # 8. 外专业课程学分
    outmajor_courses_1 = df[
        (df['课程性质'] == '选修') & 
        (df['课程类别'] == '外专业课程') & 
        (df['学分'] >= 2) & 
        (df['最终折算成绩'] >= 60)
    ]
    outmajor_courses_2 = df[
        (df['课程名称'].isin(['生物化学B', '分子生物学', '遗传学B'])) & 
        (df['最终折算成绩'] >= 60)
    ]
    total_outmajor_credits = outmajor_courses_1['学分'].sum() + outmajor_courses_2['学分'].sum()

    # 9. 素质核心和素质选修学分
    culture_core_courses = df[
        (df['课程性质'] == '任选') & 
        ((df['课程类别'] == '素质核心') | (df['课程类别'] == '素质核心（艺术与审美）')) & 
        (df['最终折算成绩'] >= 60)
    ]
    culture_choose_courses = df[
        (df['课程性质'] == '任选') & 
        (df['课程类别'] == '素质选修') & 
        (df['最终折算成绩'] >= 60)
    ]
    mooc_courses = df[
        (df['课程性质'] == '任选') & 
        ((df['课程类别'] == 'MOOC') | (df['课程类别'] == '新生研讨')) & 
        (df['最终折算成绩'] >= 60)
    ]
    total_culture_core_credits = culture_core_courses['学分'].sum()
    total_culture_choose_credits = culture_choose_courses['学分'].sum()
    total_culture_credits = total_culture_core_credits + total_culture_choose_credits + mooc_courses['学分'].sum()

    # 10. 创新创业学分
    innovation_courses = df[
        (df['课程性质'] == '任选') & 
        (df['课程类别'].isin(['创新创业', '创新MOOC', '创新研修'])) & 
        (df['最终折算成绩'] >= 60)
    ]
    total_innovation_credits = innovation_courses['学分'].sum()

    # 汇总结果
    result = {
        '春季必修学分': spring_total_required_credits,
        '秋季必修学分': autumn_total_required_credits,
        '春季核心课程学分': major_spring_credits,
        '秋季核心课程学分': major_autumn_credits,
        '数字逻辑学分': total_numerical_logic_credits,
        '春季限选学分': spring_limited_credits,
        '秋季限选学分': autumn_limited_credits,
        '企业短期实训/专业实践学分': total_short_term_training_credits,
        '国际化课程学分': total_international_credits,
        '专业选修学分': total_elective_credits,
        '外专业学分': total_outmajor_credits,
        '素质核心学分': total_culture_core_credits,
        '素质选修学分': total_culture_choose_credits,
        '文化素质教育学分': total_culture_credits,
        '创新创业学分': total_innovation_credits
    }

    return result
