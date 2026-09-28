numbers =[10,20,30,40,10];
print(numbers)

numbers.append(50);
print(numbers) ;
numbers.insert(1,15);
print(numbers);


numbers.extend([55,65]);
print(numbers)

print("index(50) : " , numbers.index(50));
print("count(10) : ", numbers.count(10));

numbers.remove(55);
print(numbers);

numbers.sort();  # bubble , selection , merge , quick , ? 
print(numbers);

numbers.reverse();
print(numbers);

print("Max : " , max(numbers));
print("Max : " , min(numbers));
print("SUm : " , sum(numbers));
numbers.clear()
print(numbers)