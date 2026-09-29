employee = {
    "id": 101,
    "name": "Thanesh",
    "age": 30,
    "salary": 50000
}

print("original : " , employee) ;
#============ Reading values===========
print("Employee Name  : ", employee["name"]);
print("EMployee Age : ", employee["age"]);
print("EMployee Salary : ", employee.get("salary"));

print("Keys : ", employee.keys());

print("VALUE  : ", employee.values());

print("Items  : ", employee.items());

print("====================================")
employee["salary"]=60000;
print("After update  : ",employee);

employee.pop("salary");
print("After DELETE  : ", employee)

