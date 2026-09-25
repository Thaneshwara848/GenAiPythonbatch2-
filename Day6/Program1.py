try :
    fnumber=int(input("ENter First Number : "));
    snumber=int(input("ENter Second Number : "));
    result = fnumber / snumber;
    print("Result is  : " , result) ;
    
    
except ValueError  as e :
    print("Invlalid Input , Please Enter the Number only....!", e )

except ZeroDivisionError :
    print("boss we can div anything by Zero ");
    
except  TypeError :
    print("Please enter the Both Numbers only....!");
    
except NameError :
    print("Please SOme variable are not Declared Please Check ")

finally:
    print("Program Excution Completed Thank you ")
