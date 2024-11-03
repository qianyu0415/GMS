# import pandas as pd
# from sqlalchemy import create_engine

# # 数据准备，确保每个字段的长度一致
# # 数据准备
# data = {
#     'course_name': [
#         '思想政治理论实践课', '军事理论', '军事技能', '大学计算机-计算思维导论D', '高级语言程序设计',
#         'PjBL与科技创新', '大学外语', '微积分B(1)', '代数与几何B', '习近平新时代中国特色社会主义思想概论',
#         '思想道德与法治', '体育', '集合论与图论', '专业解读', '大学外语', '微积分B(2)',
#         '中国近现代史纲要', '形势与政策（1）', '体育', '大学物理B(1)', '数据结构与算法',
#         '信息安全概论', '信息安全数学基础', '大学外语', '概率论与数理统计B', '毛泽东思想和中国特色社会主义理论体系概论',
#         '体育', '大学物理实验B', '计算机系统', '计算机组成原理', '计算机网络',
#         '大学外语', '形势与政策（2）', '马克思主义基本原理', '体育', '算法设计与分析',
#         '操作系统', '人工智能导论', '形式语言与自动机', '软件工程', '编译原理',
#         '形势与政策（3）', '毕业设计（论文）'
#     ],
#     'academic_year': [
#         '第1学年秋季', '第1学年秋季', '第1学年秋季', '第1学年秋季', '第1学年秋季',
#         '第1学年秋季', '第1学年秋季', '第1学年秋季', '第1学年秋季', '第1学年秋季',
#         '第1学年秋季', '第1学年秋季', '第1学年春季', '第1学年春季', '第1学年春季', '第1学年春季',
#         '第1学年春季', '第1学年春季', '第1学年春季', '第1学年春季', '第2学年秋季',
#         '第2学年秋季', '第2学年秋季', '第2学年秋季', '第2学年秋季', '第2学年秋季',
#         '第2学年秋季', '第2学年秋季', '第2学年春季', '第2学年春季', '第2学年春季',
#         '第2学年春季', '第2学年春季', '第2学年春季', '第2学年春季', '第3学年秋季',
#         '第3学年秋季', '第3学年秋季', '第3学年秋季', '第3学年春季', '第3学年春季',
#         '第3学年春季', '第4学年春季'
#     ],
#     'department': [
#         '学工处', '学工处', '学工处', '计算学部', '计算学部',
#         '电子与信息工程学院', '人文社科学部', '数学学院', '数学学院', '马克思主义学院',
#         '马克思主义学院', '体育部', '计算学部', '计算学部', '人文社科学部', '数学学院',
#         '马克思主义学院', '马克思主义学院', '体育部', '物理学院', '计算学部',
#         '计算学部', '计算学部', '人文社科学部', '数学学院', '马克思主义学院',
#         '体育部', '物理学院', '计算学部', '计算学部', '计算学部',
#         '人文社科学部', '马克思主义学院', '马克思主义学院', '体育部', '计算学部',
#         '计算学部', '计算学部', '计算学部', '计算学部', '计算学部',
#         '马克思主义学院', '计算学部'
#     ],
#     'credits': [
#         2.0, 2.0, 2.0, 2.0, 3.0,
#         1.0, 1.5, 5.5, 4.0, 2.0,
#         2.5, 1.0, 3.0, 1.0, 1.5, 5.5,
#         2.5, 0.5, 1.0, 5.5, 3.0,
#         2.0, 3.0, 1.5, 3.5, 4.0,
#         0.5, 1.0, 3.0, 3.0, 3.0,
#         1.5, 1.0, 3.0, 0.5, 2.0,
#         3.0, 2.0, 2.0, 3.0, 3.0,
#         0.5, 10.0
#     ],
#     'id': [3] * 43  # 将所有id设置为2
# }

# # 打印每个字段的长度
# for key, value in data.items():
#     print(f"{key} 列表长度: {len(value)}")

# # 创建 DataFrame
# df = pd.DataFrame(data)

# # 连接到 MySQL 数据库（请替换用户名、密码和数据库名称）
# # 示例连接字符串: mysql+pymysql://username:password@localhost/db_name
# engine = create_engine('mysql+pymysql://root:123456@localhost/credits_db')

# # 将数据插入到 MySQL 表 'required_course'，其中包含 'id' 列，所有值为 2
# df.to_sql('required_course', con=engine, index=False, if_exists='append')

# print("数据已成功插入到 'required_course' 表中。")


# 直接从excel表格中读取数据
import pandas as pd
import os
import pymysql

# 数据库连接配置
db_config = {
    'host': 'localhost',  # 数据库主机，通常为 'localhost'
    'port': 3306,         # 数据库端口号
    'user': 'root',       # 数据库用户名
    'password': '123456', # 数据库密码
    'database': 'credits_db'  # 数据库名称
}


# 课程名称与 ID 的映射
# course_id_mapping = {
#     "计科": "计算机科学与技术",
#     "大数据": "数据科学与大数据技术",
#     "人工智能": "人工智能",
#     "网安": "网络空间安全",
#     "信安": "信息安全",
#     "软工": "软件工程",
#     "物联网": "物联网工程",
#     "生信": "生物信息学"
# }
import pandas as pd
import os
import pymysql

# 数据库连接配置
db_config = {
    'host': 'localhost',  # 数据库主机，通常为 'localhost'
    'port': 3306,         # 数据库端口号
    'user': 'root',       # 数据库用户名
    'password': '123456', # 数据库密码
    'database': 'credits_db'  # 数据库名称
}

# 课程名称与 ID 的映射
course_id_mapping = {
    "计科": 1,
    "大数据": 2,
    "人工智能": 3,
    "网安": 4,
    "信安": 5,
    "软工-工业软件基础": "6_1",
    "软工-基础与智能软件工程": "6_2",
    "软工-软件服务工程": "6_3",
    "物联网工程": 7,
    "生信": 8
}

# 指定包含 Excel 文件的目录
directory_path = 'E:\\chengji\\毕业审核系统相关数据\\各专业限选课'

# 连接到数据库
connection = pymysql.connect(**db_config)
cursor = connection.cursor()

# 创建表的函数
def create_table_if_not_exists(major_value):
    table_name = f"limited_course_{major_value}"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        course_name VARCHAR(255) NOT NULL,
        credits FLOAT NOT NULL,
        UNIQUE KEY (course_name)
    );
    """
    cursor.execute(create_table_query)

# 遍历目录中的所有 Excel 文件
for filename in os.listdir(directory_path):
    if filename.endswith('.xlsx'):
        file_path = os.path.join(directory_path, filename)
        
        # 使用 openpyxl 引擎读取 .xlsx 文件
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # 提取课程名称和学分列（假设课程名称在第1列（索引为1），学分在第3列（索引为3））
        extracted_df = df.iloc[:, [1, 3]]
        
        # 获取课程名称（文件名去掉后缀作为课程名称）
        course_name = filename.split('.')[0]
        
        if course_name in course_id_mapping:
            major_value = course_id_mapping[course_name]  # 获取对应的 ID
            
            # 创建对应专业的表（如果不存在）
            create_table_if_not_exists(major_value)

            # 遍历提取的数据并插入到数据库
            for index, row in extracted_df.iterrows():
                course_name_from_excel = row.iloc[0] if pd.notnull(row.iloc[0]) else None
                credits = row.iloc[1] if pd.notnull(row.iloc[1]) else None
                
                # 确保 credits 为浮点数
                try:
                    credits = float(credits) if credits is not None else None
                except ValueError:
                    print(f"跳过无效学分值：{credits}，位于文件：{filename} 的第 {index + 1} 行")
                    continue
                
                # 检查数据有效性
                if course_name_from_excel and credits is not None:
                    # 插入数据到数据库
                    insert_query = f"""
                    INSERT INTO limited_course_{major_value} (course_name, credits)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE credits = VALUES(credits);
                    """
                    cursor.execute(insert_query, (course_name_from_excel, credits))

# 提交更改并关闭连接
connection.commit()
cursor.close()
connection.close()

print("数据已成功插入到数据库中。")





# import pandas as pd
# import pymysql

# # 数据库连接配置
# db_config = {
#     'host': 'localhost',      # 数据库主机
#     'port': 3306,             # 数据库端口号
#     'user': 'root',           # 数据库用户名
#     'password': '123456',     # 数据库密码
#     'database': 'credits_db'  # 数据库名称
# }

# # 指定包含 Excel 文件的路径
# file_path = './国际化课程.xlsx'

# # 连接到数据库
# connection = pymysql.connect(**db_config)
# cursor = connection.cursor()

# # 使用 openpyxl 引擎读取 .xlsx 文件
# df = pd.read_excel(file_path, engine='openpyxl')

# # 提取第二列和第四列（假设索引为1和3）
# extracted_df = df.iloc[:, [1, 3]]

# # 遍历提取的数据并插入到数据库
# for index, row in extracted_df.iterrows():
#     course_name_from_excel = row[0]
#     credits = row[1]

#     # 插入数据到数据库
#     insert_query = """
#     INSERT INTO international (course_name, credits)
#     VALUES (%s, %s)
#     ON DUPLICATE KEY UPDATE credits = VALUES(credits);
#     """
#     cursor.execute(insert_query, (course_name_from_excel, credits))

# # 提交更改并关闭连接
# connection.commit()
# cursor.close()
# connection.close()

# print("数据已成功插入到数据库中。")

# import pandas as pd
# from sqlalchemy import create_engine, text
# import pymysql

# # 数据库连接配置
# db_config = 'mysql+pymysql://root:123456@localhost:3306/credits_db'

# # Excel 文件路径
# excel_file_path = 'E:\\Github\\GMS\\backend\\信安、网安必修课.xlsx'  # 替换为您的 Excel 文件路径

# # 读取 Excel 文件
# df = pd.read_excel(excel_file_path)

# # 选择所需的列，并重命名为数据库中的字段名
# df = df[['课程名称', '开课学年学期', '开课院系', '学分']]  # 按您的 Excel 列名
# df.columns = ['course_name', 'academic_year', 'department', 'credits']


# # 创建数据库连接
# engine = create_engine(db_config)

# # 创建 required_course 表的 SQL 语句
# create_table_query = """
# CREATE TABLE IF NOT EXISTS required_course_3 (
#     course_name VARCHAR(100) NOT NULL,
#     academic_year VARCHAR(50),
#     department VARCHAR(100),
#     credits DECIMAL(3, 1),
#     PRIMARY KEY (course_name, academic_year)  -- 假设课程名称和学年学期的组合是唯一的
# );
# """

# # 执行创建表的 SQL 语句
# with engine.connect() as connection:
#     connection.execute(text(create_table_query))
#     print("表 required_course 创建成功")

# # 将数据写入数据库
# with engine.connect() as connection:
#     try:
#         df.to_sql('required_course_3', con=engine, if_exists='append', index=False)
#         print("数据已成功插入到 required_course 表中")
#     except Exception as e:
#         print(f"数据插入出错: {e}")


