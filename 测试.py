#utf-8
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

def home():
    root_zhu=tk.Tk()
    root_zhu.title('测试报错记录')
    root_zhu.geometry('1000x600')

    tk.Label(root_zhu,text='部门：',bg='#f0f0f0').place(x=30,y=50)
    tk.Label(root_zhu,text='工号：',bg='#f0f0f0').place(x=200,y=50)
    tk.Label(root_zhu,text='姓名：',bg='#f0f0f0').place(x=350,y=50)
    tk.Label(root_zhu,text='SN：',bg='#f0f0f0').place(x=500,y=50)
    tk.Label(root_zhu,text='报错信息：',bg='#f0f0f0').place(x=30,y=150)

    bumeng=tk.Entry(root_zhu,width=17)
    bumeng.place(x=65,y=50)
    gonghao=tk.Entry(root_zhu,width=15)
    gonghao.place(x=235,y=50)
    name=tk.Entry(root_zhu,width=15)
    name.place(x=385,y=50)
    sn=tk.Entry(root_zhu,width=30)
    sn.place(x=535,y=50)
    baocuo=tk.Text(root_zhu,width=100,height=20)
    baocuo.place(x=95,y=150)

    def queren():
        bumeng_get=bumeng.get()
        gonghao_get=gonghao.get()
        name_get=name.get()
        sn_get=sn.get()
        baocuo_get=baocuo.get('1.0','end')#若行数超过1时需要索引获取起始位置和结尾
        writetime=datetime.now()
        if bumeng_get and gonghao_get and name_get and sn_get and baocuo_get != '':
            pass#待写入数据库
        else:
            messagebox.showerror('错误','请检查各项信息不能为空！')
        print(f'{bumeng_get},{gonghao_get},{name_get},{sn_get},{baocuo_get},{writetime}')

    buttom_queren=tk.Button(root_zhu,text='确认维护',command=queren).place(x=150,y=500)



    root_zhu.mainloop()

