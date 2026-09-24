class Student :
    
    def __init__(self,name , age , course):
        #print("This is Constructor...!");
        self.name=name ;
        self.age = age;
        self.course =course;
       
    
    def display(self) :
        #print("Hi This is Method....!")
        print("Name : ", self.name)
        print("Age  : ", self.age )
        print("Course  :  " , self.course )

s1 = Student(name="Thanesh",age=30,course="Python"); 
s1.display();

#s1.display();
print("============")
s2 = Student(course="JAVA",age=40,name="Rahul");
s2.display();
#s2.display();

 