import mysql.connector

# Step 1: Connect Python to MySQL
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="genAIB2"
)

cursor = con.cursor()

# Step 2: Take employee ID from user
id = int(input("Enter Employee ID to Delete : "))

# Step 3: Delete employee from MySQL
sql = "DELETE FROM Employee WHERE eid = %s"

values = (id,)

cursor.execute(sql, values)

# Step 4: Save changes
con.commit()

# Step 5: Check result
if cursor.rowcount > 0:
    print("Employee deleted successfully")
else:
    print("Employee ID not found")

# Step 6: Close connection
cursor.close()
con.close()