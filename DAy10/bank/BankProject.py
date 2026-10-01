import mysql.connector

# Step 1: Connect Python to MySQL
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="bankdb"
)

cursor = con.cursor()


while True:

    print("\n====================================")
    print("          BANK ACCOUNT MENU")
    print("====================================")
    print("1. Create Account")
    print("2. Display All Accounts")
    print("3. Get Account By Account Number")
    print("4. Deposit Money")
    print("5. Withdraw Money")
    print("6. Delete Account")
    print("7. Delete All Accounts")
    print("8. Exit")
    print("====================================")

    choice = int(input("Enter your choice: "))


    # ---------------------------------
    # 1. CREATE ACCOUNT
    # ---------------------------------
    if choice == 1:

        account_no = int(input("Enter Account Number: "))
        name = input("Enter Customer Name: ")
        balance = int(input("Enter Opening Balance: "))
        account_type = input("Enter Account Type: ")
        branch = input("Enter Branch Name: ")

        sql = """
        INSERT INTO BankAccount
        (account_no, name, balance, account_type, branch)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            account_no,
            name,
            balance,
            account_type,
            branch
        )

        cursor.execute(sql, values)

        con.commit()

        print("Bank Account Created Successfully")


    # ---------------------------------
    # 2. DISPLAY ALL ACCOUNTS
    # ---------------------------------
    elif choice == 2:

        cursor.execute("SELECT * FROM BankAccount")

        accounts = cursor.fetchall()

        if len(accounts) == 0:
            print("No Bank Accounts Found")

        else:

            for acc in accounts:

                print("\n---------------------------")
                print("Account Number :", acc[0])
                print("Name           :", acc[1])
                print("Balance        :", acc[2])
                print("Account Type   :", acc[3])
                print("Branch         :", acc[4])


    # ---------------------------------
    # 3. GET ACCOUNT BY NUMBER
    # ---------------------------------
    elif choice == 3:

        account_no = int(input("Enter Account Number: "))

        sql = """
        SELECT * FROM BankAccount
        WHERE account_no = %s
        """

        values = (account_no,)

        cursor.execute(sql, values)

        acc = cursor.fetchone()

        if acc is not None:

            print("\nAccount Found")
            print("---------------------------")
            print("Account Number :", acc[0])
            print("Name           :", acc[1])
            print("Balance        :", acc[2])
            print("Account Type   :", acc[3])
            print("Branch         :", acc[4])

        else:
            print("Account Not Found")


    # ---------------------------------
    # 4. DEPOSIT MONEY
    # ---------------------------------
    elif choice == 4:

        account_no = int(input("Enter Account Number: "))
        amount = int(input("Enter Deposit Amount: "))

        sql = """
        UPDATE BankAccount
        SET balance = balance + %s
        WHERE account_no = %s
        """

        values = (amount, account_no)

        cursor.execute(sql, values)

        con.commit()

        if cursor.rowcount > 0:
            print("Amount Deposited Successfully")

        else:
            print("Account Not Found")


    # ---------------------------------
    # 5. WITHDRAW MONEY
    # ---------------------------------
    elif choice == 5:

        account_no = int(input("Enter Account Number: "))
        amount = int(input("Enter Withdraw Amount: "))

        sql = """
        SELECT balance FROM BankAccount
        WHERE account_no = %s
        """

        values = (account_no,)

        cursor.execute(sql, values)

        account = cursor.fetchone()

        if account is None:

            print("Account Not Found")

        else:

            balance = account[0]

            if balance >= amount:

                sql = """
                UPDATE BankAccount
                SET balance = balance - %s
                WHERE account_no = %s
                """

                values = (amount, account_no)

                cursor.execute(sql, values)

                con.commit()

                print("Amount Withdrawn Successfully")

            else:
                print("Insufficient Balance")


    # ---------------------------------
    # 6. DELETE ACCOUNT
    # ---------------------------------
    elif choice == 6:

        account_no = int(input("Enter Account Number: "))

        sql = """
        DELETE FROM BankAccount
        WHERE account_no = %s
        """

        values = (account_no,)

        cursor.execute(sql, values)

        con.commit()

        if cursor.rowcount > 0:
            print("Account Deleted Successfully")

        else:
            print("Account Not Found")


    # ---------------------------------
    # 7. DELETE ALL ACCOUNTS
    # ---------------------------------
    elif choice == 7:

        cursor.execute("DELETE FROM BankAccount")

        con.commit()

        print(cursor.rowcount, "Accounts Deleted Successfully")


    # ---------------------------------
    # 8. EXIT
    # ---------------------------------
    elif choice == 8:

        print("Thank You for Using Bank Application")
        break


    else:

        print("Invalid Choice")


cursor.close()
con.close()