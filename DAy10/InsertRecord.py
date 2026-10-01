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

# Step 3: Ask number of employees
n = int(input("Enter number of employees: "))

# Step 4: Loop to take employee details
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

# Step 5: Save all changes
con.commit()

# Step 6: Close connection
cursor.close()
con.close()

print("\nAll Employees Inserted Successfully")