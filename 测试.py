#utf-8
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk, simpledialog
from tkcalendar import DateEntry  # 需要安装: pip install tkcalendar
import csv
from tkinter import filedialog

# 导入数据库模块
from 数据库 import DBManager

class ErrorLogApp:
    def __init__(self, root):
        self.root = root
        self.root.title('测试报错记录系统')
        self.root.geometry('1000x700')
        self.db = DBManager()
        
        # 创建标签页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建录入页面
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text='错误录入')
        
        # 创建查询页面
        self.query_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.query_frame, text='错误查询')
        
        # 创建报告生成页面
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text='报告生成')
        
        # 初始化录入页面
        self.setup_input_frame()
        
        # 初始化查询页面
        self.setup_query_frame()
        
        # 初始化报告生成页面
        self.setup_report_frame()
    
    def setup_input_frame(self):
        '''
        设置错误录入页面的UI组件
        
        创建姓名、SN和错误信息的输入控件，以及提交和清空按钮
        '''
        # 创建标签
        tk.Label(self.input_frame, text='姓名：', font=('Arial', 12)).place(x=30, y=50)
        tk.Label(self.input_frame, text='SN：', font=('Arial', 12)).place(x=350, y=50)
        tk.Label(self.input_frame, text='报错信息：', font=('Arial', 12)).place(x=30, y=100)
        
        # 创建输入控件
        self.name = tk.Entry(self.input_frame, width=25, font=('Arial', 11))
        self.name.place(x=80, y=50)
        self.sn = tk.Entry(self.input_frame, width=30, font=('Arial', 11))
        self.sn.place(x=385, y=50)
        self.baocuo = tk.Text(self.input_frame, width=100, height=20)
        self.baocuo.place(x=95, y=100)
        
        # 创建操作按钮
        tk.Button(self.input_frame, text='确认维护', command=self.queren, width=15).place(x=150, y=500)
        tk.Button(self.input_frame, text='清空输入', command=self.clear_input, width=15).place(x=350, y=500)
        tk.Button(self.input_frame, text='批量导入', command=self.batch_import, width=15).place(x=550, y=500)
    
    def setup_query_frame(self):
        '''
        设置错误查询页面的UI组件
        
        创建SN查询区域、结果显示表格和高级筛选功能
        '''
        # 创建SN查询区域 - 突出显示，方便维修工程师使用
        sn_frame = ttk.LabelFrame(self.query_frame, text='SN查询')
        sn_frame.pack(fill='x', padx=10, pady=10)
        
        # SN查询输入框和按钮
        tk.Label(sn_frame, text='输入SN:', font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=10, pady=15, sticky='w')
        self.sn_query = tk.Entry(sn_frame, width=30, font=('Arial', 11))
        self.sn_query.grid(row=0, column=1, padx=10, pady=15, sticky='w')
        tk.Button(sn_frame, text='查询', command=self.query_by_sn, width=15, font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=10, pady=15)
        tk.Button(sn_frame, text='清空', command=self.clear_sn_query, width=10).grid(row=0, column=3, padx=10, pady=15)
        
        # 创建结果显示区域
        result_frame = ttk.LabelFrame(self.query_frame, text='查询结果')
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建表格
        columns = ('id', 'username', 'sn', 'error_message', 'log_time')
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show='headings')
        
        # 定义表头
        self.result_tree.heading('id', text='ID')
        self.result_tree.heading('username', text='姓名')
        self.result_tree.heading('sn', text='SN')
        self.result_tree.heading('error_message', text='报错信息')
        self.result_tree.heading('log_time', text='时间')
        
        # 定义列宽
        self.result_tree.column('id', width=50)
        self.result_tree.column('username', width=120)
        self.result_tree.column('sn', width=150)
        self.result_tree.column('error_message', width=450)
        self.result_tree.column('log_time', width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.result_tree.yview)
        self.result_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.result_tree.pack(fill='both', expand=True)
        
        # 双击查看详情
        self.result_tree.bind('<Double-1>', self.show_error_details)
        
        # 添加导出按钮
        tk.Button(result_frame, text='导出结果', command=self.export_results, width=15).pack(side='right', padx=10, pady=5)
        
        # 创建高级筛选区域（放在最下面）
        advanced_frame = ttk.LabelFrame(self.query_frame, text='高级筛选')
        advanced_frame.pack(fill='x', padx=10, pady=5)
        
        # 高级筛选按钮
        tk.Button(advanced_frame, text='打开高级筛选', command=self.advanced_filter, width=15).pack(pady=10)
    
    def queren(self):
        '''
        确认按钮的回调函数 - 提交错误信息到数据库
        
        获取用户输入的姓名、SN和错误信息，验证非空后写入数据库
        成功后显示提示并清空输入框
        '''
        # 获取并清理输入内容
        name_get = self.name.get().strip()
        sn_get = self.sn.get().strip()
        baocuo_get = self.baocuo.get('1.0', 'end-1c').strip()  # 获取文本内容，排除最后的换行符
        
        # 验证所有字段都不为空
        if not (name_get and sn_get and baocuo_get):
            messagebox.showerror('错误', '请检查各项信息不能为空！')
            return
        
        try:
            # 写入数据库
            conn = self.db.conn()
            if not conn:
                messagebox.showerror('错误', '无法连接到数据库，请检查网络连接！')
                return
                
            # 调用数据库模块记录错误信息
            if self.db.log_error(name_get, sn_get, baocuo_get):
                messagebox.showinfo('成功', f'SN: {sn_get} 的错误信息已成功记录！')
                self.clear_input()  # 清空输入
            else:
                messagebox.showerror('错误', '记录错误信息失败，请重试！')
        except Exception as e:
            messagebox.showerror('错误', f'记录错误信息失败: {str(e)}')
    
    def clear_input(self):
        '''
        清空输入框的回调函数
        
        清空姓名、SN和错误信息的输入控件
        '''
        self.name.delete(0, tk.END)  # 清空姓名输入框
        self.sn.delete(0, tk.END)    # 清空SN输入框
        self.baocuo.delete('1.0', tk.END)  # 清空错误信息文本框
    
    def filter_logs(self):
        """
        基本筛选功能的实现
        
        根据用户名、日期范围等条件筛选错误日志记录，
        并在结果表格中显示筛选结果
        """
        # 获取筛选条件
        username = self.username_filter.get()
        username = username if username else None
        
        # 获取日期
        try:
            start_date = self.start_date.get_date()
            # 设置为当天的开始时间
            start_date = datetime.combine(start_date, datetime.min.time())
        except:
            start_date = None
        
        try:
            end_date = self.end_date.get_date()
            # 设置为当天的结束时间
            end_date = datetime.combine(end_date, datetime.max.time())
        except:
            end_date = None
        
        # 获取限制数量
        try:
            limit = int(self.limit_var.get())
        except:
            limit = 100
        
        # 清空当前结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 查询数据库
        conn = None
        cursor = None
        try:
            conn = self.db.conn()
            cursor = conn.cursor()
            query = """
                SELECT id, username, sn, error_message, log_time
                FROM error_logs
                WHERE 1=1
            """
            params = []
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
            results = cursor.fetchall()
            
            # 显示结果
            for record in results:
                self.result_tree.insert('', 'end', values=record)
            
            # 显示结果数量
            messagebox.showinfo('查询结果', f'共找到 {len(results)} 条记录')
            
        except Exception as e:
            messagebox.showerror('查询失败', f'查询失败: {str(e)}')
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
    
    def clear_filter(self):
        self.username_filter.delete(0, tk.END)
        self.limit_var.set('100')
        # 重置日期选择器为当前日期
        today = datetime.now().date()
        self.start_date.set_date(today)
        self.end_date.set_date(today)
        
    def advanced_filter(self):
        # 创建高级筛选对话框
        filter_dialog = tk.Toplevel(self.root)
        filter_dialog.title('高级筛选')
        filter_dialog.geometry('500x400')
        filter_dialog.transient(self.root)  # 设置为主窗口的子窗口
        filter_dialog.grab_set()  # 模态对话框
        
        # 创建筛选选项
        ttk.Label(filter_dialog, text='筛选条件', font=('Arial', 12, 'bold')).pack(pady=10)
        
        # 创建选项框架
        options_frame = ttk.Frame(filter_dialog)
        options_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 部门筛选
        ttk.Label(options_frame, text='部门:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        department_var = tk.StringVar()
        department_entry = ttk.Entry(options_frame, textvariable=department_var, width=20)
        department_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # 工号筛选
        ttk.Label(options_frame, text='工号:').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        employee_id_var = tk.StringVar()
        employee_id_entry = ttk.Entry(options_frame, textvariable=employee_id_var, width=20)
        employee_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # 姓名筛选
        ttk.Label(options_frame, text='姓名:').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        name_var = tk.StringVar()
        name_entry = ttk.Entry(options_frame, textvariable=name_var, width=20)
        name_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        # SN筛选
        ttk.Label(options_frame, text='SN:').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        sn_var = tk.StringVar()
        sn_entry = ttk.Entry(options_frame, textvariable=sn_var, width=20)
        sn_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        
        # 错误信息关键词
        ttk.Label(options_frame, text='错误关键词:').grid(row=4, column=0, padx=5, pady=5, sticky='w')
        error_keyword_var = tk.StringVar()
        error_keyword_entry = ttk.Entry(options_frame, textvariable=error_keyword_var, width=20)
        error_keyword_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        
        # 日期范围
        date_frame = ttk.LabelFrame(options_frame, text='日期范围')
        date_frame.grid(row=0, column=2, rowspan=3, padx=15, pady=5, sticky='nsew')
        
        ttk.Label(date_frame, text='开始日期:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        start_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        start_date.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(date_frame, text='结束日期:').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        end_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        end_date.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # 排序选项
        sort_frame = ttk.LabelFrame(options_frame, text='排序方式')
        sort_frame.grid(row=3, column=2, rowspan=2, padx=15, pady=5, sticky='nsew')
        
        sort_var = tk.StringVar(value='time_desc')
        ttk.Radiobutton(sort_frame, text='时间降序（最新优先）', variable=sort_var, value='time_desc').grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Radiobutton(sort_frame, text='时间升序（最早优先）', variable=sort_var, value='time_asc').grid(row=1, column=0, padx=5, pady=2, sticky='w')
        ttk.Radiobutton(sort_frame, text='ID降序', variable=sort_var, value='id_desc').grid(row=2, column=0, padx=5, pady=2, sticky='w')
        ttk.Radiobutton(sort_frame, text='ID升序', variable=sort_var, value='id_asc').grid(row=3, column=0, padx=5, pady=2, sticky='w')
        
        # 限制记录数
        limit_frame = ttk.Frame(filter_dialog)
        limit_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(limit_frame, text='最大显示记录数:').pack(side=tk.LEFT, padx=5)
        limit_var = tk.StringVar(value='100')
        limit_entry = ttk.Entry(limit_frame, textvariable=limit_var, width=10)
        limit_entry.pack(side=tk.LEFT, padx=5)
        
        # 保存筛选设置选项
        save_var = tk.BooleanVar(value=False)
        save_check = ttk.Checkbutton(filter_dialog, text='保存此筛选设置', variable=save_var)
        save_check.pack(pady=5)
        
        # 按钮区域
        button_frame = ttk.Frame(filter_dialog)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        def apply_filter():
            # 构建用户名筛选条件（格式：部门-工号-姓名）
            department = department_var.get().strip()
            employee_id = employee_id_var.get().strip()
            name = name_var.get().strip()
            
            username_parts = []
            if department:
                username_parts.append(department)
            if employee_id:
                username_parts.append(employee_id)
            if name:
                username_parts.append(name)
                
            # 如果有任何部分，则构建用户名筛选条件
            if username_parts:
                username_filter = '-'.join(username_parts)
                self.username_filter.delete(0, tk.END)
                self.username_filter.insert(0, username_filter)
            
            # 设置日期
            try:
                self.start_date.set_date(start_date.get_date())
                self.end_date.set_date(end_date.get_date())
            except:
                pass
                
            # 设置记录限制
            if limit_var.get().strip() and limit_var.get().strip().isdigit():
                self.limit_var.set(limit_var.get().strip())
            
            # 应用高级筛选
            self.filter_logs_advanced(
                sn=sn_var.get().strip() if sn_var.get().strip() else None,
                error_keyword=error_keyword_var.get().strip() if error_keyword_var.get().strip() else None,
                sort_option=sort_var.get()
            )
            
            # 如果选择了保存设置
            if save_var.get():
                self.save_filter_settings({
                    'department': department,
                    'employee_id': employee_id,
                    'name': name,
                    'sn': sn_var.get().strip(),
                    'error_keyword': error_keyword_var.get().strip(),
                    'sort_option': sort_var.get(),
                    'limit': limit_var.get().strip()
                })
            
            filter_dialog.destroy()
        
        def load_settings():
            # 加载保存的筛选设置
            settings = self.load_filter_settings()
            if settings:
                if 'department' in settings:
                    department_var.set(settings['department'])
                if 'employee_id' in settings:
                    employee_id_var.set(settings['employee_id'])
                if 'name' in settings:
                    name_var.set(settings['name'])
                if 'sn' in settings:
                    sn_var.set(settings['sn'])
                if 'error_keyword' in settings:
                    error_keyword_var.set(settings['error_keyword'])
                if 'sort_option' in settings:
                    sort_var.set(settings['sort_option'])
                if 'limit' in settings:
                    limit_var.set(settings['limit'])
                messagebox.showinfo('加载设置', '已加载保存的筛选设置')
            else:
                messagebox.showinfo('加载设置', '没有找到保存的筛选设置')
        
        ttk.Button(button_frame, text='应用筛选', command=apply_filter, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='加载保存的设置', command=load_settings, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='取消', command=filter_dialog.destroy, width=15).pack(side=tk.RIGHT, padx=5)
    
    def filter_logs_advanced(self, sn=None, error_keyword=None, sort_option='time_desc'):
        """
        高级筛选功能的实现
        
        根据用户名、SN、错误关键词、日期范围和排序方式等条件筛选错误日志记录，
        并在结果表格中显示筛选结果
        """
        # 获取基本筛选条件
        username = self.username_filter.get()
        username = username if username else None
        
        # 获取日期
        try:
            start_date = self.start_date.get_date()
            # 设置为当天的开始时间
            start_date = datetime.combine(start_date, datetime.min.time())
        except:
            start_date = None
        
        try:
            end_date = self.end_date.get_date()
            # 设置为当天的结束时间
            end_date = datetime.combine(end_date, datetime.max.time())
        except:
            end_date = None
        
        # 获取限制数量
        try:
            limit = int(self.limit_var.get())
        except:
            limit = 100
        
        # 清空当前结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 查询数据库
        conn = None
        cursor = None
        try:
            conn = self.db.conn()
            cursor = conn.cursor()
            query = """
                SELECT id, username, sn, error_message, log_time
                FROM error_logs
                WHERE 1=1
            """
            params = []
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
                params.append(f"%{sn}%")  # 使用模糊匹配SN字段
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
            results = cursor.fetchall()
            
            # 显示结果
            for record in results:
                self.result_tree.insert('', 'end', values=record)
            
            # 显示结果数量
            messagebox.showinfo('查询结果', f'共找到 {len(results)} 条记录')
            
        except Exception as e:
            messagebox.showerror('查询失败', f'查询失败: {str(e)}')
        finally:
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()
    
    def save_filter_settings(self, settings):
        # 保存筛选设置到文件
        try:
            import json
            with open('filter_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            messagebox.showinfo('保存成功', '筛选设置已保存')
        except Exception as e:
            messagebox.showerror('保存失败', f'保存筛选设置失败: {e}')
    
    def load_filter_settings(self):
        # 从文件加载筛选设置
        try:
            import json
            import os
            if os.path.exists('filter_settings.json'):
                with open('filter_settings.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror('加载失败', f'加载筛选设置失败: {e}')
        return None
    
    def query_by_sn(self):
        """
        通过SN直接查询错误信息
        
        获取用户输入的SN，调用数据库模块查询相关错误记录，
        并在结果表格中显示查询结果
        """
        sn = self.sn_query.get().strip()
        if not sn:
            messagebox.showinfo('提示', '请输入要查询的SN')
            return
            
        # 清空当前结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
            
        try:
            # 查询数据库
            results = self.db.get_error_by_sn(sn)
            
            if not results:
                messagebox.showinfo('查询结果', f'未找到SN为 {sn} 的错误记录')
                return
                
            # 显示结果
            for record in results:
                # 确保显示所有字段：ID, 用户名, SN, 错误信息, 时间
                self.result_tree.insert('', 'end', values=record)
                
            messagebox.showinfo('查询结果', f'共找到 {len(results)} 条记录')
            
        except Exception as e:
            messagebox.showerror('查询失败', f'查询失败: {str(e)}')
    
    def clear_sn_query(self):
        """
        清空SN查询框
        """
        self.sn_query.delete(0, tk.END)
        
    def show_error_details(self, event):
        """
        双击查看错误详情的回调函数
        
        创建一个新窗口显示选中错误记录的完整信息，
        包括ID、姓名、SN、时间和完整的错误信息
        """
        # 获取选中的项
        selected_item = self.result_tree.focus()
        if not selected_item:
            return
        
        # 获取项的值
        values = self.result_tree.item(selected_item, 'values')
        if not values:
            return
        
        # 创建详情窗口
        detail_window = tk.Toplevel(self.root)
        detail_window.title('错误详情')
        detail_window.geometry('600x400')
        
        # 显示详情
        tk.Label(detail_window, text=f'ID: {values[0]}', font=('Arial', 11)).pack(anchor='w', padx=10, pady=5)
        tk.Label(detail_window, text=f'姓名: {values[1]}', font=('Arial', 11)).pack(anchor='w', padx=10, pady=5)
        tk.Label(detail_window, text=f'SN: {values[2]}', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
        tk.Label(detail_window, text=f'时间: {values[4]}', font=('Arial', 11)).pack(anchor='w', padx=10, pady=5)
        
        # 错误信息文本框 - 支持滚动查看
        tk.Label(detail_window, text='报错信息:', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
        
        # 添加滚动条
        text_frame = tk.Frame(detail_window)
        text_frame.pack(padx=10, pady=5, fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        error_text = tk.Text(text_frame, wrap=tk.WORD, width=70, height=15, yscrollcommand=scrollbar.set)
        error_text.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=error_text.yview)
        
        error_text.insert('1.0', values[3])
        error_text.config(state='disabled')  # 设为只读
        
        # 添加复制按钮
        def copy_error_text():
            detail_window.clipboard_clear()
            detail_window.clipboard_append(values[3])
            messagebox.showinfo('复制成功', '错误信息已复制到剪贴板')
            
        tk.Button(detail_window, text='复制错误信息', command=copy_error_text).pack(pady=10)
        
        # 关闭按钮
        tk.Button(detail_window, text='关闭', command=detail_window.destroy).pack(pady=10)
    
    def export_results(self):
        """
        导出查询结果到CSV文件
        
        将当前表格中显示的所有错误记录导出到用户选择的CSV文件中，
        包括ID、姓名、SN、报错信息和时间等字段
        """
        # 获取当前显示的结果
        items = self.result_tree.get_children()
        if not items:
            messagebox.showinfo('导出', '没有可导出的数据')
            return
        
        # 选择保存位置
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV 文件', '*.csv'), ('所有文件', '*.*')],
            title='保存查询结果'
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                # 写入表头
                writer.writerow(['ID', '姓名', 'SN', '报错信息', '时间'])
                
                # 写入数据
                for item in items:
                    values = self.result_tree.item(item, 'values')
                    writer.writerow(values)
            
            messagebox.showinfo('导出成功', f'数据已成功导出到 {file_path}')
        except Exception as e:
            messagebox.showerror('导出失败', f'导出失败: {str(e)}')
    
    def setup_report_frame(self):
        '''
        设置报告生成页面的UI组件
        
        创建报告类型选择、时间范围选择和报告格式选择等控件，以及生成报告按钮
        '''
        # 创建报告配置区域
        config_frame = ttk.LabelFrame(self.report_frame, text='报告配置')
        config_frame.pack(fill='x', padx=10, pady=10)
        
        # 报告类型选择
        report_type_frame = ttk.Frame(config_frame)
        report_type_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(report_type_frame, text='报告类型:', font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.report_type_var = tk.StringVar(value='daily')
        ttk.Radiobutton(report_type_frame, text='日报', variable=self.report_type_var, value='daily').grid(row=0, column=1, padx=10, pady=5)
        ttk.Radiobutton(report_type_frame, text='周报', variable=self.report_type_var, value='weekly').grid(row=0, column=2, padx=10, pady=5)
        ttk.Radiobutton(report_type_frame, text='月报', variable=self.report_type_var, value='monthly').grid(row=0, column=3, padx=10, pady=5)
        ttk.Radiobutton(report_type_frame, text='自定义', variable=self.report_type_var, value='custom').grid(row=0, column=4, padx=10, pady=5)
        
        # 时间范围选择
        date_frame = ttk.Frame(config_frame)
        date_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(date_frame, text='开始日期:', font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.report_start_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.report_start_date.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(date_frame, text='结束日期:', font=('Arial', 11)).grid(row=0, column=2, padx=10, pady=5, sticky='w')
        self.report_end_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.report_end_date.grid(row=0, column=3, padx=10, pady=5)
        
        # 报告格式选择
        format_frame = ttk.Frame(config_frame)
        format_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(format_frame, text='报告格式:', font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        self.report_format_var = tk.StringVar(value='excel')
        ttk.Radiobutton(format_frame, text='Excel', variable=self.report_format_var, value='excel').grid(row=0, column=1, padx=10, pady=5)
        ttk.Radiobutton(format_frame, text='PDF', variable=self.report_format_var, value='pdf').grid(row=0, column=2, padx=10, pady=5)
        ttk.Radiobutton(format_frame, text='CSV', variable=self.report_format_var, value='csv').grid(row=0, column=3, padx=10, pady=5)
        
        # 报告内容选项
        content_frame = ttk.LabelFrame(self.report_frame, text='报告内容')
        content_frame.pack(fill='x', padx=10, pady=10)
        
        # 错误类型统计选项
        self.include_error_types_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(content_frame, text='包含错误类型统计', variable=self.include_error_types_var).pack(anchor='w', padx=10, pady=5)
        
        # 错误频率统计选项
        self.include_error_frequency_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(content_frame, text='包含错误频率统计', variable=self.include_error_frequency_var).pack(anchor='w', padx=10, pady=5)
        
        # 严重程度分析选项
        self.include_severity_analysis_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(content_frame, text='包含严重程度分析', variable=self.include_severity_analysis_var).pack(anchor='w', padx=10, pady=5)
        
        # 可视化图表选项
        self.include_charts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(content_frame, text='包含可视化图表', variable=self.include_charts_var).pack(anchor='w', padx=10, pady=5)
        
        # 生成报告按钮
        button_frame = ttk.Frame(self.report_frame)
        button_frame.pack(fill='x', padx=10, pady=20)
        
        ttk.Button(button_frame, text='生成报告', command=self.generate_report, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text='重置选项', command=self.reset_report_options, width=15).pack(side=tk.LEFT, padx=10)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(self.report_frame, text='报告预览')
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, width=80, height=15)
        self.preview_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.preview_text.insert('1.0', '点击"生成报告"按钮预览报告内容')
    
    def generate_report(self):
        # 生成报告的实现
        report_type = self.report_type_var.get()
        start_date = self.report_start_date.get_date()
        end_date = self.report_end_date.get_date()
        report_format = self.report_format_var.get()
        
        # 清空预览区域
        self.preview_text.delete('1.0', tk.END)
        
        # 生成报告预览
        self.preview_text.insert('1.0', f'报告类型: {report_type}\n')
        self.preview_text.insert(tk.END, f'时间范围: {start_date} 至 {end_date}\n')
        self.preview_text.insert(tk.END, f'报告格式: {report_format}\n\n')
        
        # 根据选项添加内容
        if self.include_error_types_var.get():
            self.preview_text.insert(tk.END, '- 包含错误类型统计\n')
        if self.include_error_frequency_var.get():
            self.preview_text.insert(tk.END, '- 包含错误频率统计\n')
        if self.include_severity_analysis_var.get():
            self.preview_text.insert(tk.END, '- 包含严重程度分析\n')
        if self.include_charts_var.get():
            self.preview_text.insert(tk.END, '- 包含可视化图表\n')
        
        # 提示用户报告生成成功
        messagebox.showinfo('报告生成', '报告预览已生成，实际报告将导出到文件')
    
    def reset_report_options(self):
        # 重置报告选项
        self.report_type_var.set('daily')
        today = datetime.now().date()
        self.report_start_date.set_date(today)
        self.report_end_date.set_date(today)
        self.report_format_var.set('excel')
        self.include_error_types_var.set(True)
        self.include_error_frequency_var.set(True)
        self.include_severity_analysis_var.set(True)
        self.include_charts_var.set(True)
        
        # 清空预览
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', '点击"生成报告"按钮预览报告内容')

def main():
    root = tk.Tk()
    app = ErrorLogApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()


    def batch_import(self):
        '''
        批量导入SN和错误信息的功能
        
        允许用户选择CSV文件并批量导入多条错误记录
        CSV文件格式应包含：姓名,SN,错误信息
        '''
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title='选择CSV文件',
            filetypes=[('CSV文件', '*.csv'), ('所有文件', '*.*')]
        )
        
        if not file_path:
            return  # 用户取消了选择
        
        try:
            # 创建预览对话框
            preview_dialog = tk.Toplevel(self.root)
            preview_dialog.title('导入预览')
            preview_dialog.geometry('800x600')
            preview_dialog.transient(self.root)  # 设置为主窗口的子窗口
            preview_dialog.grab_set()  # 模态对话框
            
            # 创建预览表格
            preview_frame = ttk.Frame(preview_dialog)
            preview_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # 创建表格
            columns = ('username', 'sn', 'error_message')
            preview_tree = ttk.Treeview(preview_frame, columns=columns, show='headings')
            
            # 定义表头
            preview_tree.heading('username', text='姓名')
            preview_tree.heading('sn', text='SN')
            preview_tree.heading('error_message', text='报错信息')
            
            # 定义列宽
            preview_tree.column('username', width=120)
            preview_tree.column('sn', width=150)
            preview_tree.column('error_message', width=450)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=preview_tree.yview)
            preview_tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side='right', fill='y')
            preview_tree.pack(fill='both', expand=True)
            
            # 读取CSV文件并显示预览
            valid_records = []
            invalid_records = []
            
            with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
                csv_reader = csv.reader(csvfile)
                headers = next(csv_reader, None)  # 读取表头
                
                # 检查CSV文件格式
                if not headers or len(headers) < 3:
                    messagebox.showerror('格式错误', 'CSV文件格式不正确，应包含：姓名,SN,错误信息')
                    preview_dialog.destroy()
                    return
                
                # 显示数据预览
                row_count = 0
                for row in csv_reader:
                    if len(row) >= 3:
                        username = row[0].strip()
                        sn = row[1].strip()
                        error_message = row[2].strip()
                        
                        # 验证数据
                        if username and sn and error_message:
                            preview_tree.insert('', 'end', values=(username, sn, error_message))
                            valid_records.append((username, sn, error_message))
                        else:
                            invalid_records.append(row)
                    else:
                        invalid_records.append(row)
                    
                    row_count += 1
                    if row_count >= 100:  # 限制预览数量
                        break
            
            # 显示统计信息
            info_label = ttk.Label(preview_dialog, 
                                  text=f'共读取 {len(valid_records) + len(invalid_records)} 条记录，'
                                       f'有效记录 {len(valid_records)} 条，'
                                       f'无效记录 {len(invalid_records)} 条')
            info_label.pack(pady=5)
            
            # 创建按钮区域
            button_frame = ttk.Frame(preview_dialog)
            button_frame.pack(fill='x', padx=10, pady=10)
            
            def import_records():
                # 导入有效记录到数据库
                success_count = 0
                error_count = 0
                
                conn = self.db.conn()
                if not conn:
                    messagebox.showerror('错误', '无法连接到数据库，请检查网络连接！')
                    preview_dialog.destroy()
                    return
                
                try:
                    for username, sn, error_message in valid_records:
                        if self.db.log_error(username, sn, error_message):
                            success_count += 1
                        else:
                            error_count += 1
                    
                    messagebox.showinfo('导入完成', 
                                       f'成功导入 {success_count} 条记录，'
                                       f'失败 {error_count} 条记录')
                    preview_dialog.destroy()
                except Exception as e:
                    messagebox.showerror('导入错误', f'导入过程中发生错误: {str(e)}')
            
            ttk.Button(button_frame, text='确认导入', command=import_records, width=15).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text='取消', command=preview_dialog.destroy, width=15).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror('错误', f'读取CSV文件失败: {str(e)}')
