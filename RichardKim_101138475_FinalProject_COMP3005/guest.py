import constants
import psycopg2

"""
takes isbn from the search page, then shows a detailed looks of the specific book
"""
def view_book(isbn):
    print("\nViewing Book")

    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #run loginFunc()
        try:
            cur.execute("""
            select book.*, book_publisher.publisher_name 
            from book 
            inner join book_publisher on book_publisher.isbn = book.isbn
            where book.isbn = %s""", ([isbn]))

            book_result = cur.fetchone()

            print("\nISBN: " + str(book_result[0])+"\nTitle: " + str(book_result[1]) + "\nAuthor name: " + str(book_result[2]) + "\nGenre: " + str(book_result[3]) + "\nPublisher: " + str(book_result[7]) + "\nPages: " + str(book_result[4]) + "\nPrice: $" + str(book_result[5]))

            try:
                cur.execute("select * from book where author_name = %s and isbn != %s", (str(book_result[2]), isbn))

                same_author = cur.fetchall()

                try:
                    cur.execute("select * from book where genre = %s and isbn != %s and author_name != %s", (str(book_result[3]), isbn, str(book_result[2])))

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
                    
                    print("\nYou can navigate to the similar books suggested by entering their index.\nOr you can go back to the search page by entering 0")
                    index = input("Enter index to navigate or 0 to go back to search: ")
                    
                    if int(index) in range(1, counter):
                        isbn_selected = similar_books[int(index)][similar_books[int(index)].rfind(':')+2:]
                        view_book(isbn_selected)

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
def search_books(search_type):

    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #run loginFunc()
        try:
            #title
            if search_type == 0:
                print("\nSearching by Title")
                title = input("Input title you want to search.\nBooks with similar title, books with input as a substring of their title will be shown as well: ")
                cur.execute("select * from book where lower(title) like lower(%s) or lower(title) = lower(%s) or similarity(lower(title), lower(%s)) > 0.4", ('%'+title+'%', title, title))
            
            #author
            elif search_type == 1:
                print("\nSearching by Author")
                author = input("Input author you want to search.\nBooks with similar author names and books with input as a substring of their author will be shown as well: ")
                cur.execute("select * from book where lower(author_name) like lower(%s) or lower(author_name) = lower(%s) or similarity(lower(author_name), lower(%s)) > 0.4", ('%'+author+'%', author, author))

            #isbn
            elif search_type == 2:
                print("\nSearching by ISBN")
                isbn = input("Input isbn you want to search.\nBooks with similar isbn will be shown as well: ")
                cur.execute("select * from book where isbn like %s or isbn = %s or similarity(isbn, %s) > 0.4", (isbn, isbn, isbn))
            
            #genre
            elif search_type == 3:
                print("\nSearching by Genre")
                genre = input("Input one genre you want to search.\nBooks with similar genre, books with input as a substring of their genre will be shown as well: ")
                cur.execute("select * from book where lower(genre) like lower(%s) or lower(genre) = lower(%s) or similarity(lower(genre), lower(%s)) > 0.4", ('%'+genre+'%', genre, genre))
            
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
                
                if previous_input_flag == 0:
                    query = "select * from book"

                cur.execute(query)

            conn.commit()
            book_result = cur.fetchall()
            print("")
            counter = 1
            for row in book_result:
                build_string = "Index: " + str(counter) + ",  Title: " + str(row[1]) + ",  Author name: " + str(row[2]) + ",  Genre: " + str(row[3]) + ",  Price: $" + str(row[5])
                print(build_string)
                counter+=1
            
            browse_input = input("\nEnter the index of the book you would like to see in detail.\nIf you want to go search for another book, enter 0: ")
            
            #passing on isbn
            if int(browse_input) in range(1, counter):
                view_book(book_result[int(browse_input)-1][0])

            cur.close()

        except Exception as query_error:
            print("Could not search for books using query: ", query_error) 
            conn.rollback()

    except Exception as sqle:
        print("Exception : ", sqle)

#main program that allow guests to search book by various criteria they want
def guest_mode():
    welcome_msg = """
    Hello GUEST!
    Welcome to Look Inna Book!

    How would you like to search for a book?
    Enter:
        0 - by title
        1 - by author name
        2 - by ISBN
        3 - by genre
        4 - by pages
        5 - by multiple factors
    
    To go back to the first welcome page, enter any other integer.
    """
    print(welcome_msg)
    while (1):
        search_mode = input("Enter in your choice: ")
        if search_mode in ['0','1','2','3','4','5']:
            search_books(int(search_mode))
        else:
            break
        
        second_msg = """

    Searching for more books.
    Enter:
        0 - by title, 1 - by author name, 2 - by ISBN, 3 - by genre, 4 - by pages, 5 - by multiple factors
        To go back to the first welcome page, enter any other integer.
        """
        print(second_msg)