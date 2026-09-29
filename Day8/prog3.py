employees = [
    {"id": 101, "name": "Thanesh", "salary": 50000},
    {"id": 102, "name": "Ravi", "salary": 40000},
    {"id": 103, "name": "Anu", "salary": 60000,"id":111}
]

for employee in employees:
    print(employee);

print("================================")
# 2. Access the first employee
print(employees[1])

print("================================")
# 3. Access the first employee's name
print(employees[1]["name"])  # Thanesh
