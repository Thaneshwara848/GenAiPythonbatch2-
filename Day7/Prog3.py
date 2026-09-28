shopping_list = []  # this is EMpty list , Dup : yes 
while True:
    print("\n===== SHOPPING LIST MENU =====")
    print("1. Add Item")
    print("2. View Items")
    print("3. Update Item")
    print("4. Remove Item")
    print("5. Search Item")
    print("6. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        item = input("Enter item name: ")
        shopping_list.append(item)
        print(item, "added successfully.")
    elif choice == "2":
        if len(shopping_list) == 0:
            print("Shopping list is empty.")
        else:
            print("\nShopping Items:")
            for index, item in enumerate(shopping_list, start=1):
               print(index, ".", item)
    elif choice == "3":
        if len(shopping_list) == 0:
            print("Shopping list is empty.")
        else:
            for index, item in enumerate(shopping_list, start=1):
                print(index, ".", item)
                number = int(input("Enter item number to update: "))
            if 1 <= number <= len(shopping_list):
                new_item = input("Enter new item name: ")
                shopping_list[number - 1] = new_item
                print("Item updated successfully.")
            else:
                print("Invalid item number.")
    elif choice == "4":
            item = input("Enter item name to remove: ")
            if item in shopping_list:
                shopping_list.remove(item)
                print(item, "removed successfully.")
            else:
                print("Item not found.")
    elif choice == "5":
        item = input("Enter item name to search: ")
        if item in shopping_list:
            print(item, "is available in the list.")
        else:
            print(item, "is not available.")
    elif choice == "6":
        print("Thank you!")
        break
    else:
        print("Invalid choice. Please try again.")