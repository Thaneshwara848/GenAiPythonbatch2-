#[] : it is a LIST 
# dupliacte ?   Yes 
fruits = ["Apple", "Banana", "Mango","Banana"]
print(fruits);

fruits.append("Orange");
print("After append:", fruits)

fruits.insert(1, "Grapes")
print("After insert:", fruits)

fruits.extend(["Guava", "Papaya"])
print("After extend:", fruits)

fruits.remove("Apple");
print("After remove:", fruits);

fruits.pop();
print(fruits);

removed = fruits.pop(2)
print("Removed item:", removed)
print("Final list:", fruits);
print("=========================================")
while "Banana" in fruits:
    fruits.remove("Banana")

print(fruits)




