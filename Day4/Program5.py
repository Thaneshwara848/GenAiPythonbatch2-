def check_even_or_odd():
    for i in range(1,11):
        if i%2==0:
            print(i);

def printtables():
    for i in range(1,11):
        print( "2 ", "* ", i  , " = " , 2 * i);

check_even_or_odd();
print("====================")
printtables();


def add_number(a , b ):
   
    c = a + b ; 
    print("Sum of A +  B = " , c )

a=int(input("Enter A value "));
b=int(input("ENter B Val :"));

add_number(a,b);