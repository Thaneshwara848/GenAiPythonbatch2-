class Student :
    
    def studentdetailes(self,name,age):
        self.name=name;
        self.age=age;
        print("My name is  :  ", self.name, "Age is  : ", self.age  )
        
    def printDetailes(self):
          print("Hiii",self.name )
          print("HI My AGe is : " , self.age )


s1 = Student();
#s1.studentdetailes("Rahul",21);           #My name id Rahul 
s1.printDetailes();