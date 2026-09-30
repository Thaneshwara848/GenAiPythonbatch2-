import mysql.connector

# Step 1: Connect Python to MySQL
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="genAIB2"
)

cursor = con.cursor()

# Step 2: Insert 3 records using for loop
noofEmp = int(input("How many Employee Record you want to Inser ? "))
for i in range(noofEmp):

    print("\nEnter Employee", i + 1, "Details")

    id = int(input("Enter the ID : "))
    name = input("Enter the Name : ")
    age = int(input("Enter the Age : "))
    salary = int(input("Enter the SALARY : "))
    desig = input("Enter the Designation : ")

    # Step 3: Insert into MySQL
    sql = """
    INSERT INTO Employee(eid, name, age, salary, desig)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (id, name, age, salary, desig)

    cursor.execute(sql, values)

    print("Employee inserted successfully")

# Step 4: Save all 3 records
con.commit()

# Step 5: Close connection
cursor.close()
con.close()