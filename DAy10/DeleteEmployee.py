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

# Step 3: Ask how many employees to delete
n = int(input("Enter number of employees to delete: "))

# Step 4: Loop
for i in range(n):

    print("\nDelete Employee", i + 1)

    eid = int(input("Enter Employee ID to delete: "))

    sql = """
    DELETE FROM Employee
    WHERE eid = %s
    """

    values = (eid,)

    cursor.execute(sql, values)

    if cursor.rowcount > 0:
        print("Employee deleted successfully")
    else:
        print("Employee ID not found")

# Step 5: Save changes
con.commit()

# Step 6: Close connection
cursor.close()
con.close()

print("\nDelete operation completed")