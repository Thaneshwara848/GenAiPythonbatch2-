import mysql.connector

# Step 1: Connect Python to MySQL
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="genaib2"
)

# Step 2: Create cursor
cursor = con.cursor()


while True:

    print("\n================================")
    print("       EMPLOYEE MENU")
    print("================================")
    print("1. Insert Employee")
    print("2. Display All Employees")
    print("3. Get Employee By ID")
    print("4. Update Employee Salary")
    print("5. Delete Employee")
    print("6. Delete All Employees")
    print("7. Exit")
    print("================================")

    choice = int(input("Enter your choice: "))


    # ---------------------------------
    # 1. INSERT EMPLOYEE
    # ---------------------------------
    if choice == 1:

        n = int(input("Enter number of employees: "))

        for i in range(n):

            print("\nEnter details of Employee", i + 1)

            eid = int(input("Enter Employee ID: "))
            name = input("Enter Name: ")
            age = int(input("Enter Age: "))
            salary = int(input("Enter Salary: "))
            desig = input("Enter Designation: ")

            sql = """
            INSERT INTO Employee(eid, name, age, salary, desig)
            VALUES (%s, %s, %s, %s, %s)
            """

            values = (eid, name, age, salary, desig)

            cursor.execute(sql, values)

            print("Employee inserted successfully")

        con.commit()


    # ---------------------------------
    # 2. DISPLAY ALL EMPLOYEES
    # ---------------------------------
    elif choice == 2:

        sql = "SELECT * FROM Employee"

        cursor.execute(sql)

        employees = cursor.fetchall()

        if len(employees) == 0:
            print("No Employees Found")
        else:

            print("\nEmployee Records")
            print("----------------------------------------------------------")

            for emp in employees:
                print("ID          :", emp[0])
                print("Name        :", emp[1])
                print("Age         :", emp[2])
                print("Salary      :", emp[3])
                print("Designation :", emp[4])
                print("----------------------------------------------------------")


    # ---------------------------------
    # 3. GET EMPLOYEE BY ID
    # ---------------------------------
    elif choice == 3:

        eid = int(input("Enter Employee ID: "))

        sql = """
        SELECT * FROM Employee
        WHERE eid = %s
        """

        values = (eid,)

        cursor.execute(sql, values)

        emp = cursor.fetchone()

        if emp is not None:

            print("\nEmployee Found")
            print("----------------------------")
            print("ID          :", emp[0])
            print("Name        :", emp[1])
            print("Age         :", emp[2])
            print("Salary      :", emp[3])
            print("Designation :", emp[4])

        else:
            print("Employee ID not found")


    # ---------------------------------
    # 4. UPDATE EMPLOYEE SALARY
    # ---------------------------------
    elif choice == 4:

        eid = int(input("Enter Employee ID: "))
        salary = int(input("Enter New Salary: "))

        sql = """
        UPDATE Employee
        SET salary = %s
        WHERE eid = %s
        """

        values = (salary, eid)

        cursor.execute(sql, values)

        con.commit()

        if cursor.rowcount > 0:
            print("Employee salary updated successfully")
        else:
            print("Employee ID not found")


    # ---------------------------------
    # 5. DELETE EMPLOYEE
    # ---------------------------------
    elif choice == 5:

        eid = int(input("Enter Employee ID to delete: "))

        sql = """
        DELETE FROM Employee
        WHERE eid = %s
        """

        values = (eid,)

        cursor.execute(sql, values)

        con.commit()

        if cursor.rowcount > 0:
            print("Employee deleted successfully")
        else:
            print("Employee ID not found")


    # ---------------------------------
    # 6. DELETE ALL EMPLOYEES
    # ---------------------------------
    elif choice == 6:

        sql = "DELETE FROM Employee"

        cursor.execute(sql)

        con.commit()

        print(cursor.rowcount, "Employees deleted successfully")


    # ---------------------------------
    # 7. EXIT
    # ---------------------------------
    elif choice == 7:

        print("Program terminated")
        break


    # ---------------------------------
    # INVALID OPTION
    # ---------------------------------
    else:

        print("Invalid choice")


# Close connection
cursor.close()
con.close()