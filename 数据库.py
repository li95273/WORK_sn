# -*- coding: utf-8 -*-
'''
数据库模块 - 负责所有数据库操作

本模块封装了所有与MySQL数据库的交互操作，包括：
- 数据库连接管理
- 错误日志记录
- 用户认证和管理
- 数据查询和筛选
'''

# -*- coding: utf-8 -*-
'''
数据库模块 - 负责所有数据库操作

本模块封装了所有与MySQL数据库的交互操作，包括：
- 数据库连接管理
- 错误日志记录
- 用户认证和管理
- 数据查询和筛选
'''

import mysql.connector
from datetime import datetime
from mysql.connector import Error   # 确保正确导入异常类

class DBManager:
    '''
    数据库管理类 - 处理所有数据库操作
    
    属性:
        connection: MySQL数据库连接对象
    '''
    
    def __init__(self):
        '''
        初始化数据库管理器并创建错误日志表
        '''
        self.connection = self.conn()  # 初始化连接
        self.create_error_table()
        self.create_users_table()

    def conn(self):
        '''
        创建并返回数据库连接
        
        返回:
            connection: MySQL数据库连接对象，连接失败则返回None
        '''
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
        '''
        创建错误日志表，如果表不存在
        表结构包含ID、用户名、SN、错误信息和记录时间
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            # 创建错误日志表，添加sn字段用于直接查询
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255),
                    sn VARCHAR(100),
                    error_message TEXT,
                    log_time DATETIME,
                    INDEX idx_sn (sn)
                )
            ''')
            conn.commit()
        except mysql.connector.Error as e:
            print(f"建表失败: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
            
    def create_users_table(self):
        '''
        创建用户表，如果表不存在
        表结构包含用户名、密码和注册时间
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS USERS (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user VARCHAR(255) UNIQUE,
                    password VARCHAR(255),
                    time DATETIME
                )
            ''')
            conn.commit()
        except mysql.connector.Error as e:
            print(f"建表失败: {e}")
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def log_error(self, username, sn, error_msg):
        '''
        记录错误信息到数据库
        
        参数:
            username: 用户名
            sn: 设备序列号
            error_msg: 错误信息
            
        返回:
            bool: 写入成功返回True，失败返回False
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            # 添加错误日志记录
            query = """INSERT INTO error_logs 
                    (username, sn, error_message, log_time) 
                    VALUES (%s, %s, %s, %s)"""
            values = (username, sn, error_msg, datetime.now())
            cursor.execute(query, values)
            conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"写入失败: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
            
    def verify_user(self, username, password):
        '''
        验证用户登录信息
        
        参数:
            username: 用户名
            password: 密码
            
        返回:
            bool: 验证成功返回True，失败返回False
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            cursor.execute('SELECT user, password FROM USERS WHERE user = %s', (username,))
            result = cursor.fetchone()
            
            if result and result[1] == password:
                return True
            return False
        except mysql.connector.Error as e:
            print(f"验证用户失败: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def add_user(self, username, password):
        '''
        添加新用户
        
        参数:
            username: 用户名
            password: 密码
            
        返回:
            bool: 添加成功返回True，失败返回False
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            
            # 检查用户是否已存在
            cursor.execute('SELECT user FROM USERS WHERE user = %s', (username,))
            if cursor.fetchone():
                return False  # 用户已存在
                
            # 添加新用户
            sql = 'INSERT INTO USERS(user, password, time) VALUES(%s, %s, %s)'
            values = (username, password, datetime.now())
            cursor.execute(sql, values)
            conn.commit()
            return True
        except mysql.connector.Error as e:
            print(f"添加用户失败: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def view_logs(self, limit=100):
        '''
        查看最近的错误日志
        
        参数:
            limit: 返回的最大记录数
            
        返回:
            list: 错误日志记录列表
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, sn, error_message, log_time 
                FROM error_logs 
                ORDER BY log_time DESC
                LIMIT %s
            """, (limit,))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"查询失败: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
    def view_logs_by_filter(self, username=None, start_date=None, end_date=None, limit=100):
        '''
        按条件筛选错误日志
        
        参数:
            username: 用户名筛选
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回的最大记录数
            
        返回:
            list: 筛选后的错误日志记录列表
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            query = """
                SELECT id, username, sn, error_message, log_time
                FROM error_logs
                WHERE 1=1
            """
            params = []
            
            # 添加筛选条件
            if username:
                query += " AND username LIKE %s"
                params.append(f"%{username}%")  # 使用模糊匹配
            if start_date:
                query += " AND log_time >= %s"
                params.append(start_date)
            if end_date:
                query += " AND log_time <= %s"
                params.append(end_date)
                
            query += " ORDER BY log_time DESC LIMIT %s"
            params.append(limit)

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"查询失败: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
    def get_error_by_sn(self, sn):
        '''
        通过SN直接查询错误信息
        
        参数:
            sn: 设备序列号
            
        返回:
            list: 包含该SN的错误记录列表
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            query = """
                SELECT id, username, sn, error_message, log_time
                FROM error_logs
                WHERE sn = %s
                ORDER BY log_time DESC
            """
            cursor.execute(query, (sn,))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"查询失败: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def filter_logs_advanced(self, username=None, sn=None, error_keyword=None, 
                           start_date=None, end_date=None, sort_option='time_desc', limit=100):
        '''
        高级筛选错误日志
        
        参数:
            username: 用户名筛选
            sn: 设备序列号
            error_keyword: 错误信息关键词
            start_date: 开始日期
            end_date: 结束日期
            sort_option: 排序选项 (time_desc, time_asc, id_desc, id_asc)
            limit: 返回的最大记录数
            
        返回:
            list: 筛选后的错误日志记录列表
        '''
        conn = None
        cursor = None
        try:
            conn = self.conn()
            cursor = conn.cursor()
            query = """
                SELECT id, username, sn, error_message, log_time
                FROM error_logs
                WHERE 1=1
            """
            params = []
            
            # 添加筛选条件
            if username:
                query += " AND username LIKE %s"
                params.append(f"%{username}%")  # 使用模糊匹配
            if start_date:
                query += " AND log_time >= %s"
                params.append(start_date)
            if end_date:
                query += " AND log_time <= %s"
                params.append(end_date)
            if sn:
                query += " AND sn LIKE %s"
                params.append(f"%{sn}%")  # 查找SN字段
            if error_keyword:
                query += " AND error_message LIKE %s"
                params.append(f"%{error_keyword}%")  # 查找错误关键词
            
            # 根据排序选项设置排序方式
            if sort_option == 'time_desc':
                query += " ORDER BY log_time DESC"
            elif sort_option == 'time_asc':
                query += " ORDER BY log_time ASC"
            elif sort_option == 'id_desc':
                query += " ORDER BY id DESC"
            elif sort_option == 'id_asc':
                query += " ORDER BY id ASC"
            else:
                query += " ORDER BY log_time DESC"
                
            query += " LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"查询失败: {e}")
            return []
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
