num1 =  int(input("Enter First Number "));
num2 =  int(input("Enter Second Number "));
operator = input("Enter a Operation one from this  : + , - , * , /  :  ");

if operator=="+":
    res = num1 + num2 ;
    print("Sum of N1  + N2  : " , res) ;
elif operator=="-":
    res = num1 - num2 ;
    print("Sum of N1  -  N2 : " , res) ;
elif operator=="*":
    res = num1 * num2 ;
    print("Multiplation  of N1  -  N2 : " ,res) ;
elif operator=="/":
    res = num1 / num2 ;
    print("Divison   of N1  -  N2 : " , res) ;
else : 
    print("Boss please enter the correct Operation")