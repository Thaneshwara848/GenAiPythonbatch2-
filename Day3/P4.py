num = int(input("enter num:"))

if num%5 == 0 and num%11 == 0:
  print("number accepted")
else:
  print("not accepted")
  
  
  
------------------------
num = int(input("Enter the num: "))
if num%5 == 0 and num%11 == 0:
    print("Divisible by both the numbers 5 and 11")
elif num%5 == 0 and num%11 != 0:
    print("Divisible only by 5")
elif num%11 == 0 and num%11 != 5:
    print("Divisible only by 11")
else:
    print("Not divisible by both the number 5 and 11")
    


