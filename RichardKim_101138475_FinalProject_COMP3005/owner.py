import constants
import psycopg2
from prettytable import PrettyTable

def edit_book(username):
    print("\nBook Editing Page")
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor()
        #check if book exists
        isbn_input = input("Enter isbn of the book you want to edit: ")
        try:
            cur.execute("select * from has_in_collection where isbn = %s and owner_username = %s", (isbn_input,username))
            conn.commit()
            book_flag = cur.fetchone()

            if book_flag is not None:
                #exist in collection
                try:
                    cur.execute("select * from book where isbn = %s", ([isbn_input]))
                    conn.commit()
                    book_retrieved = cur.fetchone()

                    new_title = book_retrieved[1]
                    new_author_name = book_retrieved[2]
                    new_genre = book_retrieved[3]
                    new_total_pages = book_retrieved[4]
                    new_price = book_retrieved[5]
                    new_percentage_to_publisher = book_retrieved[6]

                    print("\nEditing Book Info.\nYou can not change book's isbn or Publisher name.\nPLEASE FOLLOW THE INSTRUCTIONS PROMPTED WHEN INPUTING INFO.")

                    title_input = input("Would you like to change the title?\n0 for yes, 1 for no: ")
                    if title_input == '0':
                        new_title = input("Please enter new title\n(required field, max 60 characters): ")

                    author_input = input("Would you like to change the author name?\n0 for yes, 1 for no: ")
                    if author_input == '0':
                        new_author_name = input("Please enter new author name\n(required field, max 30 characters): ")
                    
                    genre_input = input("Would you like to change the genre?\n0 for yes, 1 for no: ")
                    if genre_input == '0':
                        new_genre = input("Please enter new genre\n(required field, max 20 characters): ")

                    page_input = input("Would you like to change the total pages?\n0 for yes, 1 for no: ")
                    if page_input == '0':
                        new_total_pages = input("Please enter new total pages\n(required field, max 5 digits): ")
                    
                    price_input = input("Would you like to change the price?\n0 for yes, 1 for no: ")
                    if price_input == '0':
                        new_price = input("Please enter new price\n(required field, max 8 digits, with 2 decimal places): ")

                    percentage_input = input("Would you like to change the percentage to publisher?\n0 for yes, 1 for no: ")
                    if percentage_input == '0':
                        new_percentage_to_publisher = input("Please enter new percentage to publisher\n(required field, max 5 digits, with two decimal places): ")

                    try:
                        cur.execute("update book set title = %s, author_name = %s, genre = %s, total_pages = %s, price = %s, percentage_to_publisher = %s where isbn = %s", (new_title, new_author_name, new_genre, new_total_pages, new_price, new_percentage_to_publisher, isbn_input))
                        conn.commit()
                        cur.close()
                        print("\nBook Information Update Complete!")
                    except Exception as update_err:
                        print("Could not run query (edit_book - updating book): ", update_err) 
                        conn.rollback()
                except Exception as qerr:
                    print("Could not run query (edit_book - gettin book info): ", qerr) 
                    conn.rollback()
            
            else:
                print("You do not have the book in your collection.\nUnable to edit, going back to owner front page")
 
        except Exception as qeueryerr:
            print("Could not run query (edit_book - searching if book already exist in collection): ", qeueryerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

def remove_book(username):
    print("\nBook Removing Page")
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor()
        #check if book exists
        isbn_input = input("Enter isbn of the book you want to decrease quantity or remove fully from your collection: ")
        try:
            cur.execute("select * from has_in_collection where isbn = %s and owner_username = %s", (isbn_input,username))
            conn.commit()
            book_flag = cur.fetchone()

            if book_flag is not None:
                #exist in collection already, just decrease quantity or delete book depending on the quantity entered
                quantity_input = input("How many would you like to remove? ")
                quantity_input = int(quantity_input)
                try:
                    #get quantity of the book in collection
                    cur.execute("select quantity from has_in_collection where owner_username = %s and isbn = %s", (username, isbn_input))
                    conn.commit()
                    quantity_flag = cur.fetchone()[0]

                    if quantity_flag <= quantity_input:
                        print("You have entered to remove either all or more than all of the books you currently have in your collection.")
                        check_flag = input("Enter 1 if you are sure to remove, 0 if not: ")
                        if check_flag =='1':
                            try:
                                #remove book itself
                                cur.execute("delete from has_in_collection where isbn = %s and owner_username = %s;", (isbn_input, username))
                                conn.commit()
                                cur.close()
                            except Exception as qerr:
                                print("Could not run query (remove_book - removing from collection): ", qerr) 
                                conn.rollback()
                              
                    else:
                        print("Decreasing quantity of the book")
                        try:
                            #decrease quantity
                            cur.execute("""
                            update has_in_collection
                            set
                            quantity = quantity - %s
                            where owner_username = %s and isbn = %s""", (quantity_input, username, isbn_input))
                            conn.commit()
                            cur.close()
                        except Exception as qerr:
                            print("Could not run query (remove_book - decreasing quantity): ", qerr) 
                            conn.rollback()

                except Exception as qerr:
                    print("Could not run query (remove_book - getting quantity): ", qerr) 
                    conn.rollback()
            
            else:
                print("You do not have the book in your collection.\nUnable to remove, going back to owner front page")
 
        except Exception as qeueryerr:
            print("Could not run query (remove_book - searching if book already exist in collection): ", qeueryerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#simply add the book (to book if it does not exist, then add to collection)
#just gotta check if isbn exists or not
def add_book(username):
    print("\nBook Adding Page")
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor()
        #check if book exists
        isbn_input = input("Enter isbn of the book you want to newly add or increase quantity to your collection: ")
        try:
            cur.execute("select * from has_in_collection where isbn = %s and owner_username = %s", (isbn_input,username))
            conn.commit()
            book_flag = cur.fetchone()

            if book_flag is not None:
                #exist in collection already, just increment quantity
                quantity_input = input("How many more would you like to add? ")
                quantity_input = int(quantity_input)
                try:
                    #increment quantity of the book
                    cur.execute("""
                    update has_in_collection
                    set
                    quantity = quantity + %s
                    where owner_username = %s and isbn = %s""", (quantity_input, username, isbn_input))
                    conn.commit()
                    cur.close()
                    print("Adding done!")
                except Exception as qerr:
                    print("Could not run query (add_book - updating quantity): ", qerr) 
                    conn.rollback()
            
            else:
                #does not exist in collection
                #see if book exist, if not create the book
                #then create collection relationship
                try:
                    quantity_input = input("How many would you like to add? ")
                    quantity_input = int(quantity_input)
                    cur.execute("select * from book where isbn = %s", ([isbn_input]))
                    conn.commit()
                    book_result = cur.fetchone()

                    if book_result is None:
                        print("\nBook does not exist in our database, enter book data.")
                        #create book in book database itself
                        title_input = input("Enter title of the book (required field, max 60 characters, if more than 60 characters are given, only first 60 will be taken): ")
                        if len(title_input) > 60:
                            title_input =title_input[0:60]

                        author_input = input("Enter author of the book (required field, max 30 characters, if more than 30 characters are given, only first 30 will be taken): ")
                        if len(author_input) > 30:
                            author_input =author_input[0:30]

                        genre_input = input("Enter genre of the book (required field, max 20 characters, if more than 20 characters are given, only first 20 will be taken): ")
                        if len(genre_input) > 20:
                            genre_input =genre_input[0:20]
                        
                        #assume user inserts right input for those three values
                        page_input = input("Enter total pages of the book (required field, integer, max 5 digits): ")
                        page_input = int(page_input)

                        price_input = input("Enter price of the book (required field, decimal, 8 digits max, two decimal places): ")
                        price_input = float(price_input)

                        percentage_to_publisher_input = input("Enter percentage given to publisher per sale of the book (required field, decimal, 5 digits max, two decimal places): ")
                        percentage_to_publisher_input = float(percentage_to_publisher_input)

                        publisher_input = input("Enter publisher of the book (required field, max 30 characters, if more than 30 characters are given, only first 30 will be taken): ")
                        if len(publisher_input) > 30:
                            publisher_input =publisher_input[0:30]

                        cur.execute("select * from publisher where publisher_name = %s", ([publisher_input]))
                        conn.commit()
                        publisher_flag = cur.fetchone()

                        if publisher_flag is None:
                            #publisher does not exist, tell user to add publisher
                            print("\nPublisher mentioned does not exist in the database, input information about the new publisher")
                            publisher_address = input("Enter address of the publisher (required field, max 60 characters, if more than 60 characters are given, only first 60 will be taken): ")
                            if len(publisher_address) > 60:
                                publisher_address =publisher_address[0:60]
                            publisher_email = input("Enter email of the publisher (required field, max 60 characters, if more than 60 characters are given, only first 60 will be taken): ")
                            if len(publisher_email) > 60:
                                publisher_email =publisher_email[0:60]
                            #assume user inputs right data
                            publisher_phone = input("Enter phone number of the publisher (required field, max 15 digits): ")
                            publisher_bank_account = input("Enter banking information of the publisher (required field, max 8 digits): ")
                            try:
                                #add publisher with info provided
                                cur.execute("insert into publisher values(%s, %s,%s, %s,%s)", (publisher_input, publisher_address, publisher_email, publisher_phone, publisher_bank_account))
                                conn.commit()
                            except Exception as querr:
                                print("Could not run query (add_book - adding new publisher): ", querr) 
                                conn.rollback()
                        #finally create new book
                        try:
                            cur.execute("insert into book values (%s, %s, %s, %s, %s, %s, %s)", (isbn_input, title_input, author_input, genre_input, page_input, price_input, percentage_to_publisher_input))
                            conn.commit()
                            #new relation to publisher
                            try:
                                cur.execute("insert into book_publisher values (%s, %s)", (isbn_input, publisher_input))
                                conn.commit()
                            except Exception as queerr:
                                print("Could not run query (add_book - adding new book_publisher): ", queerr) 
                                conn.rollback()
                        except Exception as queerr:
                            print("Could not run query (add_book - adding new book): ", queerr) 
                            conn.rollback()
                    #book created, publisher created if needed, those two linked
                    #finally add to collection
                    try:
                        cur.execute("insert into has_in_collection values (%s, %s, %s)", (username, isbn_input, quantity_input))
                        conn.commit()
                        cur.close()
                        print("Adding done!")
                    except Exception as queerr:
                        print("Could not run query (add_book - adding new has_in_collection): ", queerr) 
                        conn.rollback()
                except Exception as quererr:
                    print("Could not run query (add_book - query to see if book exist in db): ", quererr) 
                    conn.rollback()
        except Exception as qeueryerr:
            print("Could not run query (add_book - searching if book already exist in collection): ", qeueryerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#user can edit any profile information, or delete their account
def edit_info(username, name):
    print("\nProfile Edit / Delete Page")
    edit_input = input("Enter 0 if you want edit your information.\nEnter 1 to delete account\nEnter 2 to go back to owner front page: ")
    if edit_input=='0':
        #get current owner info (before edit)
        try:
            conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
            cur = conn.cursor() 
            #get owner using username and get owner's input
            try:
                cur.execute("select * from store_owner where owner_username = %s", ([username]))
                conn.commit()
                user_retrieved = cur.fetchone()

                new_password = user_retrieved[1]
                new_name = user_retrieved[2]
                new_bank_info = user_retrieved[3]
                new_warehouse_address = user_retrieved[4]

                print("\nEditing Information.\nYou can not change your username.")

                password_input = input("Would you like to change your password?\n0 for yes, 1 for no: ")
                if password_input == '0':
                    new_password = input("Please enter your password\n(required field, max 10 characters, if more than 10 characters are given, only first 10 will be taken): ")
                    if len(new_password) > 10:
                        new_password =new_password[0:10]

                name_input = input("Would you like to change your name?\n0 for yes, 1 for no: ")
                if name_input == '0':
                    new_name = input("Please enter your name\n(required field, max 30 characters, if more than 30 characters are given, only first 30 will be taken): ")
                    if len(new_name) > 30:
                        new_name =new_name[0:30]

                bank_input = input("Would you like to change your banking information?\n0 for yes, 1 for no: ")
                if bank_input == '0':
                    bank_flag = 0
                    #check if bank_input is 7 digits and only contains numbers 
                    while bank_flag == 0:
                        new_bank_info = input("Please enter your payment information\n(required field, 7 digit number to mimic bank account number): ")
                        if len(new_bank_info) == 7 and new_bank_info.isdecimal():
                            bank_flag = 1
                
                warehouse_input = input("Would you like to change your warehouse address?\n0 for yes, 1 for no: ")
                if warehouse_input == '0':
                    new_warehouse_address = input("Please enter your warehouse address\n(required field, max 60 characters, if more than 60 characters are given, only first 60 will be taken):")
                    if len(new_warehouse_address) > 60:
                        new_warehouse_address =new_warehouse_address[0:60]

                try:
                    cur.execute("update store_owner set password = %s, name = %s, owner_bank = %s, warehouse_address = %s where owner_username = %s", (new_password, new_name, new_bank_info, new_warehouse_address, username))
                    conn.commit()
                    cur.close()
                    print("\nAccount Information Update Complete!")
                except Exception as update_err:
                    print("Could not run query (edit_info - updating owner): ", update_err) 
                    conn.rollback()
            except Exception as qerr:
                print("Could not run query (edit_info - gettin owner info): ", qerr) 
                conn.rollback()
        except Exception as sqle:
            print("Exception : ", sqle)

    elif edit_input=='1':
        print("\nAre you sure you want to delete your account?")
        sure_input = input("Enter 0 again if you are sure: ")
        if sure_input == '0':
            try:
                conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
                cur = conn.cursor() 
                #delete account
                #has_in_collection and store_owner_publisher are on delete cascade, so do not worry about them
                try:
                    cur.execute("delete from store_owner where owner_username = %s", ([username]))
                    conn.commit()
                    cur.close()
                except Exception as derr:
                    print("Could not run query (edit_info - deleting owner): ", derr) 
                    conn.rollback()
            except Exception as sqle:
                print("Exception : ", sqle)

            print("\nDeleting account, good bye", name)
            return 0
        return 1
    elif edit_input=='2':
        return 1

def report(username):
    print("\nReport Page")
    print("\nEnter 0 to see sales per day, 1 to see sales per genre, 2 to see sales per author")
    report_input = input("Which report would you like to see: ")

    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        try:
            #create a view that shows all sales per book
            cur.execute("""
            create or replace view total_sales as
            select owner_order.order_id, store_order.ordered_date, book_ordered.quantity, book.*, to_char((book.price*(book.percentage_to_publisher/100)),'FM999999999.00') as send_to_pub
            from owner_order
            inner join store_order on store_order.order_id = owner_order.order_id
            inner join book_ordered on book_ordered.order_id = owner_order.order_id
            inner join book on book.isbn = book_ordered.isbn
            where owner_order.owner_username = %s""", ([username]))
            conn.commit()

            if report_input == '0':
                print("\nViewing Sales per Date\nInput two dates to view sales in between.")
                print("total_sale_per_date is sales per date including tax, but not including delivery fees (they are sent to delivery company right away")
                print("sent_to_publisher is the amount of money sent to publisher, calculated by percentage_to_publisher per book")
                print("profit is total sales - tax - sent_to_publisher")
                d1 = input("Input first date (the earlier one): ")
                d2 = input("Input second date (the later one): ")
                cur.execute("""select ordered_date, 
                to_char(sum(price*quantity*1.13),'FM999999999.00') as total_sale_per_date, 
                to_char(sum(price*quantity*0.13),'FM999999999.00') as tax, 
                to_char(sum(price*quantity*percentage_to_publisher/100),'FM999999999.00') as sent_to_publisher, 
                to_char(sum(price*quantity*1.13) - sum(price*quantity*percentage_to_publisher/100)  - sum(price*quantity*0.13),'FM999999999.00') as profit
                from total_sales
                where ordered_date >= date(%s) and ordered_date <= date(%s)
                group by ordered_date""", (d1, d2))

                col_names = [header[0] for header in cur.description]
                data_r = []
                for row in cur:
                    data_r.append(row)

                print("")

                t = PrettyTable(col_names)
                for row in data_r:
                    t.add_row(row)
                print(t)


            elif report_input == '1':
                print("\nViewing Sales per Genre\nInput two dates to view sales in between.")
                print("total_sale_per_date is sales per date including tax, but not including delivery fees (they are sent to delivery company right away")
                print("sent_to_publisher is the amount of money sent to publisher, calculated by percentage_to_publisher per book")
                print("profit is total sales - tax - sent_to_publisher")
                d1 = input("Input first date (the earlier one): ")
                d2 = input("Input second date (the later one): ")
                cur.execute("""select genre, 
                to_char(sum(price*quantity*1.13),'FM999999999.00') as total_sale_per_date, 
                to_char(sum(price*quantity*0.13),'FM999999999.00') as tax, 
                to_char(sum(price*quantity*percentage_to_publisher/100),'FM999999999.00') as sent_to_publisher, 
                to_char(sum(price*quantity*1.13) - sum(price*quantity*percentage_to_publisher/100)  - sum(price*quantity*0.13),'FM999999999.00') as profit
                from total_sales
                where ordered_date >= date(%s) and ordered_date <= date(%s)
                group by genre""", (d1, d2))

                col_names = [header[0] for header in cur.description]
                data_r = []
                for row in cur:
                    data_r.append(row)

                print("")
                t = PrettyTable(col_names)
                for row in data_r:
                    t.add_row(row)
                print(t)

            elif report_input == '2':
                print("\nViewing Sales per Author\nInput two dates to view sales in between.")
                print("total_sale_per_date is sales per date including tax, but not including delivery fees (they are sent to delivery company right away")
                print("sent_to_publisher is the amount of money sent to publisher, calculated by percentage_to_publisher per book")
                print("profit is total sales - tax - sent_to_publisher")
                d1 = input("Input first date (the earlier one): ")
                d2 = input("Input second date (the later one): ")
                cur.execute("""select author_name, 
                to_char(sum(price*quantity*1.13),'FM999999999.00') as total_sale_per_date, 
                to_char(sum(price*quantity*0.13),'FM999999999.00') as tax, 
                to_char(sum(price*quantity*percentage_to_publisher/100),'FM999999999.00') as sent_to_publisher, 
                to_char(sum(price*quantity*1.13) - sum(price*quantity*percentage_to_publisher/100)  - sum(price*quantity*0.13),'FM999999999.00') as profit
                from total_sales
                where ordered_date >= date(%s) and ordered_date <= date(%s)
                group by author_name""", (d1, d2))

                col_names = [header[0] for header in cur.description]
                data_r = []
                for row in cur:
                    data_r.append(row)
                    
                print("")
                
                t = PrettyTable(col_names)
                for row in data_r:
                    t.add_row(row)
                print(t)

            cur.close()

        except Exception as qerr:
            print("Could not run query (get_first_date_available): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#view books this owner has
def view_books_in_collection(username):
    print("\nViewing All Books in Collection")
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #view all books in collections
        try:
            cur.execute("""
            select book.*, has_in_collection.quantity from has_in_collection
            inner join book on book.isbn = has_in_collection.isbn
            where owner_username = %s;
            """, ([username]))
            conn.commit()

            book_result = cur.fetchall()

            print("")
            for row in book_result:
                build_string = "ISBN: " + str(row[0]) +", Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Total pages: " + str(row[4]) + ",  Price: $" + str(row[5])+ ",  Percentage to publisher: " + str(row[6]) + ",  Quantity: " + str(row[7])
                print(build_string)

            cur.close()
        except Exception as derr:
            print("Could not run query (view_books_in_collection): ", derr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#main program that allow owners to perform actions
def owner_mode(name, username):

    welcome_msg = "\nOwner Front Page\n\tHello " + name + """!
    Welcome back to Look Inna Book!

    What would you like to do?

    Enter:
        0 - add new books to your collection
        1 - remove books from your collection
        2 - edit books in your collection
        3 - view reports
        4 - edit account information (including warehouse information)
        5 - view books in your collection

    To logout and go back to the first welcome page, enter any other integers.
    """
    print(welcome_msg)
    while (1):
        mode = input("Enter in your choice: ")
        if mode == '0':
            add_book(username)
        elif mode == '1':
            remove_book(username)
        elif mode == '2':
            edit_book(username)
        elif mode == '3':
            report(username)
        elif mode == '4':
            delete_flag = edit_info(username, name)
            #if owner deleted this account, go back to main page
            if delete_flag == 0:
                break
        elif mode == '5':
            view_books_in_collection(username)
        else:
            break
        
        second_msg = """

    Owner Front page

    What would you like to do?

    Enter:
        0 - add new books to your collection
        1 - remove books from your collection
        2 - edit books in your collection
        3 - view reports
        4 - edit account information (including warehouse information)
        5 - view books in your collection

    To logout and go back to the first welcome page, enter any other integers.
        """
        print(second_msg)