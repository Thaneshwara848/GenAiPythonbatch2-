#           LIST                        SET

#           Allow dup                   not allow the dup 
#           index                       no index 
#           order ? user order          no order : mixed order 
#           easy for search             diff to searh 
#           diff to add/ remove         easy to add / remove 
#           Mutable           

#           LIST                         Tuple       

#           Mutable(can be modify)       Im Mutable(we can not modify )
#           add / remove / update : yes   no it will not ? 
#           allow dup ? yes                 yes 
#              order  ? yes user order      yes user order 
#           index                               index 

fruits= ["Apple","Banana","Mango"];
print(fruits);
print(fruits[1]);       # access 
fruits[1]="Orange";        # insted of banana we updated to orange : yes we can modify 
print(fruits);
fruits.append("Graps"); 
print(fruits);
fruits.remove("Mango");
print(fruits);
print("===========================================")
names=("Anusha","Bharath","Charan");
print(names)
print(names[1]);       # yes access (index based );
names[1]="Bindu";      # im trying to Modify : can we modify ? 
print(names) 
