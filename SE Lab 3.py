import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

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


def user_signup():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    cursor.execute(
        'INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    print("User registered successfully.")


def user_login():
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        cursor.execute(
            'SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user_id = cursor.fetchone()
        if user_id:
            print("User login successful.")
            return user_id[0]
        else:
            print("Invalid user credentials. Access denied.")
            print("1. Sign up")
            print("2. Try again")
            print("3. Exit")
            choice = input("Enter your choice: ")
            if choice == "1":
                user_signup()
            elif choice == "2":
                continue
            else:
                break


def view_all_users():
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    if users:
        print("All Registered Users are:")
        for user in users:
            print(f"User ID: {user[0]}, {user[1]}")
    else:
        print("No users are registered yet.")


def get_all_available_books():
    cursor.execute(
        'SELECT id, title, author, edition, available_stock FROM books')
    books = cursor.fetchall()
    if books:
        print("All Books avaialble in the Library are:")
        for book in books:
            print(
                f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Edition: {book[3]}, Available Stock: {book[4]}")
    else:
        print("There are no books available in the library right now.")


def add_book_to_database(title, author, edition, stock):
    cursor.execute('INSERT INTO books (title, author, edition, available, available_stock, total_stock) VALUES (?, ?, ?, ?, ?, ?)',
                   (title, author, edition, stock, stock, stock))
    conn.commit()
    print(f"{stock} copies of the book added to the library.")


def delete_book(title, edition):
    cursor.execute(
        'SELECT available_stock FROM books WHERE title = ? AND edition = ?', (title, edition))
    available_stock = cursor.fetchone()

    if not available_stock:
        print(
            f"The book '{title}' (Edition: {edition}) is not available in stock. You can't delete it.")
    elif available_stock[0] > 0:
        print(
            f"The book '{title}' (Edition: {edition}) is available in stock.")
        num_copies_to_delete = int(
            input("Enter the number of copies to delete: "))
        if num_copies_to_delete <= available_stock[0]:
            new_stock = available_stock[0] - num_copies_to_delete
            if new_stock == 0:
                cursor.execute(
                    'DELETE FROM books WHERE title = ? AND edition = ?', (title, edition))
                print(
                    f"All copies of the book '{title}' (Edition: {edition}) have been deleted from the library.")
            else:
                cursor.execute(
                    'UPDATE books SET available_stock = ? WHERE title = ? AND edition = ?', (new_stock, title, edition))
                print(
                    f"{num_copies_to_delete} copies of the book '{title}' (Edition: {edition}) deleted from the library.")
            conn.commit()
            get_all_available_books()
        else:
            print("The number of copies to delete is greater than available stock.")
    else:
        print("You can't delete anything as there is nothing available at the moment.")


def borrow_book(user_id):
    get_all_available_books()
    book_title = input("Enter the title of the book you want to borrow: ")
    book_edition = input("Enter the edition of the book you want to borrow: ")

    cursor.execute(
        'SELECT id, available_stock FROM books WHERE title = ? AND edition = ?', (book_title, book_edition))
    book_info = cursor.fetchone()

    if book_info and book_info[1] > 0:
        book_id = book_info[0]

        cursor.execute(
            'SELECT COUNT(*) FROM borrow_history WHERE user_id = ? AND book_id = ?', (user_id, book_id))
        user_borrowed_count = cursor.fetchone()[0]

        max_borrow_limit = 1

        if user_borrowed_count < max_borrow_limit:
            cursor.execute(
                'UPDATE books SET available_stock = available_stock - 1 WHERE id = ?', (book_id,))
            cursor.execute('INSERT INTO borrow_history (user_id, book_id, borrow_date) VALUES (?, ?, CURRENT_DATE)',
                           (user_id, book_id))
            cursor.execute('INSERT INTO admin_history (user_id, book_id, borrow_date) VALUES (?, ?, CURRENT_DATE)',
                           (user_id, book_id))
            conn.commit()
            print("Book borrowed successfully.")
        else:
            print(
                f"You've reached the limit for borrowing the book '{book_title}' (Edition: {book_edition}).")
    else:
        print(
            f"The book '{book_title}' (Edition: {book_edition}) is not available for borrowing.")


def return_book(user_id):
    cursor.execute('''
    SELECT bh.id, b.title, b.edition
    FROM borrow_history bh
    LEFT JOIN books b ON bh.book_id = b.id
    WHERE bh.user_id = ? AND bh.return_date IS NULL
    ''', (user_id,))

    borrowed_books = cursor.fetchall()

    if borrowed_books:
        print("Books you have borrowed and can return are:")
        for record in borrowed_books:
            borrow_id, title, edition = record
            print(f"Book ID: {borrow_id}, Title: {title}, Edition: {edition}")

        book_title = input("Enter the title of the book you want to return: ")
        book_edition = input(
            "Enter the edition of the book you want to return: ")

        for borrow_id, title, edition in borrowed_books:
            if book_title == title and book_edition == edition:
                cursor.execute(
                    'UPDATE borrow_history SET return_date = CURRENT_DATE WHERE id = ?', (borrow_id,))
                cursor.execute(
                    'UPDATE books SET available_stock = available_stock + 1 WHERE title = ? AND edition = ?', (book_title, book_edition))
                cursor.execute(
                    'UPDATE admin_history SET return_date = CURRENT_DATE WHERE user_id = ? AND book_id = ? AND return_date IS NULL', (user_id, borrow_id))
                conn.commit()
                print("Book returned successfully.")
                return

        print("You can't return this book as it was not borrowed or has already been returned.")
    else:
        print("You have not borrowed any books that can be returned.")


def Loged_in_user_borrow_history(user_id):
    cursor.execute('''
    SELECT b.title, b.edition
    FROM borrow_history bh
    JOIN books b ON bh.book_id = b.id
    WHERE bh.user_id = ?
    ''', (user_id,))
    borrow_history = cursor.fetchall()

    if borrow_history:
        print("Till now you have borrowed all of these books:")
        for record in borrow_history:
            title, edition = record
            print(
                f"Book Title: {title}, Book Edition: {edition if edition else 'Not specified'}")
    else:
        print("You have not borrowed any books.")


def admin_view_current_borrow_history():
    cursor.execute('''
    SELECT u.username, b.title, b.edition
    FROM borrow_history bh
    JOIN users u ON bh.user_id = u.id
    JOIN books b ON bh.book_id = b.id
    WHERE bh.return_date IS NULL
    ''')
    current_borrow_history = cursor.fetchall()

    if current_borrow_history:
        print("All the books borrowed by the users are: ")
        for record in current_borrow_history:
            username, title, edition = record
            print(
                f"Username: {username}, Book Title: {title}, Book Edition: {edition if edition else 'Not specified'}")
    else:
        print("No one has borrowed any book yet.")


def user_menu(user_id):
    while True:
        print("User Menu:")
        print("1. Borrow a book")
        print("2. Return a book")
        print("3. View your borrowing history")
        print("4. Exit user mode")
        choice = input("Enter your choice: ")

        if choice == "1":
            borrow_book(user_id)
        elif choice == "2":
            Loged_in_user_borrow_history(user_id)
            return_book(user_id)
        elif choice == "3":
            Loged_in_user_borrow_history(user_id)
        elif choice == "4":
            break


def admin_mode():
    if not admin_login():
        return

    while True:
        print("Admin Menu:")
        print("1. Add a book")
        print("2. Delete a book")
        print("3. View all book details")
        print("4. View borrow history")
        print("5. View all users")
        print("6. Exit admin mode")
        choice = input("Enter your choice: ")

        if choice == "1":
            book_title = input("Enter book title: ")
            book_author = input("Enter book author: ")
            book_edition = input("Enter book edition: ")
            stock = int(
                input("Enter the number of copies you want to addd in the stock: "))
            add_book_to_database(book_title, book_author, book_edition, stock)
        elif choice == "2":
            cursor.execute(
                'SELECT COUNT(*) FROM books WHERE available_stock > 0')
            available_books_count = cursor.fetchone()[0]

            if available_books_count == 0:
                print("There are no books available right now. Nothing to delete.")
            else:
                get_all_available_books()
                book_title = input(
                    "Enter the title of the book you want to delete: ")
                book_edition = input(
                    "Enter the edition of the book you want to delete: ")
                delete_book(book_title, book_edition)
        elif choice == "3":
            get_all_available_books()
        elif choice == "4":
            admin_view_current_borrow_history()
        elif choice == "5":
            view_all_users()
        elif choice == "6":
            break


def user_mode():
    print("Select an option:")
    print("1. Sign up")
    print("2. Login")
    print("3. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        user_signup()
        login_choice = input(
            "Sign up successful. Do you want to log in? (yes/no): ")
        if login_choice.lower() == "yes":
            user_id = user_login()
            if user_id:
                user_menu(user_id)
    elif choice == "2":
        user_id = user_login()
        if user_id:
            user_menu(user_id)
    elif choice == "3":
        quit


while True:
    print("Select Mode:")
    print("1. Admin Mode")
    print("2. User Mode")
    print("3. Exit")
    mode_choice = input("Enter your choice: ")

    if mode_choice == "1":
        admin_mode()
    elif mode_choice == "2":
        user_mode()
    elif mode_choice == "3":
        break

conn.close()
