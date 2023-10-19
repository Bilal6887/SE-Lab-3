import sqlite3

conn = sqlite3.connect('library.db')

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        edition TEXT
    )
''')

admin_username = "Library Staff"
admin_password = "Namal123"

def admin_login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    if username == admin_username and password == admin_password:
        print("Admin login successful.")
        return True
    else:
        print("Invalid admin credentials. Access denied.")
        return False

def add_book_to_database(title, author, edition):
    cursor.execute('INSERT INTO books (title, author, edition) VALUES (?, ?, ?)', (title, author, edition))
    conn.commit()
    print("Book added to the library.")

def delete_book_from_database(title, edition):
    cursor.execute('DELETE FROM books WHERE title = ? AND edition = ?', (title, edition))
    conn.commit()
    print("Book deleted from the library.")

def get_all_books():
    cursor.execute('SELECT title, author, edition FROM books')
    books = cursor.fetchall()
    if books:
        print("All Books in the Library:")
        for book in books:
            print(f"Title: {book[0]}, Author: {book[1]}, Edition: {book[2]}")
    else:
        print("There are no books available right now.")

while True:
    print("First of all, you have to login!")
    if admin_login():
        break

while True:
    print("Admin Menu:")
    print("1. Add a book")
    print("2. Delete a book")
    print("3. View all book details")
    print("4. Exit admin mode")
    choice = input("Enter your choice: ")

    if choice == "1":
        book_title = input("Enter book title: ")
        book_author = input("Enter book author: ")
        book_edition = input("Enter book edition: ")
        add_book_to_database(book_title, book_author, book_edition)
    elif choice == "2":
        book_title = input("Enter the title of the book to delete: ")
        book_edition = input("Enter the edition of the book to delete: ")
        delete_book_from_database(book_title, book_edition)
    elif choice == "3":
        get_all_books()
    elif choice == "4":
        break

conn.close()