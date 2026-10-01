
import mysql.connector

# Step 1: Connect Python to MySQL
con = mysql.connector.connect(host="localhost",user="root",password="root", database="genaib2")

cursor = con.cursor()

cursor.execute("SELECT * FROM Employee")
employees = cursor.fetchall();

#print(employees);
#print(type(employees))

for emp in employees:
    print("Employee ID :", emp[0])
    print("Name        :", emp[1])
    print("Age         :", emp[2])
    print("Salary      :", emp[3])
    print("Designation :", emp[4])
    print("--------------------------")


cursor.close()
con.close();
