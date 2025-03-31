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
        
        # 初始化录入页面
        self.setup_input_frame()
        
        # 初始化查询页面
        self.setup_query_frame()
    
    def setup_input_frame(self):
        # 创建输入区域 - 简化为只需要姓名、SN和错误信息
        tk.Label(self.input_frame, text='姓名：', font=('Arial', 12)).place(x=30, y=50)
        tk.Label(self.input_frame, text='SN：', font=('Arial', 12)).place(x=350, y=50)
        tk.Label(self.input_frame, text='报错信息：', font=('Arial', 12)).place(x=30, y=100)
        
        self.name = tk.Entry(self.input_frame, width=25, font=('Arial', 11))
        self.name.place(x=80, y=50)
        self.sn = tk.Entry(self.input_frame, width=30, font=('Arial', 11))
        self.sn.place(x=385, y=50)
        self.baocuo = tk.Text(self.input_frame, width=100, height=20)
        self.baocuo.place(x=95, y=100)
        
        # 创建确认按钮
        tk.Button(self.input_frame, text='确认维护', command=self.queren, width=15).place(x=150, y=500)
        tk.Button(self.input_frame, text='清空输入', command=self.clear_input, width=15).place(x=350, y=500)
    
    def setup_query_frame(self):
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
                
            self.db.log_error(name_get, sn_get, baocuo_get)
            messagebox.showinfo('成功', f'SN: {sn_get} 的错误信息已成功记录！')
            self.clear_input()  # 清空输入
        except Exception as e:
            messagebox.showerror('错误', f'记录错误信息失败: {str(e)}')
    
    def clear_input(self):
        self.name.delete(0, tk.END)
        self.sn.delete(0, tk.END)
        self.baocuo.delete('1.0', tk.END)
    
    def filter_logs(self):
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
                SELECT id, username, error_message, log_time
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
            for (log_id, user, msg, time) in results:
                self.result_tree.insert('', 'end', values=(log_id, user, msg[:50], time.strftime('%Y-%m-%d %H:%M:%S')))
            
            # 显示结果数量
            messagebox.showinfo('查询结果', f'共找到 {len(results)} 条记录')
            
        except Exception as e:
            messagebox.showerror('查询失败', f'查询失败: {e}')
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
                SELECT id, username, error_message, log_time
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
                query += " AND error_message LIKE %s"
                params.append(f"%SN: {sn}%")  # 查找SN字段
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
            for (log_id, user, msg, time) in results:
                self.result_tree.insert('', 'end', values=(log_id, user, msg[:50], time.strftime('%Y-%m-%d %H:%M:%S')))
            
            # 显示结果数量
            messagebox.showinfo('查询结果', f'共找到 {len(results)} 条记录')
            
        except Exception as e:
            messagebox.showerror('查询失败', f'查询失败: {e}')
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
        """通过SN直接查询错误信息"""
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
                self.result_tree.insert('', 'end', values=record)
                
            messagebox.showinfo('查询结果', f'共找到 {len(results)} 条记录')
            
        except Exception as e:
            messagebox.showerror('查询失败', f'查询失败: {str(e)}')
    
    def clear_sn_query(self):
        """清空SN查询框"""
        self.sn_query.delete(0, tk.END)
        
    def show_error_details(self, event):
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
        
        # 错误信息文本框
        tk.Label(detail_window, text='报错信息:', font=('Arial', 11, 'bold')).pack(anchor='w', padx=10, pady=5)
        error_text = tk.Text(detail_window, wrap=tk.WORD, width=70, height=15)
        error_text.pack(padx=10, pady=5, fill='both', expand=True)
        error_text.insert('1.0', values[3])
        error_text.config(state='disabled')  # 设为只读
        
        # 关闭按钮
        tk.Button(detail_window, text='关闭', command=detail_window.destroy).pack(pady=10)
    
    def export_results(self):
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
            messagebox.showerror('导出失败', f'导出失败: {e}')

def main():
    root = tk.Tk()
    app = ErrorLogApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

