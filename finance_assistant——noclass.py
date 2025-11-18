import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DATA_FILE = 'finance_datak.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'expenses': [], 'incomes': [], 'fixed_incomes': []}
    else:
        return {'expenses': [], 'incomes': [], 'fixed_incomes': []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_expense(data, amount, category, note):
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    month = date_str[:7]
    data['expenses'].append({'amount': amount, 'category': category, 'note': note, 'date': date_str, 'month': month})
    save_data(data)

def add_income(data, amount, category, note, is_fixed=False, start_month=None):
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    month = date_str[:7]
    if is_fixed:
        fid = datetime.now().strftime('%Y%m%d%H%M%S%f')
        start = start_month or month
        data['fixed_incomes'].append({'id': fid, 'amount': amount, 'category': category, 'note': note, 'start_month': start})
        apply_fixed_incomes(data, month)
    else:
        data['incomes'].append({'amount': amount, 'category': category, 'note': note, 'date': date_str, 'month': month})
    save_data(data)

def apply_fixed_incomes(data, month):
    for fi in data.get('fixed_incomes', []):
        if fi['start_month'] <= month:
            exists = any(i.get('fixed_id') == fi['id'] and i.get('month') == month for i in data['incomes'])
            if not exists:
                date_str = f"{month}-01 00:00:00"
                data['incomes'].append({'amount': fi['amount'], 'category': fi['category'], 'note': fi.get('note', ''), 'date': date_str, 'month': month, 'fixed_id': fi['id']})
    save_data(data)

def total(data, key):
    return sum(float(i.get('amount', 0)) for i in data.get(key, []))

def refresh_output(output, data):
    output.delete('1.0', tk.END)
    total_inc = total(data, 'incomes')
    total_exp = total(data, 'expenses')
    balance = total_inc - total_exp
    output.insert(tk.END, f'总收入: {total_inc:.2f}\n')
    output.insert(tk.END, f'总支出: {total_exp:.2f}\n')
    output.insert(tk.END, f'余额: {balance:.2f}\n\n最近10条记录:\n')
    all_records = []
    for i in data['incomes']:
        all_records.append({**i, 'type': '收入'})
    for i in data['expenses']:
        all_records.append({**i, 'type': '支出'})
    all_records.sort(key=lambda x: x.get('date', ''), reverse=True)
    for r in all_records[:10]:
        output.insert(tk.END, f"[{r['type']}] {r['date']} {r['category']} {r['amount']} {r.get('note','')}\n")

def open_add_expense(root, data, output):
    win = tk.Toplevel(root)
    win.title('添加支出')

    ttk.Label(win, text='金额:').grid(row=0, column=0, padx=5, pady=5)
    amt = ttk.Entry(win)
    amt.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(win, text='类别:').grid(row=1, column=0, padx=5, pady=5)
    cat = ttk.Combobox(win, values=['食品', '交通', '租金', '娱乐', '其他'])
    cat.grid(row=1, column=1, padx=5, pady=5)
    cat.set('其他')

    ttk.Label(win, text='备注:').grid(row=2, column=0, padx=5, pady=5)
    note = ttk.Entry(win)
    note.grid(row=2, column=1, padx=5, pady=5)

    def submit():
        try:
            amount_val = float(amt.get())
        except:
            messagebox.showerror('错误', '请输入数字金额')
            return
        add_expense(data, amount_val, cat.get(), note.get())
        messagebox.showinfo('完成', '支出已记录')
        win.destroy()
        refresh_output(output, data)

    ttk.Button(win, text='保存', command=submit).grid(row=3, column=0, columnspan=2, pady=10)

def open_add_income(root, data, output):
    win = tk.Toplevel(root)
    win.title('添加收入')

    ttk.Label(win, text='金额:').grid(row=0, column=0, padx=5, pady=5)
    amt = ttk.Entry(win)
    amt.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(win, text='类别:').grid(row=1, column=0, padx=5, pady=5)
    cat = ttk.Entry(win)
    cat.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(win, text='备注:').grid(row=2, column=0, padx=5, pady=5)
    note = ttk.Entry(win)
    note.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(win, text='类型:').grid(row=3, column=0, padx=5, pady=5)
    inc_type = ttk.Combobox(win, values=['一次性收入', '固定月度收入'])
    inc_type.grid(row=3, column=1, padx=5, pady=5)
    inc_type.set('一次性收入')

    def submit():
        try:
            amount_val = float(amt.get())
        except:
            messagebox.showerror('错误', '请输入数字金额')
            return
        if inc_type.get() == '固定月度收入':
            start_month = simpledialog.askstring('起始月份', '输入起始月份 (YYYY-MM)', parent=win)
            add_income(data, amount_val, cat.get(), note.get(), True, start_month)
        else:
            add_income(data, amount_val, cat.get(), note.get())
        messagebox.showinfo('完成', '收入已记录')
        win.destroy()
        refresh_output(output, data)

    ttk.Button(win, text='保存', command=submit).grid(row=4, column=0, columnspan=2, pady=10)

def main():
    data = load_data()
    apply_fixed_incomes(data, datetime.now().strftime('%Y-%m'))

    root = tk.Tk()
    root.title('简易个人理财（无类版本）')
    root.geometry('600x450')

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Button(frame, text='添加支出', command=lambda: open_add_expense(root, data, output)).pack(side=tk.LEFT, padx=5)
    ttk.Button(frame, text='添加收入', command=lambda: open_add_income(root, data, output)).pack(side=tk.LEFT, padx=5)

    output = tk.Text(frame, height=20)
    output.pack(fill=tk.BOTH, expand=True)

    refresh_output(output, data)

    root.mainloop()

if __name__ == '__main__':
    main()
