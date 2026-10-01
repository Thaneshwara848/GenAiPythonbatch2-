
import mysql.connector

# Step 1: Connect Python to MySQL
con = mysql.connector.connect(host="localhost",user="root",password="root", database="genaib2")

# Step 2: Create cursor
cursor = con.cursor()

# Step 3: Take input from user
eid = int(input("Enter Employee ID: "))
salary = int(input("Enter New Salary: "))

# Step 4: Update query
sql = """
UPDATE Employee
SET salary = %s
WHERE eid = %s
"""

values = (salary, eid)

# Step 5: Execute query
cursor.execute(sql, values)

# Step 6: Save changes
con.commit()

if cursor.rowcount > 0:
    print("Employee salary updated successfully")
else:
    print("Employee ID not found")

# Step 7: Close connection
cursor.close()
con.close()