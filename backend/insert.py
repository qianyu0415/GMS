import pandas as pd
from sqlalchemy import text
from db_config import get_engine

def read_excel_file(file_path):
    """
    自动读取 .xls 或 .xlsx 文件。
    """
    if file_path.endswith('.xls'):
        return pd.read_excel(file_path, engine='xlrd')  # 使用 xlrd 处理 .xls 文件
    elif file_path.endswith('.xlsx'):
        return pd.read_excel(file_path, engine='openpyxl')  # 使用 openpyxl 处理 .xlsx 文件
    else:
        raise ValueError("不支持的文件格式，请提供 .xls 或 .xlsx 文件")

def insert_excel_data_to_db(excel_file_path, table_name):
    """
    将 Excel 文件中的数据插入到数据库表中。
    :param excel_file_path: Excel 文件的路径
    :param table_name: 数据库中目标表的表名
    """
    # 读取 Excel 文件
    try:
        df = read_excel_file(excel_file_path)
    except Exception as e:
        print(f"读取 Excel 文件失败: {e}")
        return

    # 检查是否包含必要的列
    if '课程名称' not in df.columns or '学分' not in df.columns:
        print("Excel 文件中缺少必要的列：'课程名称' 或 '学分'")
        return

    # 处理空值：将空值替换为空字符串或 0
    df['课程名称'] = df['课程名称'].fillna('')
    df['学分'] = df['学分'].fillna(0)

    # 打开数据库连接
    engine = get_engine()
    with engine.connect() as connection:
        transaction = connection.begin()  # 开启事务
        try:
            for index, row in df.iterrows():
                # 构造插入 SQL
                insert_query = text(f"""
                    INSERT INTO {table_name} (course_name, credits)
                    VALUES (:course_name, :credits)
                """)

                # 执行插入操作
                connection.execute(insert_query, {
                    'course_name': row['课程名称'],
                    'credits': row['学分']
                })
                print(f"插入成功: 课程名称={row['课程名称']}, 学分={row['学分']}")

            transaction.commit()  # 提交事务
            print("数据插入完成并提交！")
        except Exception as e:
            transaction.rollback()  # 回滚事务
            print(f"事务失败，已回滚: {e}")
    print("数据插入完成！")

# 示例调用
if __name__ == "__main__":
    # Excel 文件路径
    excel_file_path = "21软工专业选修.xlsx"


    # 目标数据库表名
    table_name = 'elective_course_6'  # 替换为你的数据库表名

    # 调用函数插入数据
    insert_excel_data_to_db(excel_file_path, table_name)
