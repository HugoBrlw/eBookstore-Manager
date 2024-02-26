"""
A simple program designed to add, update, search or delete books in a database
"""



#--- Imports ---#

import sqlite3

#--- Database creation ---#

db = sqlite3.connect('data/ebookstore_db.db')

cursor = db.cursor()

# Check if the 'book' table already exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='book'")
if not cursor.fetchone():
    # Create the table and insert initial data only if it doesn't exist
    # Added autoincrement to ID to avoid duplicate or admin errors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (ID INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT,
        author TEXT, qty INTEGER)
        ''')

    db.commit()

    library = [(3001, 'A Tale of Two Cities', 'Charles Dickens', 30),
    (3002, "Harry Potter and the Philosopher's Stone", 'J.K. Rowling', 40),
    (3003, "The Lion, the Witch and the Wardrobe", "C.S. Lewis", 25),
    (3004, "The Lord of the Rings", "J.R.R Tolkien", 37),
    (3005, "Alice in Wonderland", "Lewis Carroll", 12)]

    cursor.executemany('''INSERT INTO book (ID, title, author, qty) VALUES (?, ?, ?, ?)''', library)

    db.commit()

#--- 1. Enter book ---#

def enter_book():
    print("\nYou have selected the option to add a new book to the library.")
    new_title = input("Please insert the new book's title: ")
    new_author = input(f"Please insert the author of {new_title}: ")
    while True:
        try:
            new_qty = input(f"Please insert how many copies there are of {new_title}: ")
            break
        except ValueError:
            print("Invalid input. Please use numeric values.")
    print("The book's ID has been added automatically! Please use UPDATE BOOK to manually change it!")
    print("Book added successfully!")

    cursor.execute('''INSERT INTO book (title, author, qty) VALUES (?, ?, ?)''', (new_title, new_author, new_qty))
    
    db.commit()

#--- 2. Update book ---#

def update_book():
    print("\nYou have selected the option to update a book.")

    # Find the book to update
    book = search_book_id()
    if not book:
        return  # Exit if book not found

    # Get the fields to update from the user
    fields_to_update = []
    while True:
        field = input("Enter the field you want to update (title, author, quantity, ID, or 'done'): ").lower()
        if field == "done":
            menu()
        elif field in ("title", "author", "quantity", "id"):
            fields_to_update.append(field)
            break
        else:
            print("Invalid field. Please choose from title, author, quantity, or ID.")

    # Get the updated information for each selected field
    new_values = {}
    for field in fields_to_update:
        if field == "title":
            new_title = input(f"Enter the new title for '{book[1]}' (leave blank to keep current): ") or book[1]
            new_values["title"] = new_title

        elif field == "author":
            new_author = input(f"Enter the new author for '{book[1]}' (leave blank to keep current): ") or book[2]
            new_values["author"] = new_author

        elif field == "id":
            while True:
                try:
                    new_id = int(input(f"Enter the new ID for '{book[1]}' (leave blank to keep current): "))
                    cursor.execute("SELECT ID FROM book WHERE ID=?", (new_id,))
                    if cursor.fetchone():  # Check if the ID already exists
                        print("ID already exists. Please choose a unique ID.")
                    else:
                        break
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the ID.")
            new_values["ID"] = new_id  

        elif field == "quantity":
            while True:
                try:
                    new_qty = int(input(f"Enter the new quantity for '{book[1]}' (leave blank to keep current): "))
                    if new_qty < 0:
                        raise ValueError("Quantity cannot be negative.")
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid integer for the quantity.")
            new_values["qty"] = new_qty


    # Confirm changes
    confirmation = input(f"Are you sure you want to update '{book[1]}' with the following changes:\n"
                         + "\n".join([f"   - {field}: {new_values[field]}" for field in new_values])
                         + f"\n(y/n): ")
    if confirmation.lower() == 'y':
        # Update the book in the database
        query = "UPDATE book SET " + ", ".join([f"{field}=?" for field in new_values]) + " WHERE ID=?"
        values = tuple(new_values.values()) + (book[0],)  # Add the original ID as the last value
        cursor.execute(query, values)
        db.commit()
        print("Book updated successfully!")
    else:
        print("Update canceled.")


#--- 3. Delete book ---#

def delete_book():
    print("\nYou have selected the option to delete a book from the library."
    "\nDue to the sensitive nature of deleting a book, please provide the book ID.")

    # Find the book to delete
    book = search_book_id()
    if not book:
        return # Exit if book not found

    # Confirm deletion
    confirmation = input(f"Are you sure you want to delete '{book[1]}'? (y/n): ")
    if confirmation.lower() == 'y':
        book_id = book[0]  # Extract the ID explicitly
        cursor.execute("DELETE FROM book WHERE ID=?", (book_id,))  # Pass the ID as a tuple
        db.commit()  # Commit the changes to the database
        print("Book deleted successfully!")
    else:
        print("Deletion canceled.")


#--- 4. Search book ---#

# Separate search functions

# Search by ID, made specifically for the delete_book and update_book functions
def search_book_id():
    print("\nAvailable books:")

    # Retrieve all book IDs and titles
    cursor.execute("SELECT ID, title FROM book")
    books = cursor.fetchall()

    for book in books:
        print(f"ID: {book[0]} - Title: {book[1]}")

    while True:
        try:
            book_id = int(input("\nEnter the book ID: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer for the book ID.")

    # Retrieve the book by ID and display all details
    cursor.execute("SELECT * FROM book WHERE ID=?", (book_id,))
    book = cursor.fetchone()

    if not book:
        print("Book not found.")
        return None
    else:
        print("\nBook details:")
        print(f"ID: {book[0]}")
        print(f"Title: {book[1]}")
        print(f"Author: {book[2]}")
        print(f"Quantity: {book[3]}")
        return book

# Search by title
def search_book_title():
    print("\nAvailable books:")

    # Retrieve all book IDs and titles
    cursor.execute("SELECT ID, title FROM book")
    books = cursor.fetchall()

    for book in books:
        print(f"ID: {book[0]} - Title: {book[1]}")

    while True:
        search_term = input("\nEnter a keyword to search in titles: ").lower()

        cursor.execute("SELECT * FROM book WHERE title LIKE ?", ("%" + search_term + "%",))
        books = cursor.fetchall()

        if not books:
            print("\nNo books found with the keyword '{}'.".format(search_term))
        else:
            print("\nMatching books:")
            for book in books:
                print(f"ID: {book[0]}")
                print(f"Title: {book[1]}")
                print(f"Author: {book[2]}")
                print(f"Quantity: {book[3]}\n")
            return None  # Return to the menu after displaying results

#--- User menu ---#

def menu():
    while True:
        menu = input('''\nSelect one of the following options:
        1 - Enter book
        2 - Update book
        3 - Delete book
        4 - Search book
        5 - Customer support details
        0 - Close program
        : ''')

        if menu in ['1', '2', '3', '4', '5', '0']:

            if menu == '1':
                enter_book()

            elif menu == '2':
                update_book()
            
            elif menu == '3':
                delete_book()

            elif menu == '4':
                print("\nYou have selected the option to search for a book.")
                while True:
                    search_option = input('''\nSelect one of the following search options:
            1 - Search by ID
            2 - Search by title
            3 - Go back to main menu
            : ''')
                    if search_option in ['1', '2', '3']:

                        if search_option == '1':
                            search_book_id()
                        
                        elif search_option == '2':
                            search_book_title()
                        
                        elif search_option == '3':
                            break
                
                    else:
                        print("\nYou have made entered an invalid input. Please try again.")

            elif menu == '5':
                print("\nPlease contact our helpdesk at 555-000-000 or help@program.com for support or to report an error!")

            elif menu == '0':
                print("\nGoodbye!")
                exit()
            
        else:
            print("\nYou have made entered an invalid input. Please try again.\n")


menu()