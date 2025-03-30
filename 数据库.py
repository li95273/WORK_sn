import mysql.connector
from datetime import datetime
from mysql.connector import Error   # 确保正确导入异常类

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
    #按条件筛选日志
    def view_logs_by_filter(self,username=None,start_date=None,end_date=None,limit=100):
        conn=None
        cursor=None
        try:
            conn=self.conn()
            cursor=conn.cursor()
            query="""
                SELECT id,username,error_message,log_time
                FROM error_logs
                WHERE 1=1
            """
            params=[]
            if username:
                query+=" AND username=%s"
                params.append(username)
            if start_date:
                query+=" AND log_time>=%s"
                params.append(start_date)
            if end_date:
                query+=" AND log_time<=%s"
                params.append(end_date)
            query+=" ORDER BY log_time DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query,tuple(params))
            results=cursor.fetchall()

            print("\n错误日志：")
            print("{:<5} {:<15} {:<30} {:<20}".format("ID", "用户名", "错误信息", "时间"))
            for (log_id,user,msg,time) in results:
                print(f"{log_id:<5} {user:<15} {msg[:25]:<30} {time.strftime('%Y-%m-%d %H:%M:%S'):<20}")

        except mysql.connector.Error as e:
            print(f"查询失败：{e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
# 使用示例     
if __name__ == "__main__":
    db = DBManager()
    
    while True:
        print("\n====== 错误日志管理系统 =====")
        print("1. 添加新日志")
        print("2. 查看所有日志")
        print("3. 按条件筛选日志")
        print("0. 退出")
        choice = input("请选择操作(0~3):")
        if choice == "1":
            username = input("请输入用户名：")
            error_msg = input("请输入错误信息：")
            db.log_error(username, error_msg)
        elif choice == "2":
            db.view_logs()
        elif choice == "3":
            print("====== 按条件筛选日志 =====")
            username = input("请输入用户名:") 
            username = username if username else None # 如果输入为空，设置为None

            start_date_str = input("开始日期 (YYYY-MM-DD，留空表示不筛选): ")
            start_date = None
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                except ValueError:
                    print("日期格式错误，将不使用此筛选条件")
            
            end_date_str = input("结束日期 (YYYY-MM-DD，留空表示不筛选): ")
            end_date = None
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    # 设置为当天的最后一秒，以包含整个结束日期
                    end_date = end_date.replace(hour=23, minute=59, second=59)
                except ValueError:
                    print("日期格式错误，将不使用此筛选条件")
            
            limit_str = input("最大显示记录数 (默认100): ")
            limit = 100
            if limit_str and limit_str.isdigit():
                limit = int(limit_str)
            
            db.view_logs_by_filter(username, start_date, end_date, limit)
            
        elif choice == "0":
            print("感谢使用，再见！")
            break
            
        else:
            print("无效选择，请重试")
