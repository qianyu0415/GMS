"""
不同专业对应的表
- 必修课表
- 专业核心课表
- 专业限选课表
"""
from sqlalchemy import text
from db_config import get_engine

# 创建数据库引擎
engine = get_engine()

def get_required_course_table(major):
    """
    根据专业获取对应的必修课表名。
    """
    required_course_map = {
        "计算机科学与技术": "required_course_1",
        "物联网工程": "required_course_1",
        "数据科学与大数据技术": "required_course_1",
        "人工智能": "required_course_1",
        "生物信息学": "required_course_1",
        "软件工程": "required_course_2",
        "信息安全": "required_course_3",
        "网络空间安全": "required_course_3",
    }
    return required_course_map.get(major, None)

def get_core_course_table(major):
    """
    根据专业获取对应的核心课表名。
    """
    core_course_map = {
        "计算机科学与技术": "core_course_1",
        "数据科学与大数据技术": "core_course_2",
        "人工智能": "core_course_3",
        "网络空间安全": "core_course_4",
        "信息安全": "core_course_5",
        "软件工程": "core_course_6",
        "物联网工程": "core_course_7",
        "生物信息学": "core_course_8",
    }
    return core_course_map.get(major, None)

def get_sub_major(student_name):
    """
    根据学生姓名查询其对应的小专业。
    """
    query = text("SELECT major FROM softwareengineeringmajor WHERE name = :name")
    try:
        with engine.connect() as connection:
            result = connection.execute(query, {"name": student_name}).fetchone()
            if result:
                return result[0]  # 通过索引访问第一列
            print(f"未找到学生 {student_name} 的小专业信息。")
    except Exception as e:
        print(f"查询失败: {e}")
    return None


def get_limited_course_table(major, student_name=None):
    """
    根据专业和学生姓名获取对应的限选课程表名。
    """
    limited_course_map = {
        "计算机科学与技术": "limited_course_1",
        "数据科学与大数据技术": "limited_course_2",
        "人工智能": "limited_course_3",
        "网络空间安全": "limited_course_4",
        "信息安全": "limited_course_5",
        "物联网工程": "limited_course_7",
        "生物信息学": "limited_course_8",
    }

    # 如果是软件工程专业，需要根据小专业获取表名
    if major == "软件工程":
        if student_name:
            sub_major = get_sub_major(student_name)
            if sub_major == "软件服务工程":
                return "limited_course_6_3"
            elif sub_major == "工业软件技术":
                return "limited_course_6_1"
            elif sub_major == "基础与智能软件工程":
                return "limited_course_6_2"
        print(f"未找到软件工程学生 {student_name} 的小专业信息。")
        return None

    return limited_course_map.get(major, None)

# 根据专业获取专业选修（表二）九学分
def get_elective_course_table(major):
    """
    根据专业获取对应的必修课表名。
    """
    elective_course_map = {
        "计算机科学与技术": "elective_course_1",
        "数据科学与大数据技术": "elective_course_2",
        "人工智能": "elective_course_3",
        "网络空间安全": "elective_course_4",
        "信息安全": "elective_course_5",
        "软件工程": "elective_course_6",
        "物联网工程": "elective_course_7",
        "生物信息学": "elective_course_8",
    }
    return elective_course_map.get(major, None)


# 测试用例
# if __name__ == "__main__":
#     # 测试获取小专业
#     student_name = "任奕杨"
#     sub_major = get_sub_major(student_name)
#     print(f"{student_name} 的小专业是: {sub_major}")

#     # 测试获取限选课程表
#     major = "软件工程"
#     limited_course_table = get_limited_course_table(major, student_name)
#     print(f"{major} 专业的限选课程表是: {limited_course_table}")

#     major = "计算机科学与技术"
#     limited_course_table = get_limited_course_table(major)
#     print(f"{major} 专业的限选课程表是: {limited_course_table}")
