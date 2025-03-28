#utf-8
from datetime import datetime
import tkinter as tk
import re


def weixiu_windo():
    root_weixiu=tk.Tk()
    root_weixiu.title('维修详情查看')
    root_weixiu.geometry('600x200')
    
    tk.Label(root_weixiu,text='查询SN：').place(x=50,y=50)
    sn=tk.Entry(root_weixiu,width=40)
    sn.place(x=100,y=50)

    def weixiu():
        sn_get=sn.get()
        print(sn_get)
        a=r'210200A\w+'
        if re.findall(a,sn_get):
            print('ok')
            root_logfind=tk.Tk()
            root_logfind.title('报错详情')
            root_logfind.geometry('1000x600')
            
            sn_copy=tk.Text(root_logfind,width=130,height=1)
            sn_copy.insert('1.0',f'SN：{sn_get}')
            sn_copy.config(state='disabled')
            sn_copy.place(x=50,y=50)

            time_copy=tk.Text(root_logfind,width=130,height=1)
            time_copy.insert('1.0',f'送修时间：')
            time_copy.config(state='disabled')
            time_copy.place(x=50,y=150)

            name_copy=tk.Text(root_logfind,width=130,height=1)
            name_copy.insert('1.0',f'送修人员：')
            name_copy.config(state='disabled')
            name_copy.place(x=50,y=250)

            error_copy=tk.Text(root_logfind,width=130,height=7)
            error_copy.insert('1.0',f'报错详情：')
            error_copy.config(state='disabled')
            error_copy.place(x=50,y=350)

            def querenweixiu():
                timenow=datetime.now()
                print(timenow)
                pass
            def close():
                root_logfind.destroy()
            info_set=tk.Button(root_logfind,text='确认维修',command=querenweixiu).place(x=200,y=500)
            info_close=tk.Button(root_logfind,text='关闭',command=close).place(x=800,y=500)

            root_logfind.mainloop()
        else:
            print('error')
        

    sn_button=tk.Button(root_weixiu,text='确定',command=weixiu).place(x=500,y=50)


    root_weixiu.mainloop()


