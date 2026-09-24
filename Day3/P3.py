age = int(input("Enter your age: "))
gender = input("Enter your gender (male/female): ")
if gender == "female" and age >= 18:
    print("Eligible for marriage")
if gender == "male" and age >= 21:
    print("Eligible for marriage")