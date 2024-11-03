import pandas as pd
import pymysql

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'credits_db'
}

# 读取 Excel 数据
file_path = './总体数据.xlsx'
df = pd.read_excel(file_path)

# 连接到数据库
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# 遍历每个学生，创建动态表并插入数据
for (student_id, student_name,major), student_data in df.groupby(['学号', '姓名','专业']):
    # 规范化表名，避免以数字开头
    table_name = f"{student_name}_{student_id}_{major}"  # 表名格式为 姓名_学号

    # 创建学生表的 SQL 查询
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_name}` (
        course_name VARCHAR(100) NOT NULL,
        academic_year VARCHAR(20),
        course_nature VARCHAR(20),
        course_category VARCHAR(20),
        final_grade VARCHAR(20),  -- 最终成绩以字符串形式存储
        retake_remark VARCHAR(20), -- 补考重修标记
        credits DECIMAL(3, 1),
        major VARCHAR(20)  -- 专业字段
    );
    """
    
    try:
        cursor.execute(create_table_query)
    except pymysql.MySQLError as e:
        print(f"创建表 {table_name} 时出错: {e}")
        continue  # 如果创建表失败，跳过此学生

    # 插入学生的选课信息
    for index, row in student_data.iterrows():
        insert_query = f"""
        INSERT INTO `{table_name}` (course_name, academic_year, course_nature, course_category, final_grade, retake_remark, credits, major)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        try:
            cursor.execute(insert_query, (
                row['课程名称'],
                row['学年学期'],
                row['课程性质'],
                row['课程类别'],
                row['最终成绩'],  # 作为字符串插入
                row.get('补考重修标记', ''),  # 使用字典的 get 方法，避免 KeyError
                row['学分'],
                row['专业']  # 插入专业字段
            ))
        except pymysql.MySQLError as e:
            print(f"插入数据到 {table_name} 时出错: {e}")
            continue  # 如果插入数据失败，跳过此行

# 提交更改并关闭连接
try:
    connection.commit()
    print("学生选课信息已成功存储在数据库中。")
except pymysql.MySQLError as e:
    print(f"提交更改时出错: {e}")
finally:
    cursor.close()
    connection.close()
