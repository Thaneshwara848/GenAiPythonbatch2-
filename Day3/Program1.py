num1=int(input("ENter First Number "));         #100
num2 =int(input("ENter Second number "));       #200
num3 =int(input("ENter Third number "));        #300 
    #100 > 200 
    
   #100 >= 200 and 100 >= 300  
if num1 >= num2  and num1 >=num3:
    largest=num1;
elif num2 >=num1 and num2>=num3 :
   largest=num2;
else :
    largest=num3;
    
print("The Largest number is  ", largest )
    