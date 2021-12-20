import constants
import psycopg2
import uuid
import random
import datetime

"""
Add the selected book to currnet logged in user's basket.
Book is selected via ISBN, then added to the basket entity.
"""
def add_book_to_basket(isbn, username, quantity):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        print("\nAdding Book to Basket")
        try:
            #check if this book exists in user's basket
            cur.execute("select * from book_in_user_basket where username = %s and isbn = %s", (username, isbn))
            conn.commit()
            flag = cur.fetchone()
            #exists already then increment
            if flag is not None:
                cur.execute("""
                update book_in_user_basket
                set
                quantity = quantity + %s
                where username = %s and isbn = %s""", (quantity, username, isbn))
            #did not exist, create
            else:
                cur.execute("insert into book_in_user_basket values(%s, %s, %s)", (username, isbn, quantity))

            conn.commit()
            print("Complete! Book added to Basket")
            cur.close()

        except Exception as insertErr:
            print("Could not run query (get_users_name - adding book_in_basket): ", insertErr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

"""
takes isbn from the search page, then shows a detailed looks of the specific book.
Also shows similar books as current book, and allows user to add current book to basket.
"""
def view_book(isbn, username):
    print("\nViewing Book")

    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #get book with matching isbn
        try:
            cur.execute("""
            select book.*, book_publisher.publisher_name 
            from book 
            inner join book_publisher on book_publisher.isbn = book.isbn
            where book.isbn = %s""", ([isbn]))
            conn.commit()

            book_result = cur.fetchone()

            print("\nISBN: " + str(book_result[0])+"\nTitle: " + str(book_result[1]) + "\nAuthor name: " + str(book_result[2]) + "\nGenre: " + str(book_result[3]) + "\nPublisher: " + str(book_result[7]) + "\nPages: " + str(book_result[4]) + "\nPrice: $" + str(book_result[5]))

            try:
                cur.execute("select * from book where author_name = %s and isbn != %s", (str(book_result[2]), isbn))
                conn.commit()

                same_author = cur.fetchall()

                try:
                    cur.execute("select * from book where genre = %s and isbn != %s and author_name != %s", (str(book_result[3]), isbn, str(book_result[2])))
                    conn.commit()

                    same_genre = cur.fetchall()
                    #build array of simliar books
                    similar_books = []
                    counter = 1
                    for row in same_author:
                        #keep max 5
                        if counter == 6:
                            break
                        build_string = "Index: " + str(counter) + ",  Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Price: $" + str(row[5]) + ", ISBN: " + str(row[0])
                        similar_books.append(build_string)
                        counter+=1

                    mid_point = counter
                    
                    for row in same_genre:
                        #keep max 5
                        if counter == mid_point+5:
                            break
                        build_string = "Index: " + str(counter) + ",  Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Price: $" + str(row[5]) + ", ISBN: " + str(row[0])
                        similar_books.append(build_string)
                        counter+=1

                    print("\nCheck out other books written by " + str(book_result[2]) +"!\n")
                    counter = 0
                    for elem in similar_books:
                        if counter == mid_point-1:
                            print("\nCheck out other books in same genre!\n")
                        print(elem)
                        counter += 1
                    
                    print("\nDo you want to add this book to your basket?")
                    add_basket = input("Enter 1 to add to your basket, 0 to not: ")
                    if add_basket=='1':
                        quantity = input("How many would you like to add? ")
                        quantity = int(quantity)
                        curr_book_isbn = str(book_result[0])
                        add_book_to_basket(curr_book_isbn, username, quantity)
                    
                    print("\nYou can navigate to the similar books suggested by entering their index.\n")
                    index = input("Enter index to navigate or input 0 to not navigate: ")

                    if int(index) in range(1, counter+1):
                        smiilar_book_isbn_selected = similar_books[int(index)-1][similar_books[int(index)-1].rfind(':')+2:]
                        view_book(smiilar_book_isbn_selected, username)

                    cur.close()

                except Exception as qu_error:
                    print("Could not search for books using query (same genre): ", qu_error) 
                    conn.rollback()

            except Exception as q_error:
                print("Could not search for books using query (same author): ", q_error) 
                conn.rollback()

        except Exception as query_error:
            print("Could not search for books using query: ", query_error) 
            conn.rollback()

    except Exception as sqle:
        print("Exception : ", sqle)

"""
Takes user input for wanted search criteria and value, then search the database for books with the input given
Books with 1) the exact same as input, 2) similar to input (using SIMILARITY), and/or 3) books that contains input as substring of their attribute will be shown
For pages, books with user can search for books with equal or more / or less pages.
For multi search, user can choose multiple criteria to search the book on.
"""
def search_books(search_type, username):

    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #run loginFunc()
        try:
            #title
            if search_type == 0:
                print("\nSearching by Title")
                title = input("Input title you want to search.\nBooks with similar title, books with input as a substring of their title will be shown as well: ")
                cur.execute("""
                select * from book 
                where lower(title) 
                like lower(%s) or lower(title) = lower(%s) or similarity(lower(title), lower(%s)) > 0.4""", ('%'+title+'%', title, title))
            
            #author
            elif search_type == 1:
                print("\nSearching by Author")
                author = input("Input author you want to search.\nBooks with similar author names and books with input as a substring of their author will be shown as well: ")
                cur.execute("""
                select * from book 
                where lower(author_name) 
                like lower(%s) or lower(author_name) = lower(%s) or similarity(lower(author_name), lower(%s)) > 0.4""", ('%'+author+'%', author, author))

            #isbn
            elif search_type == 2:
                print("\nSearching by ISBN")
                isbn = input("Input isbn you want to search.\nBooks with similar isbn will be shown as well: ")
                cur.execute("""
                select * from book 
                where isbn 
                like %s or isbn = %s or similarity(isbn, %s) > 0.4""", (isbn, isbn, isbn))
            
            #genre
            elif search_type == 3:
                print("\nSearching by Genre")
                genre = input("Input one genre you want to search.\nBooks with similar genre, books with input as a substring of their genre will be shown as well: ")
                cur.execute("""
                select * from book 
                where lower(genre) 
                like lower(%s) or lower(genre) = lower(%s) or similarity(lower(genre), lower(%s)) > 0.4""", ('%'+genre+'%', genre, genre))
            
            #pages
            elif search_type == 4:
                print("\nSearching by Pages")
                page = input("Input number of page to search for: ")
                geq = input("If you would like to search for books with greater or equal pages as your input, enter 0\nIf you would like to search for books with less or equal pages as your input, enter 1\nAny other values will be counted as 0: ")
                if geq == '1':
                    cur.execute("select * from book where total_pages <= %s", ([int(page)]))
                else:
                    cur.execute("select * from book where total_pages >= %s", ([int(page)]))

            #multi
            else:
                print("\nSearching by Multiple Criteria")
                print("Enter in the values you want to search for when it gets prompted, if you do not want to search with the criteria mentioned, just press enter to skip it.")
                multi_title = input("Title: ")
                multi_author = input("Author: ")
                multi_isbn = input("ISBN: ")
                multi_genre = input("Genre: ")
                multi_page_geq = input("Page to be greater than or equal to: ")
                multi_page_leq = input("Page to be less than or equal to: ")

                query ="select * from book where "
                #0 if no previous input -> no need to add 'and'
                #1 if there was preivous input -> add 'and'
                previous_input_flag = 0

                if multi_title!="":
                    query += "(lower(title) like lower('%"+ multi_title +"%') or lower(title) = lower('"+ multi_title +"') or similarity(lower(title), lower('"+ multi_title +"')) > 0.4) "
                    previous_input_flag = 1
                if multi_author!="":
                    if previous_input_flag == 1:
                        query += "and "
                    query += "(lower(author_name) like lower('%"+ multi_author +"%') or lower(author_name) = lower('"+ multi_author +"') or similarity(lower(author_name), lower('"+ multi_author +"')) > 0.4) "
                    previous_input_flag = 1
                if multi_isbn!="":
                    if previous_input_flag == 1:
                        query += "and "
                    query += "(isbn like '"+ multi_isbn +"' or isbn = '"+ multi_isbn +"' or similarity(isbn, '"+ multi_isbn +"') > 0.4) "
                    previous_input_flag = 1
                if multi_genre!="":
                    if previous_input_flag == 1:
                        query += "and "
                    query += "(lower(genre) like lower('%"+multi_genre+"%') or lower(genre) = lower('"+multi_genre+"') or similarity(lower(genre), lower('"+multi_genre+"')) > 0.4 "
                previous_input_flag = 1
                if multi_page_geq!="":
                    if previous_input_flag == 1:
                        query += "and "
                    query += "(total_pages >= "+ multi_page_geq +") "
                    previous_input_flag = 1
                if multi_page_leq!="":
                    if previous_input_flag == 1:
                        query += "and "
                    query += "(total_pages <= "+ multi_page_leq +") "

                cur.execute(query)

            conn.commit()
            book_result = cur.fetchall()
            print("")
            counter = 1
            for row in book_result:
                build_string = "Index: " + str(counter) + ",  Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Price: $" + str(row[5])
                print(build_string)
                counter+=1
            
            browse_input = input("\nEnter the index of the book you would like to see in detail, or enter 0 to go back to user front page.\nTo add the book into your basket, visit the book's page (see it in detail), then select option to add to basket.\nEnter your selection: ")

            #passing on isbn
            if int(browse_input) in range(1, counter):
                view_book(book_result[int(browse_input)-1][0], username)

            cur.close()

        except Exception as query_error:
            print("Could not search for books using query: ", query_error) 
            conn.rollback()

    except Exception as sqle:
        print("Exception : ", sqle)

#get list of all the books the user has already ordered, find the most occured author and genre.
#get maximum of 5 books with the most occured author, and max 5 books with most occured genre, and show it to the user.
#need to make sure books already ordered are not included
def view_recommended_books(username):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #first get most occured author, and most occured genre
        try:
            cur.execute("""
            select mode() 
            within group (order by author_name) 
            from store_order 
            inner join book_ordered on store_order.order_id = book_ordered.order_id 
            inner join book on book_ordered.isbn = book.isbn 
            inner join user_order on store_order.order_id = user_order.order_id 
            where user_order.username = %s""", ([username]))
            conn.commit()
            most_common_author = cur.fetchone()

            cur.execute("""
            select mode() 
            within group (order by genre) 
            from store_order 
            inner join book_ordered on store_order.order_id = book_ordered.order_id 
            inner join book on book_ordered.isbn = book.isbn 
            inner join user_order on store_order.order_id = user_order.order_id 
            where user_order.username = %s""", ([username]))
            conn.commit()
            most_common_genre = cur.fetchone()

            print("\nViewing Recommended books (based on your favorite author and genre")
            print("If you do not see any, it means you already have ordered all the books written by the author / in the genre")
            print("Your favorite author is: ", most_common_author[0], " and your favorite genre is: ", most_common_genre[0])

            print("\nHere are other books written by your favorite author: ")
            #get all books that was written by most_common_author, that was not ordered by this user
            cur.execute("""
            select book.* from book 
            left join book_ordered on book_ordered.isbn = book.isbn 
            left join store_order on store_order.order_id = book_ordered.order_id 
            where book.author_name = %s 
            except 
            select book.* from book 
            inner join book_ordered on book_ordered.isbn = book.isbn 
            inner join store_order on store_order.order_id = book_ordered.order_id 
            inner join user_order on store_order.order_id = user_order.order_id 
            where user_order.username = %s""", (most_common_author[0], username))
            conn.commit()
            com_author_books = cur.fetchall()

            #get all books are in the same genre (most_common_genre), that was not ordered by this user
            cur.execute("""
            select book.* from book 
            left join book_ordered on book_ordered.isbn = book.isbn 
            left join store_order on store_order.order_id = book_ordered.order_id 
            where book.genre = %s 
            except 
            select book.* from book 
            inner join book_ordered on book_ordered.isbn = book.isbn 
            inner join store_order on store_order.order_id = book_ordered.order_id 
            inner join user_order on store_order.order_id = user_order.order_id 
            where user_order.username = %s""", (most_common_genre[0], username))
            conn.commit()
            com_genre_books = cur.fetchall()

            #build array of recommended books
            recommended_books = []
            counter = 1
            for row in com_author_books:
                #keep max 5
                if counter == 6:
                    break
                build_string = "Index: " + str(counter) + ",  Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Price: $" + str(row[5]) + ", ISBN: " + str(row[0])
                recommended_books.append(build_string)
                counter+=1

            mid_point = counter
            
            for row in com_genre_books:
                #keep max 5
                if counter == mid_point+5:
                    break
                build_string = "Index: " + str(counter) + ",  Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Price: $" + str(row[5]) + ", ISBN: " + str(row[0])
                recommended_books.append(build_string)
                counter+=1
            
            counter = 0
            for elem in recommended_books:
                if counter == mid_point-1:
                    print("\nHere are other books in your favorite genre: ")
                print(elem)
                counter += 1
            
            print("\nYou can navigate to the recommended books by entering their index.\n")
            index = input("Enter index to navigate or input 0 to not navigate: ")

            if int(index) in range(1, counter+1):
                smiilar_book_isbn_selected = recommended_books[int(index)-1][recommended_books[int(index)-1].rfind(':')+2:]
                view_book(smiilar_book_isbn_selected, username)

            cur.close()

        except Exception as qerr:
            print("Could not run query (view_recommended_books): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)


"""
make order based on information given
by that, it means:
    1) take all books in currnet user's basket
    2) create a new order using information given
    3) create new book_ordered
    3) later gotta handle this from owner side as well
    4) remove all books in user's basket
"""
def make_order(username, name, payment, shipping, billing, price, date, estimated_days_in_transit, estimated_delivery_date):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        print("\nPlacing Order...")
        #create new store_order
        try:
            order_id = uuid.uuid4()
            status = "Preparing for Shipment."
            cur.execute("""
            insert into 
            store_order values(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (str(order_id), payment, price, shipping, billing, status, date, estimated_days_in_transit, str(estimated_delivery_date)))
            conn.commit()
            try:
                #insert new user_order
                cur.execute("insert into user_order values(%s, %s)", (username, str(order_id)))
                conn.commit()
                #get books from the basket
                try:
                    cur.execute("""
                    select book_in_user_basket.* 
                    from book_in_user_basket 
                    inner join book on book.isbn = book_in_user_basket.isbn 
                    where book_in_user_basket.username = %s""", ([username]))
                    book_result = cur.fetchall()
                    conn.commit()
                    #create new book_ordered
                    try:
                        for row in book_result:
                            cur.execute("insert into book_ordered values(%s, %s, %s)", (str(order_id), str(row[1]), int(row[2])))
                            conn.commit()
                            print("A Book Added to Order.")

                            try:
                                #handle owner side things here
                                #get owner_username of the book's  owner
                                cur.execute("""
                                select owner_username
                                from has_in_collection
                                where isbn = %s""", ([str(row[1])]))
                                conn.commit()
                                owner = cur.fetchone()[0]
                            except Exception as countErr:
                                print("Could not run query (make_order - finding owner of the book from collection): ", countErr) 
                                conn.rollback()

                            #per book added to the order, decrease quantity of the books from the owner's collection
                            try:
                                #create owner_order if it does not exist already
                                #check owner_order does not exist
                                cur.execute("""
                                select * 
                                from owner_order
                                where order_id = %s""", ([str(order_id)]))
                                conn.commit()
                                owner_order_flag = cur.fetchone()
                                #create relation if it did not exist before
                                if owner_order_flag is None:
                                    try:
                                        cur.execute("insert into owner_order values(%s, %s)", (str(owner), str(order_id)))
                                        conn.commit()
                                    
                                    except Exception as deleteErr:
                                        print("Could not run query (make_order - create owner_order for owner of book): ", deleteErr) 
                                        conn.rollback()

                            except Exception as deleteErr:
                                print("Could not run query (make_order - query to select owner): ", deleteErr) 
                                conn.rollback()
                            
                            #recalculate past month sale for this owner, and this book (so inside has_in_collection)
                            #get past month sale of this book
                            try:
                                cur.execute("""
                                select sum(book_ordered.quantity) as month_total
                                from book_ordered
                                inner join store_order on store_order.order_id = book_ordered.order_id
                                inner join owner_order on store_order.order_id = owner_order.order_id
                                where 
                                book_ordered.isbn = %s 
                                and store_order.ordered_date <= date(%s) 
                                and store_order.ordered_date >= date(%s)-30""", (str(row[1]), str(date), str(date)))
                                conn.commit()
                                past_month_sale = cur.fetchone()[0]
                                if past_month_sale is None:
                                    past_month_sale = 0;
                                past_month_sale = int(past_month_sale)
                            except Exception as countErr:
                                print("Could not run query (make_order - calculating past month sale): ", countErr) 
                                conn.rollback()

                            #update has_in_collection's past month sale
                            try:
                                cur.execute("""
                                update has_in_collection 
                                set 
                                past_month_sale = %s,
                                quantity = quantity - %s
                                where isbn = %s""", (past_month_sale, int(row[2]), str(row[1])))
                                conn.commit()

                            except Exception as countErr:
                                print("Could not run query (make_order - update past month sale and decrease quantity): ", countErr) 
                                conn.rollback()
 
                        #delete everything in user's basket
                        try:
                            cur.execute("delete from book_in_user_basket where username = %s", ([username]))
                            conn.commit()
                            print("Order Complete! Thank you ", name, "!")
                            print("Copy your Order ID onto another place: ", order_id, ".\nThis unique id can be used to track your order!\nYou can always review your order id by viewing your order history.")
                            cur.close()

                        except Exception as deleteErr:
                            print("Could not run query (make_order - deleting basket contents): ", deleteErr) 
                            conn.rollback()
                    except Exception as addErr:
                        print("Could not run query (make_order - inserting new book_ordereds): ", addErr) 
                        conn.rollback()
                except Exception as countErr:
                    print("Could not run query (make_order - getting total number of books that was in the basket): ", countErr) 
                    conn.rollback()
            except Exception as iErr:
                print("Could not run query (make_order - inserting new user_order): ", iErr) 
                conn.rollback()
        except Exception as qerr:
            print("Could not run query (make_order - creating order): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

"""
makes the order on the books currently in the user's basket
user's name = user_info[2]
payment info = user_info[3]
shipping address = user_info[4]
billing address = user_info[5]
"""
def order_page(username, date):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #get all books from user's basket
        try:
            cur.execute("""
            select book.*, book_in_user_basket.quantity, book_publisher.publisher_name
            from book_in_user_basket 
            inner join book on book.isbn = book_in_user_basket.isbn 
            inner join book_publisher on book_publisher.isbn = book.isbn
            where book_in_user_basket.username = %s""", ([username]))
            conn.commit()
            book_result = cur.fetchall()
            #get total price
            cur.execute("""
            select sum(book.price * book_in_user_basket.quantity) as total 
            from book_in_user_basket 
            inner join book on book.isbn = book_in_user_basket.isbn 
            where book_in_user_basket.username = %s""", ([username]))
            conn.commit()
            total_price = cur.fetchone()
            #get user info
            try:
                cur.execute("select * from store_user where username = %s", ([username]))
                conn.commit()
                user_info = cur.fetchone()

                print("\nOrder Page\nHere are the books currently in your basket:")
                price = float(total_price[0])
                for row in book_result:
                    build_string = "Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Publisher: " + str(row[8]) + ",  Pages: " + str(row[4])+ ",  Price: $" + str(row[5]) + ",  ISBN: " + str(row[0]) + ",  Quantity: " + str(row[7])
                    print(build_string)

                print("\nSubtotal: $", price)
                print("Delivery: $5")
                price = price+5
                tax = (price*0.13)
                print("Tax: $", "{:.2f}".format((tax)))
                price = price+tax
                #format price to be in 2 decimal places
                print("\nFinal Total: $", "{:.2f}".format((price)))

                #payment info
                print("\nHow would you like to pay?")
                print("Enter 0 - if you want to use the card in your account, ending with: ", user_info[3][-4:])
                print("Enter 1- if you would like to enter in new payment information")
                payment_selection = input("Enter in your choice: ")
                #take new payment info
                if payment_selection=="1":
                    payment_flag = 0
                    while payment_flag == 0:
                        new_payment_info = input("Please enter your new payment information\n(8 digit number to mimic credit card number): ")
                        if len(new_payment_info) == 8 and new_payment_info.isdecimal():
                            payment_flag = 1
                
                #shipping address
                print("\nWhere should we ship it to?")
                print("Enter 0 - if you want to use the shipping address in your account:\n", user_info[4])
                print("Enter 1- if you would like to enter in new shipping address")
                shipping_selection = input("Enter in your choice: ")
                #take new shipping address
                if shipping_selection=="1":
                    new_shipping_address = input("Please enter your new shipping address\n(max 60 characters, if more than 60 characters are given, only first 60 will be taken): ")
                    if len(new_shipping_address) > 60:
                        new_shipping_address = new_shipping_address[0:60]
                
                #biling address
                print("\nWhere should we send your bill to?")
                print("Enter 0 - if you want to use the billing address in your account:\n", user_info[5])
                print("Enter 1 - if you would like to use the new shipping address you just entered as the billing address.\nEnter 2 - if you would like to enter in new billing address.")
                billinging_selection = input("Enter in your choice: ")
                #billing address is same as shipping
                if billinging_selection=='1':
                    #if they didnt enter a new shipping address
                    if shipping_selection != '1':
                        print("You did not enter a new shipping address. Billing address already saved in your account will be used.")
                        new_billinging_address = user_info[5]
                    else:
                        new_billinging_address = new_shipping_address
                #take new billing address
                elif billinging_selection=="2":
                    new_billinging_address = input("Please enter your new billing address\n(max 60 characters, if more than 60 characters are given, only first 60 will be taken): ")
                    if len(new_billinging_address) > 60:
                        new_billinging_address =new_billinging_address[0:60]
                #generate random number to be estimated_days_in_transit
                estimated_days_in_transit = random.randint(1,9)
                #set todays date into datetime object
                year, month, day = map(int, date.split('-'))
                estimated_delivery_date = datetime.date(year,month,day)
                #add estimated_days_in_transit + 2 - estimated delivery date
                estimated_delivery_date = estimated_delivery_date + datetime.timedelta(days=estimated_days_in_transit+2)

                print("\nAll Information taken.\nThe estimated delivery date is: ", estimated_delivery_date,". \nEnter 0 to confirm order using information above.")
                final_input = input("Enter 1 to cancel order: ")
                #finalize informations then make the order
                if final_input=='0':
                    final_name = user_info[2]

                    final_payment_info = user_info[3]
                    if payment_selection=="1":
                        final_payment_info = new_payment_info

                    final_shipping_info= user_info[4]
                    if shipping_selection=="1":
                        final_shipping_info = new_shipping_address

                    final_billing_info= user_info[5]
                    if billinging_selection!="0":
                        final_billing_info = new_billinging_address
                        
                    make_order(username, final_name, final_payment_info, final_shipping_info, final_billing_info, price, date, estimated_days_in_transit, estimated_delivery_date)

                    cur.close()
                
            except Exception as queryerr:
                print("Could not run query (order_page - getting user info): ", queryerr) 
                conn.rollback()    
        except Exception as qerr:
            print("Could not run query (order_page - getting all the books in basket): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#list all the books currently in the user's basket
def view_basket(username, date):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #inner join book_in_user_basket, book on isbn, then select only the book informations.
        #shows all books in this user's basket
        try:
            cur.execute("""
            select book.*, book_in_user_basket.quantity, book_publisher.publisher_name
            from book_in_user_basket 
            inner join book on book.isbn = book_in_user_basket.isbn 
            inner join book_publisher on book_publisher.isbn = book.isbn
            where book_in_user_basket.username = %s""", ([username]))
            conn.commit()
            book_result = cur.fetchall()

            print("\nViewing Basket")
            print("Here are the books currently in your basket:")
            for row in book_result:
                build_string = "Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Publisher: " + str(row[8]) + ",  Pages: " + str(row[4])+ ",  Price: $" + str(row[5]) + ",  ISBN: " + str(row[0])+ ",  Quantity: " + str(row[7])
                print(build_string)
            
            order_input = input("\nEnter 0 if you would like to complete your order, \nenter 1 if you would like to go back to user front page: ")

            if order_input=='0':
                order_page(username, date)
            
            cur.close()

        except Exception as qerr:
            print("Could not run query (view_basket - getting all the books in basket): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#lists all orders made my the user, and shows order information in detail
def view_orders(username):
    try:
        print("\nOrder History of: ", username)
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #get all orders from this user
        try:
            cur.execute("""
            select * 
            from store_order 
            inner join user_order on user_order.order_id = store_order.order_id
            where user_order.username = %s""", ([username]))
            conn.commit()
            order_result = cur.fetchall()
                
            #get all books in the order per order
            try:
                #start printing
                for row in order_result:
                    #build string for order
                    build_string = "\n\nOrder ID: " + str(row[0]) + "\nOrdered On: " + str(row[6]) + "\nPayment Information: " + str(row[1]) + "\nTotal Price: $" + str(row[2]) + "\nSent to: " + str(row[3]) + "\nBill sent to: " + str(row[4]) + "\nCurrent Status: " + str(row[5]) + "\n"
                    #use status to see if order is delivered yet
                    if str(row[5]) == "Delivery Complete":
                        build_string += "Delivered on: " + str(row[8]) + "\n"
                    else:
                        build_string += "Estimated to be delivered on: " + str(row[8]) + "\n"
                        
                    #get all books in the order
                    cur.execute("""
                    select book.*, book_ordered.quantity, book_publisher.publisher_name
                    from book 
                    inner join book_ordered on book_ordered.isbn = book.isbn 
                    inner join book_publisher on book_publisher.isbn = book.isbn
                    where book_ordered.order_id = %s""", ([str(row[0])]))
                    conn.commit()
                    book_result = cur.fetchall()
                    #print order then books
                    print(build_string)
                    print("Books In the Order:")
                    for i in book_result:
                        print("\nISBN: " + str(i[0])+"\nTitle: " + str(i[1]) + "\nAuthor name: " + str(i[2]) + "\nGenre: " + str(i[3]) + "\nPublisher: " + str(i[8]) + "\nPages: " + str(i[4]) + "\nPrice: $" + str(i[5]) + "\nQuantity: " + str(i[7]))
                
                cur.close()
                print("\nEnd of Orders, going back to users front page.")

            except Exception as querr:
                print("Could not run query (view_orders - getting all books in each order): ", querr) 
                conn.rollback()
        except Exception as qerr:
            print("Could not run query (view_orders - getting all the orders): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#track orders using the orders id
def track_orders():
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #get user input for an unique id, then find the corresponding order
        try:
            print("\nOrder Tracking")

            track_flag = 0

            while track_flag == 0:
                uid = input("Input unique ID of the order you wish to track: ")
                cur.execute("select * from store_order where order_id = %s", ([uid]))
                conn.commit()
                track_result = cur.fetchone()

                if track_result is not None:
                    print("\nOrder ID: ", track_result[0], "\nOrdered On: ", track_result[6],"\nCurrent Stauts: ", track_result[5], "\nTotal Price: $", track_result[2], "\nBeing shipped to: ", track_result[3])
                    
                    if str(track_result[5]) == "Delivery Complete":
                        print("Delivered on: ", track_result[8])
                    else:
                        print("Estimated to be delivered on: ", track_result[8])

                    track_flag = 1
                
                else:
                    print("Can not find any order matchin the id.")
                    track_input = input("Enter 0 if you want to try again.\nEnter 1 to go back to user front page")

                    if track_input=='1':
                        track_flag = 1

            cur.close()

        except Exception as qerr:
            print("Could not run query (track_orders): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#user can edit any profile information, or delete their account
def edit_info(username, name):
    print("\nProfile Edit / Delete Page")
    edit_input = input("Enter 0 if you want edit your information.\nEnter 1 to delete account\nEnter 2 to go back to user front page: ")
    if edit_input=='0':
        #get current user info (before edit)
        try:
            conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
            cur = conn.cursor() 
            #get user using username and get user's input
            try:
                cur.execute("select * from store_user where username = %s", ([username]))
                conn.commit()
                user_retrieved = cur.fetchone()

                new_password = user_retrieved[1]
                new_name = user_retrieved[2]
                new_payment_info = user_retrieved[3]
                new_shipping_address = user_retrieved[4]
                new_billing_address = user_retrieved[5]

                print("\nEditing Information.\nYou can not change your username.")

                password_input = input("Would you like to change your password?\n0 for yes, 1 for no: ")
                if password_input == '0':
                    new_password = input("Please enter your password\n(max 10 characters, if more than 10 characters are given, only first 10 will be taken): ")
                    if len(new_password) > 10:
                        new_password =new_password[0:10]

                name_input = input("Would you like to change your name?\n0 for yes, 1 for no: ")
                if name_input == '0':
                    new_name = input("Please enter your name\n(max 30 characters, if more than 30 characters are given, only first 30 will be taken): ")
                    if len(new_name) > 30:
                        new_name =new_name[0:30]

                payment_input = input("Would you like to change your method of payment?\n0 for yes, 1 for no: ")
                if payment_input == '0':
                    payment_flag = 0
                    #check if payment_info is 8 digits and only contains numbers 
                    while payment_flag == 0:
                        new_payment_info = input("Please enter your payment information\n(8 digit number to mimic credit card number): ")
                        if len(new_payment_info) == 8 and new_payment_info.isdecimal():
                            payment_flag = 1
                
                shipping_input = input("Would you like to change your shipping address?\n0 for yes, 1 for no: ")
                if shipping_input == '0':
                    new_shipping_address = input("Please enter your shipping address\n(max 60 characters, if more than 60 characters are given, only first 60 will be taken):")
                    if len(new_shipping_address) > 60:
                        new_shipping_address =new_shipping_address[0:60]
                
                billing_input = input("Would you like to change your billing address?\n0 for yes, 1 for no: ")
                if billing_input == '0':
                    billing_address_same = input("Enter 0 if your billing address is the same as your NEW shipping address, 1 if not.\nIf you enter 0 when you did nont enter in a new shipping address, your new billing address will be same as your old shipping address.\nEnter input: ")
                    if billing_address_same == '1':
                        new_billing_address = input("Please enter your billing address\n(max 60 characters, if more than 60 characters are given, only first 60 will be taken):")
                        if len(new_billing_address) > 60:
                            new_billing_address =new_billing_address[0:60]
                    elif billing_address_same == '0':
                        new_billing_address = new_shipping_address

                try:
                    cur.execute("update store_user set password = %s, name = %s, payment_info = %s, shipping_address = %s, billing_address = %s where username = %s", (new_password, new_name, new_payment_info, new_shipping_address, new_billing_address, username))
                    conn.commit()
                    cur.close()
                    print("\nAccount Information Update Complete!")
                except Exception as update_err:
                    print("Could not run query (edit_info - updating user): ", update_err) 
                    conn.rollback()
            except Exception as qerr:
                print("Could not run query (edit_info - gettin user info): ", qerr) 
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
                #user_order and book_in_user_basket are on delete cascade, so do not worry about them
                try:
                    cur.execute("delete from store_user where username = %s", ([username]))
                    conn.commit()
                    cur.close()
                except Exception as derr:
                    print("Could not run query (edit_info - deleting user): ", derr) 
                    conn.rollback()
            except Exception as sqle:
                print("Exception : ", sqle)
            print("\nDeleting account, good bye", name)
            return 0
        return 1
    elif edit_input=='2':
        return 1

#find the most recent order's date
#user will not be able to set the date previous to this date
def get_first_date_available(username):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        try:
            #query to get most recent ordered date by the user
            cur.execute("""
            select ordered_date 
            from store_order 
            inner join user_order on store_order.order_id = user_order.order_id 
            where user_order.username = %s 
            order by ordered_date desc limit 1""", ([username]))
            conn.commit()
            date_retrieved = cur.fetchone()

            if date_retrieved is not None:
                date_retrieved = date_retrieved[0]

            cur.close()

            return date_retrieved

        except Exception as qerr:
            print("Could not run query (get_first_date_available): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#find all orders by this user, then change its status depending on the current day given
def set_order_status(username, date):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        try:
            #query to get all orders by the user
            cur.execute("""
            select * 
            from store_order 
            inner join user_order on user_order.order_id = store_order.order_id
            where user_order.username = %s""", ([username]))
            conn.commit()
            order_result = cur.fetchall()

            try:
                #for each order
                for row in order_result:
                    #row[0] - order.id
                    #row[5] - current_status
                    #row[6] - ordered-date
                    #row[7] - estimated_days_in_transit
                    #run function for each orders
                    cur.callproc('set_status', (str(row[6]),date,str(row[7]),str(row[0])))
                    conn.commit()

                cur.close()

            except Exception as querr:
                print("Could not run query (set_order_status - changing all order statuses): ", querr) 
                conn.rollback()
        except Exception as qerr:
            print("Could not run query (set_order_status - retrieving all orders by this user): ", qerr) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)


#main program that allow users to search book by various criteria they want
def user_mode(name, username):
    most_recent_order_date = get_first_date_available(username)
    
    if most_recent_order_date is not None:
        date_str = "\nWhat is the day today?\n Input in following format: YYYY-MM-DD. Once you make an order, you will not be able to set the date previous of the order.\nCurrently, the earliest date you may set into is " + str(most_recent_order_date)
    else:
        date_str = "\nWhat is the day today?\n Input in following format: YYYY-MM-DD. Once you make an order, you will not be able to set the date previous of the order.\nCurrently, the earliest date you may set into is any date"
    print(date_str)
    date_input = input("Input date here. MAKE SURE IT IS IN YYYY-MM-DD FORMAT: ")

    if most_recent_order_date is not None:
        #change all order's current_status for this date
        set_order_status(username, date_input)
    

    welcome_msg = "\nUser Front Page\n\tHello " + name + """!
    Welcome to Look Inna Book!

    Would you like to search for a book?
    Enter:
        0 - by title
        1 - by author name
        2 - by ISBN
        3 - by genre
        4 - by pages
        5 - by multiple factors

    Or take other actions?
    Enter:
        6 - view recommended books based on order history
        7 - view your order history
        8 - view your basket and confirm order
        9 - track your orders
        10 - edit your account information or delete account
        11 - change today's date


    To logout and go back to the first welcome page, enter any other integers.
    """
    print(welcome_msg)
    while (1):
        most_recent_order_date = get_first_date_available(username)
        mode = input("Enter in your choice: ")
        if mode in ['0','1','2','3','4','5']:
            search_books(int(mode), username)
        elif mode == '6':
            view_recommended_books(username)
        elif mode == '7':
            view_orders(username)
        elif mode == '8':
            view_basket(username, date_input)
        elif mode == '9':
            track_orders()
        elif mode == '10':
            delete_flag = edit_info(username, name)
            #if user deleted this account, go back to main page
            if delete_flag == 0:
                break
        elif mode == '11':
            if most_recent_order_date is not None:
                print("Input new date here. \nMAKE SURE IT IS IN YYYY-MM-DD FORMAT AND IS NOT BEFORE ", most_recent_order_date)
                date_input = input("Enter: ")
                #change all order's current_status for this date
                set_order_status(username, date_input)
            else:
                date_input = input("Input new date here. \nMAKE SURE IT IS IN YYYY-MM-DD FORMAT.\n Enter: ")
        else:
            print("Logging out, good bye ", name, "!")
            break
        
        second_msg = """

    User Front page

    Would you like to search for a book?
    Enter:
        0 - by title
        1 - by author name
        2 - by ISBN
        3 - by genre
        4 - by pages
        5 - by multiple factors

    Or take other actions?
    Enter:
        6 - view recommended books based on order history
        7 - view your order history
        8 - view your basket and confirm order
        9 - track your orders
        10 - edit your account information or delete account
        11 - change today's date

    To logout and go back to the first welcome page, enter any other integers.
        """
        print(second_msg)