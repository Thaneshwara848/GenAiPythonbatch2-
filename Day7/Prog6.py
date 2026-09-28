students = {"Ravi", "Anu", "Kiran", "Ravi", "Anu"}
print("Original set:", students)  # Duplicates are removed

# 1. add() — Add a single element
students.add("Thanesh")
print("After add:", students);

# 2. update() — Add multiple elements
students.update(["Divya", "Rahul"])
print("After update:", students)

students.remove("Ravi");
# remove : if value : good , if no value ,no error
print("After remove:", students)

# 4. discard() — Remove an element without an error if missing
students.discard("RaviKumar");
# discard : if value : good , if no value ,no error
print("After discard:", students) ;


removed_student = students.pop()
print("Removed student:", removed_student)
print("After pop:", students)