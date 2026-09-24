class BankAccount:
    def __init__(self,acc_num,cust_name, balance):
        self.acc_num= acc_num;
        self.cust_name=cust_name;
        self.balance=balance    
        
    def show_balance(self):
        print("My Avaliable Balalance is :  " , self.balance)    
      
    def deposit(self,amount) :
        self.balance=self.balance+amount; 
        print("After Depositing ...",self.balance)
        
    def withdraw(self,amount):
        self.balance= self.balance-amount;  
        print("After Withdrawn ",self.balance)

a1 = BankAccount(111,"Thanesh",-10000);
a1.show_balance();

depo=int(input("how Much Amount You Want to Deposit "));
a1.deposit(depo);

withdrawamount=int(input("how Much Amount You Want to WithDraw "));
a1.withdraw(withdrawamount);

