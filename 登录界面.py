#登录界面
#utf-8
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import 测试
import 维修
import 数据库
import mysql.connector
from datetime import datetime 
from mysql.connector import Error


def login():
    username=entry_username.get()
    password=entry_password.get()
    bumeng=entry_bumeng.get()
    print(f'{username},{password},{bumeng}')
    if username and password:
        try:
            conn= mysql.connector.connect(
                    host='110.41.57.192',
                    user='root',
                    password='Zzm8023.',
                    database='ZGWL_db',
                    port=3306
                )
            cursor = conn.cursor()
            cursor.execute('SELECT user,password FROM USERS;')
            result=cursor.fetchall()
            for i in result:
                if username ==i[0]:
                    if password==i[1]:
                        if bumeng == '测试':
                            root_login.destroy()
                            测试.home()            
                        elif bumeng =='维修':
                            root_login.destroy()
                            维修.weixiu_windo()
                        else:
                            messagebox.showerror("错误提示", "部门有误，请输入测试或者维修！")
                else:
                    messagebox.showerror('错误','请输入正确的账号或密码,若没有账号请先注册!')
                    
        except mysql.connector.Error as err:
            messagebox.showerror('错误','账号或密码不对,请重新输入！')
    else:
        messagebox.showerror('错误','账号密码不能为空请重新输入！')
        
            

def zhuche():
    root_zhuce=tk.Tk()
    root_zhuce.title('账号注册')
    root_zhuce.geometry('400x300')

    tk.Label(root_zhuce,text='账号：').place(x=112,y=70)
    user=tk.Entry(root_zhuce)
    user.place(x=150,y=70)

    tk.Label(root_zhuce,text='密码：').place(x=112,y=120)
    password=tk.Entry(root_zhuce,show='*')
    password.place(x=150,y=120)

    tk.Label(root_zhuce,text='确认密码：').place(x=90,y=170)
    password1=tk.Entry(root_zhuce,show='*')
    password1.place(x=150,y=170)

    def mima():
        user_name=user.get()
        password_name=password.get()
        password1_name=password1.get()
        time_name=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if user_name and password_name and password1_name !='':
            if password1_name !=password_name:
                messagebox.showerror('错误','两次密码不一样！请重新输入。')
            else:
                try:
                    #写入数据库并关闭注册界面
                    conn= mysql.connector.connect(
                    host='110.41.57.192',
                    user='root',
                    password='Zzm8023.',
                    database='ZGWL_db',
                    port=3306
                )
                    cursor = conn.cursor()

                    sql=f'INSERT INTO  USERS(user,password,time) VALUES(%s,%s,%s)'
                    values=(user_name,password_name,time_name)
                    cursor.execute(sql,values)
                    conn.commit()
                    messagebox.showinfo('成功','注册成功！')
                except mysql.connector.Error as err:
                    print(f'{err}')
                    messagebox.showerror('错误','添加失败')   
            root_zhuce.destroy()         
                
        else:
            messagebox.showerror('错误','账号密码不能为空！')
            

    tk.Button(root_zhuce,text='确认',command=mima).place(x=180,y=220)
    root_zhuce.mainloop()
    pass
root_login=tk.Tk()
root_login.title('用户登录')
root_login.geometry('400x300')

tk.Label(root_login,text='欢迎使用数据流转软件！').place(x=145,y=20)

tk.Label(root_login,text='用户名：').place(x=100,y=70)
entry_username=tk.Entry(root_login)
entry_username.place(x=150,y=70)

tk.Label(root_login,text='密码：').place(x=112,y=120)
entry_password=tk.Entry(root_login,show='*')
entry_password.place(x=150,y=120)

tk.Label(root_login,text='部门(测试/维修)：').place(x=52,y=170)
entry_bumeng=tk.Entry(root_login)
entry_bumeng.place(x=150,y=170)

button_zhu=tk.Button(root_login,text='登录',command=login)
button_zhu.place(x=120,y=220)

button_zhuche=tk.Button(root_login,text='注册',command=zhuche)
button_zhuche.place(x=250,y=220)
root_login.mainloop()


