import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import re
from datetime import datetime
import calendar
from pathlib import Path
import os
import json

# Save data files to Documents folder
def get_user_documents_file(filename):
    return str(Path.home() / "Documents" / filename)

FILENAME = get_user_documents_file("bills.json")
BALANCE_FILE = get_user_documents_file("balance.json")

SAMPLE_BILLS = [
    {"amount": 0.00, "due_date": "04/02", "name": "creditone", "paid": True},
    {"amount": 21.78, "due_date": "04/03", "name": "vz affirm", "paid": False},
    {"amount": 21.73, "due_date": "04/05", "name": "chatGPT", "paid": False},
    {"amount": 15.79, "due_date": "04/07", "name": "alpha", "paid": False},
    {"amount": 472.42, "due_date": "04/12", "name": "kia", "paid": False},
    {"amount": 61.00, "due_date": "03/28", "name": "discover", "paid": True}
]

def ensure_bills_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, 'w') as f:
            json.dump(SAMPLE_BILLS, f)

def load_bills(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def save_bills(filename, bills):
    with open(filename, 'w') as f:
        json.dump(bills, f, indent=2)

def save_balance_data(data):
    with open(BALANCE_FILE, 'w') as f:
        json.dump(data, f)

def load_balance_data():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, 'r') as f:
            return json.load(f)
    return {"balance": 0.0}

def advance_date(mmdd_str):
    month, day = map(int, mmdd_str.split('/'))
    year = datetime.now().year
    try:
        datetime(year, month, day)
    except ValueError:
        return mmdd_str
    new_month = month + 1 if month < 12 else 1
    new_year = year if new_month != 1 else year + 1
    last_day = calendar.monthrange(new_year, new_month)[1]
    new_day = min(day, last_day)
    return f"{new_month:02d}/{new_day:02d}"

class FinanceApp:
    def __init__(self, root, bills):
        self.root = root
        self.bills = bills
        self.widgets = []

        self.balance_data = load_balance_data()
        self.root.title("Bill Tracker")
        self.root.configure(bg="#f5f5f5")

        self.main_frame = tk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#f5f5f5", foreground="#333", font=("Helvetica Neue", 10))
        style.configure("TButton", background="#e0e0e0", foreground="#333", font=("Helvetica Neue", 10))
        style.configure("TCheckbutton", background="#f5f5f5", foreground="#333")

        ttk.Label(self.main_frame, text="Total Deposits:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.balance_var = tk.DoubleVar(value=self.balance_data.get("balance", 0.0))
        self.balance_label = ttk.Label(self.main_frame, textvariable=self.balance_var)
        self.balance_label.grid(row=0, column=1, pady=4, sticky="w")

        ttk.Button(self.main_frame, text="+ Add Funds", command=self.add_funds).grid(row=0, column=2, padx=4)
        ttk.Button(self.main_frame, text="- Subtract Funds", command=self.subtract_funds).grid(row=0, column=3, padx=4)

        headers = ["Date", "Name", "Amount", "Paid", ""]
        for col, header in enumerate(headers):
            ttk.Label(self.main_frame, text=header).grid(row=1, column=col, padx=6, pady=4)

        self.add_button = ttk.Button(self.main_frame, text="+ Add Bill", command=self.add_blank_bill)
        self.save_button = ttk.Button(self.main_frame, text="Save Changes", command=self.save_changes)
        self.roll_button = ttk.Button(self.main_frame, text="Roll Over to Next Month", command=self.rollover_bills)

        for idx, bill in enumerate(self.bills):
            self.add_bill_row(bill)

        self.total_label = ttk.Label(self.main_frame, text="")
        self.total_label.grid(row=len(self.widgets)+2, column=0, columnspan=5, pady=6)
        self.update_total()

        self.reposition_action_buttons()

    def add_funds(self):
        amount = simpledialog.askfloat("Add Funds", "Enter amount to add:", minvalue=0.01)
        if amount:
            self.balance_data["balance"] += amount
            self.balance_var.set(self.balance_data["balance"])
            self.update_total()

    def subtract_funds(self):
        amount = simpledialog.askfloat("Subtract Funds", "Enter amount to subtract:", minvalue=0.01)
        if amount:
            self.balance_data["balance"] -= amount
            self.balance_var.set(self.balance_data["balance"])
            self.update_total()

    def add_bill_row(self, bill=None):
        date_var = tk.StringVar(value=bill['due_date'] if bill else "")
        name_var = tk.StringVar(value=bill['name'] if bill else "")
        amount_var = tk.StringVar(value=f"{bill['amount']:.2f}" if bill else "0.00")
        paid_var = tk.BooleanVar(value=bill['paid'] if bill else False)

        row = len(self.widgets) + 2
        self.create_bill_widgets(date_var, name_var, amount_var, paid_var, row)
        self.widgets.append((date_var, name_var, amount_var, paid_var))
        self.reposition_action_buttons()

    def delete_bill_row(self, index):
        for widget in self.main_frame.grid_slaves(row=index + 2):
            widget.destroy()
        self.widgets.pop(index)
        for i in range(index, len(self.widgets)):
            date_var, name_var, amount_var, paid_var = self.widgets[i]
            self.create_bill_widgets(date_var, name_var, amount_var, paid_var, i + 2, update=True)
        self.reposition_action_buttons()
        self.update_total()

    def create_bill_widgets(self, date_var, name_var, amount_var, paid_var, row, update=False):
        ttk.Entry(self.main_frame, textvariable=date_var, width=10).grid(row=row, column=0, padx=5, pady=2)
        ttk.Entry(self.main_frame, textvariable=name_var, width=20).grid(row=row, column=1, padx=5, pady=2)
        ttk.Entry(self.main_frame, textvariable=amount_var, width=8).grid(row=row, column=2, padx=5, pady=2)
        ttk.Checkbutton(self.main_frame, variable=paid_var, command=self.update_total).grid(row=row, column=3, padx=5, pady=2)
        delete_btn = ttk.Button(self.main_frame, text="❌", width=2, command=lambda r=row: self.delete_bill_row(r - 2))
        delete_btn.grid(row=row, column=4, padx=5, pady=2)

    def add_blank_bill(self):
        self.add_bill_row()
        self.update_total()

    def reposition_action_buttons(self):
        row = len(self.widgets) + 3
        self.add_button.grid(row=row, column=0, pady=4)
        self.save_button.grid(row=row, column=1, pady=4)
        self.roll_button.grid(row=row, column=2, columnspan=2, pady=4)

    def update_total(self):
        total = 0.0
        balance_after = self.balance_data["balance"]
        for (_, _, amount_var, paid_var) in self.widgets:
            try:
                amount = float(amount_var.get())
                if not paid_var.get():
                    total += amount
                if paid_var.get():
                    balance_after -= amount
            except ValueError:
                pass
        balance_color = "red" if balance_after < 0 else "#333"
        self.total_label.config(text=f"Total unpaid: ${total:.2f} | Remaining balance: ${balance_after:.2f}", foreground=balance_color)

    def save_changes(self):
        updated_bills = []
        errors = []
        for (date_var, name_var, amount_var, paid_var) in self.widgets:
            try:
                amount = float(amount_var.get())
                due_date = date_var.get().strip()
                name = name_var.get().strip()
                if not re.match(r'^\d{2}/\d{2}$', due_date):
                    raise ValueError("Invalid date format")
                updated_bills.append({
                    'amount': amount,
                    'due_date': due_date,
                    'name': name,
                    'paid': paid_var.get()
                })
            except ValueError as e:
                errors.append(f"{name_var.get()} — {str(e)}")

        if errors:
            messagebox.showerror("Invalid Entries", "\n".join(errors))
            return

        self.bills = updated_bills
        save_bills(FILENAME, self.bills)
        save_balance_data(self.balance_data)
        self.update_total()
        messagebox.showinfo("Saved", "Changes saved to file!")

    def rollover_bills(self):
        for (date_var, _, _, paid_var) in self.widgets:
            date_var.set(advance_date(date_var.get()))
            paid_var.set(False)
        self.balance_data["balance"] = 0.0
        self.balance_var.set(0.0)
        self.save_changes()

if __name__ == "__main__":
    ensure_bills_file()
    root = tk.Tk()
    bills = load_bills(FILENAME)
    app = FinanceApp(root, bills)
    root.mainloop()
