class BankAccount:
    def __init__(self, acc_num, cust_name, balance):
        self.acc_num = acc_num
        self.cust_name = cust_name

        if balance < 0:
            print("Negative starting balance! Setting balance to 0.")
            self.balance = 0
        else:
            self.balance = balance

    def show_balance(self):
        print("Available balance:", self.balance)

    def deposit(self, amount):
        if amount <= 0:
            print("Deposit amount must be greater than zero.")
        else:
            self.balance = self.balance + amount
            print("After depositing, balance:", self.balance)

    def withdraw(self, amount):
        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
        elif amount > self.balance:
            print("Insufficient balance!")
            self.show_balance()
        else:
            self.balance = self.balance - amount
            print("After withdrawal, balance:", self.balance)


a1 = BankAccount(111, "Thanesh", 10000)
a1.show_balance()

# Validate input before converting it to an integer.
depo = input("How much do you want to deposit? ").strip()

if depo.isascii() and depo.isdigit():
    a1.deposit(int(depo))
else:
    print("Invalid amount! Enter a positive whole number.")

withdrawamount = input("How much do you want to withdraw? ").strip()

if withdrawamount.isascii() and withdrawamount.isdigit():
    a1.withdraw(int(withdrawamount))
else:
    print("Invalid amount! Enter a positive whole number.")

a1.show_balance()