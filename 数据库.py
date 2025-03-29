import mysql.connector
from datetime import datetime
from mysql.connector import Error  # 确保正确导入异常类

class DBManager:
    def __init__(self):
        self.connection = self.conn()  # 初始化连接
        self.create_error_table()

    def conn(self):
        try:
            return mysql.connector.connect(
                host='110.41.57.192',
                user='root',
                password='Zzm8023.',
                database='ZGWL_db',
                port=3306
            )
        except mysql.connector.Error as e:
            print(f"连接错误: {e}")
            return None

    def create_error_table(self):
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            # 确保字段名称统一使用log_time
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255),
                    error_message TEXT,
                    log_time DATETIME
                )
            ''')
            conn.commit()
            print("表创建成功")
        except mysql.connector.Error as e:
            print(f"建表失败: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def log_error(self, username, error_msg):
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            # 添加log_time字段值
            query = """INSERT INTO error_logs 
                    (username, error_message, log_time) 
                    VALUES (%s, %s, %s)"""
            values = (username, error_msg, datetime.now())
            cursor.execute(query, values)
            conn.commit()
            print("日志写入成功")
        except mysql.connector.Error as e:
            print(f"写入失败: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def view_logs(self):
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            # 使用正确的字段名称log_time
            cursor.execute("""
                SELECT id, username, error_message, log_time 
                FROM error_logs 
                ORDER BY log_time DESC
            """)
            results = cursor.fetchall()

            print("\n错误日志：")
            print("{:<5} {:<15} {:<30} {:<20}".format(
                "ID", "用户名", "错误信息", "时间"))
            for (log_id, user, msg, time) in results:
                print(f"{log_id:<5} {user:<15} {msg[:25]:<30} {time.strftime('%Y-%m-%d %H:%M:%S'):<20}")

        except mysql.connector.Error as e:
            print(f"查询失败: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

# 使用示例
if __name__ == "__main__":
    db = DBManager()
    # 通过控制台输入（测试用）
    username = input("请输入用户名：")
    error_msg = input("请输入错误信息：")
    db.log_error(username, error_msg)

    db.view_logs()
