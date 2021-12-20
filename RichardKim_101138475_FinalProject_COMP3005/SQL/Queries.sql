/*
This file does not actually get ran, this file just shows list of queries used in the program.
The individual queries were used within the python script when required.
Each query will have information on the purpose, and at which python function it was used (in which .py file as well)

Since I just listed all queries I used in my program (grouped by functions and files), you will find simliar/same queries multiple times.
*/



--LOGIN.PY

--get_users_name(username), login.py
--Query is used in get_users_name(username) to search for the user's actual name using username
select * 
from store_user 
where username = username;

--get_owners_name(username), login.py
--Query is used in get_owners_name(username) to search for the owner's actual name using username
select * 
from store_owner 
where owner_username = username;



--SIGNUP.PY

/*
add_owner(username_input, password_input, name_input, banking_input, warehouse_address), signup.py

Quries used in add_owner(username_input, password_input, name_input, banking_input, warehouse_address).
Main purpose is to insert new owner data.
*/
--Query is used to insert a new row in store_owner table.
insert into store_owner values (username_input, password_input, name_input, banking_input, warehouse_address);

--add_user(username_input, password_input, name_input, payment_info, shipping_address, billing_address), signup.py
--Query inserts a new user
insert into store_user values (username_input, password_input, name_input, payment_info_input, shipping_address_input, billing_address_input);



--GUEST.PY

/*
view_book(isbn_input), guest.py - most of the function is shared in user.py (and so the queries too)

Queries used in view_book(isbn_input). Main purpose is to find the specific book with the isbn given, and find books recommneded based on this current book user is viewing.
*/
--Query is used to search for the book with given isbn, inner joins book_publisher so we have access to publisher's name
select book.*, book_publisher.publisher_name 
from book 
inner join book_publisher on book_publisher.isbn = book.isbn
where book.isbn = isbn.input;
/*
Query is used to search for all the books with given author's name, without the book with the given isbn, returns the result after grouping by isbn
This query is used to create a list of books with the same author as the one user searched up for.
But then the current book the user did search up for is not included, since they are already in the page of the book.
*/
select * 
from book 
where author_name = author_input and isbn != isbn_input;
/*
Query is used to search for all the books with given genre, without the book with the given isbn, and the author name given, returns the result after grouping by isbn
This is used similarly as previous query, just recommending some more books in the same genre, but this time books with the same author will be removed as well.
Since it was just shown above.
*/
select * 
from book 
where genre = genre_input and isbn != isbn_input and author_name != author_input;

/*
search_books(search_type), guest.py - most of the function is shared in user.py (and so the queries too)

Queries used in search_books(search_type). Main purpose is to search for the book that matches the criteria.
search_books(search_type) function also includes dynamic build of query, which was made by combining the queries listed below.
*/
/*
Query searches for books that is similar to the title given.
Uses lower() to make the search case-INsensitive, uses '%' to search for titles that includes the input as a substirng, uses similarity() from pg_trgm extension to use trigrams to search for similar titles (incase of typos)
Then groups all the result by isbn to return.
*/
select * 
from book
where lower(title) like lower('%' + title_input + '%') 
    or lower(title) = lower(title_input) 
    or similarity(lower(title), lower(title_input)) > 0.4;
/*
Query searches for books that is similar to the author input.
Contains same features to query just above.
*/
select * 
from book 
where lower(author_name) like lower('%' + author_name + '%') 
    or lower(author_name) = lower(author_input) 
    or similarity(lower(author_name), lower(author_input)) > 0.4;
/*
Query searches for books that is similar to the isbn input.
Contains same features to query above.
*/
select * 
from book 
where isbn like isbn_input 
    or isbn = isbn_input 
    or similarity(isbn, isbn_input) > 0.4;
/*
Query searches for books that is similar to the genre input.
Contains same features to queries above.
*/
select * 
from book 
where lower(genre) like lower('%' + genre_input + '%') 
    or lower(genre) = lower(genre_input) 
    or similarity(lower(genre), lower(genre_input)) > 0.4;
/*
Query searches for books that has less or equal pages than page_input
*/
select * 
from book 
where total_pages <= page_input;
/*
Query searches for books that has greater or equal pages than page_input
Contains same features to query just above
*/
select * 
from book 
where total_pages >= page_input;



--USER.PY
/*
add_book_to_basket(isbn, username, quantity), user.py
this function's main purpose is to add selected book into current logged in user's basket
Query to retrieve the book from the user's basket if needed
*/
select * from book_in_user_basket where username = username_input and isbn = isbn_input;
--Query to update the quantity of the book inside user's basket
update book_in_user_basket
set
quantity = quantity + %s
where username = %s and isbn = %s;
--Query inserts a new row into book_in_user_basket with the data provided.
insert into book_in_basket values(username_input, isbn_input, quantity_input);

/*
view_book(isbn, username), guest.py - most of the function is shared in user.py (and so the queries too)

Queries used in view_book(isbn, username). Main purpose is to find the specific book with the isbn given, and find books recommneded based on this current book user is viewing.
*/
--Query is used to search for the book with given isbn, inner join publisher to have access to publisher name of the book
select book.*, book_publisher.publisher_name 
from book 
inner join book_publisher on book_publisher.isbn = book.isbn
where book.isbn = isbn_input;
/*
Query is used to search for all the books with given author's name, without the book with the given isbn, returns the result after grouping by isbn
This query is used to create a list of books with the same author as the one user searched up for.
But then the current book the user did search up for is not included, since they are already in the page of the book.
*/
select * 
from book 
where author_name = author_input and isbn != isbn_input;
/*
Query is used to search for all the books with given genre, without the book with the given isbn, and the author name given, returns the result after grouping by isbn
This is used similarly as previous query, just recommending some more books in the same genre, but this time books with the same author will be removed as well.
Since it was just shown above.
*/
select * 
from book 
where genre = genre_input and isbn != isbn_input and author_name != author_input;

/*
search_books(search_type), guest.py - most of the function is shared in user.py (and so the queries too)

Queries used in search_books(search_type). Main purpose is to search for the book that matches the criteria.
search_books(search_type) function also includes dynamic build of query, which was made by combining the queries listed below.
*/
/*
Query searches for books that is similar to the title given.
Uses lower() to make the search case-INsensitive, uses '%' to search for titles that includes the input as a substirng, uses similarity() from pg_trgm extension to use trigrams to search for similar titles (incase of typos)
Then groups all the result by isbn to return.
*/
select * 
from book
where lower(title) like lower('%' + title_input + '%') 
    or lower(title) = lower(title_input) 
    or similarity(lower(title), lower(title_input)) > 0.4;
/*
Query searches for books that is similar to the author input.
Contains same features to query just above.
*/
select * 
from book 
where lower(author_name) like lower('%' + author_name + '%') 
    or lower(author_name) = lower(author_input) 
    or similarity(lower(author_name), lower(author_input)) > 0.4;
/*
Query searches for books that is similar to the isbn input.
Contains same features to query above.
*/
select * 
from book 
where isbn like isbn_input 
    or isbn = isbn_input 
    or similarity(isbn, isbn_input) > 0.4;
/*
Query searches for books that is similar to the genre input.
Contains same features to queries above.
*/
select * 
from book 
where lower(genre) like lower('%' + genre_input + '%') 
    or lower(genre) = lower(genre_input) 
    or similarity(lower(genre), lower(genre_input)) > 0.4;
/*
Query searches for books that has less or equal pages than page_input
*/
select * 
from book 
where total_pages <= page_input;
/*
Query searches for books that has greater or equal pages than page_input
Contains same features to query just above
*/
select * 
from book 
where total_pages >= page_input;

--view_recommended_books(username), user.py
--This function's main purpose is to find books the user may like judging from their order history and recommending to the user

--Query finds the most occured author in among the books this user has ordered.
--Uses inner join to connect the tables, and uses aggregate mode to search for most occured author, uses order by to order the authors in terms of occurance
select mode() within group (order by author_name) 
from store_order 
inner join book_ordered on store_order.order_id = book_ordered.order_id 
inner join book on book_ordered.isbn = book.isbn 
inner join user_order on store_order.order_id = user_order.order_id
where user_order.username = username_input;

--Exact same query as above, but genre instead of author
select mode() within group (order by genre) 
from store_order 
inner join book_ordered on store_order.order_id = book_ordered.order_id 
inner join book on book_ordered.isbn = book.isbn 
inner join user_order on store_order.order_id = user_order.order_id
where user_order.username = username_input;

--Query searches for all the books written by the user's favorite author, without the ones the user has already ordered
--select all columns in row from left joins book, book_ordered, store_order and user_order to keep all books that were not ordered by the user in the final table.
--where the author name matches,
--use except to remove rows that were ordered by the user already
--use inner join this time, to remove the books that were not ordered by any user.
--select all columns from book where username matches the input
select book.* 
from book 
left join book_ordered on book_ordered.isbn = book.isbn 
left join store_order on store_order.order_id = book_ordered.order_id 
where book.author_name = most_common_author_input 
except 
select book.* 
from book 
inner join book_ordered on book_ordered.isbn = book.isbn 
inner join store_order on store_order.order_id = book_ordered.order_id 
inner join user_order on store_order.order_id = user_order.order_id
where user_order.username = username_input;

--Exact same query as above, but genre instead of author
select book.* 
from book 
left join book_ordered on book_ordered.isbn = book.isbn 
left join store_order on store_order.order_id = book_ordered.order_id 
where book.genre = genre_input 
except 
select book.* 
from book 
inner join book_ordered on book_ordered.isbn = book.isbn 
inner join store_order on store_order.order_id = book_ordered.order_id 
inner join user_order on store_order.order_id = user_order.order_id
where user_order.username = username_input;

--make_order(username, name, payment, shipping, billing, price, date, estimated_days_in_transit, estimated_delivery_date), user.py
--Main purpose of this function is to create an order based on information given, create new rows book_ordered as needed, then clean out basket for this user

--Query inserts a new row into store_order using values given
insert into store_order values(order_id_input, payment_info_input, price_input, shipping_address_input, billing_address_input, status_input, today_date, estimated_days_in_transit, estimated_delivery_date);

--Query inserts a new row into user_order using values given
insert into user_order values(username_input, order_id_input)

--Query returns all books in the user's basket
--uses inner join to join book_in_basket to basket to user_basket to ensure all books are selected (although all books should be naturally be fully related to basket)
--searches by using username
select book_in_user_basket.* 
from book_in_user_basket 
inner join book on book.isbn = book_in_user_basket.isbn 
where book_in_user_basket.username = %s;

--Query inserts a new row into book_ordered using values given
insert into book_ordered values(book_ordered_id_input, order_id_input, isbn_input);

--Query returns owner's username of the book selected
select owner_username
from has_in_collection
where isbn = %s;

--Query retrieves information on owner_order
select * 
from owner_order
where order_id = %s;

--Query inserts a new row into owner_order
insert into owner_order values(owner_input, order_id);

--Query calculates how many copies of this book was sold in last 30 days (last month)
--inner joins with store_order to get ordered_date, and inner join owner_order to get the copies sold by THIS OWNER
select sum(book_ordered.quantity) as month_total
from book_ordered
inner join store_order on store_order.order_id = book_ordered.order_id
inner join owner_order on store_order.order_id = owner_order.order_id
where 
book_ordered.isbn = %s 
and store_order.ordered_date <= date(%s) 
and store_order.ordered_date >= date(%s)-30;

--Query updates has_in_collection to set a new past_month_sale (does it after every order), and decrease the quantity of the book in the owner's collection
update has_in_collection 
set 
past_month_sale = %s,
quantity = quantity - %s
where isbn = %s;

--Query deletes rows in book_in_basket, if they are from this user's basket.
--Each user only has one basket, and it is given an unique id, and so book_in_basket rows are distinguishable into each user
delete from book_in_basket where basket_id = basket_id_input;

--order_page(username), user.py
--main purpose of this query is to show a page where user can see the order information before confirming order

--Query shows all the books in the user's basket
--book_in_user_basket is inner joined with  book to ensure all things in the basket are joined (although they should systematically already be so)
--inner join publisher of each book to get publisher name
--selects all columns of book
select book.*, book_in_user_basket.quantity, book_publisher.publisher_name
from book_in_user_basket 
inner join book on book.isbn = book_in_user_basket.isbn 
inner join book_publisher on book_publisher.isbn = book.isbn
where book_in_user_basket.username = %s;

--Query takes total price of all books in the user's basket
--This query is mostly similar to query just above, but just takes the sum of book.price as total instead of returning all selected, and no need to inner join publisher
select sum(book.price * book_in_user_basket.quantity) as total 
from book_in_user_basket 
inner join book on book.isbn = book_in_user_basket.isbn 
where book_in_user_basket.username = %s;

--Query simply selects user with the username given to get all user info. There should be only one since username is primary key.
select * 
from store_user where username = username_input;

--view_basket(username), user.py
--main purpose of this function is to show all books in the user's basket

--Query is similar to another query explained above, simply find all books the user holds in the basket
select book.*, book_in_user_basket.quantity, book_publisher.publisher_name
from book_in_user_basket 
inner join book on book.isbn = book_in_user_basket.isbn 
inner join book_publisher on book_publisher.isbn = book.isbn
where book_in_user_basket.username = %s;

--view_orders(username), user.py
--main purpose of this function is to show all orders in user's order history, and also show all books in each order

--Query simply selects user with the username given. There should be only one since username is primary key.
select * 
from store_order 
inner join user_order on user_order.order_id = store_order.order_id
where user_order.username = %s;

--Query searches for all books included in the order
--Uses inner join to join book_publisher and book_ordered, and uses unique id to search
select book.*, book_ordered.quantity, book_publisher.publisher_name
from book 
inner join book_ordered on book_ordered.isbn = book.isbn 
inner join book_publisher on book_publisher.isbn = book.isbn
where book_ordered.order_id = %s

--track_orders(), user.py
--main purpose of this function is to track orders down, and show its status using the unique order_id

--Query simply finds all store_order rows with matching order_id
select *
from store_order 
where order_id = order_id_input;

--edit_info(username, name), user.py
--main purpose of this function is to allow user to edit their account information, or delete their account

--Another repeated query to get user information, I really should have made my code more efficient but I did not really have enough time :(
select *
from store_user 
where username = username_input;

--Query to update all attributes of a user
--Program is built so that the attributes the user does not want to edit are just updated to what it was before, making no difference
--Specific user distinguished by username
--Uses 'set' to 'update'
update store_user 
set 
password = new_password, 
name = new_name, 
payment_info = new_payment_info, 
shipping_address = new_shipping_address, 
billing_address = new_billing_address 
where username = username_input;

--Query that simply deletes the user specified
--Rows in other tables that is on delete cascade to user.username will be deleted as well:book_in_user_basket, user_order, ect
delete from store_user where username = username_input;



--OWNER.PY

--edit_book(username), owner.py
--function that is very similar to the one from user.py, edits book's information instead

--query to get info on row in has_in_collection
select * from has_in_collection where isbn = %s and owner_username = %s;

--query to get all information of a book
select * from book where isbn = %s;

--query to update the book with info provided
update book 
set title = %s, author_name = %s, genre = %s, total_pages = %s, price = %s, percentage_to_publisher = %s 
where isbn = %s;

--remove_book(username), owner.py
--function that deletes books in collection partiall or fully, depending on the quantity given. no new technique used

--query to get info on row in has_in_collection
select * from has_in_collection where isbn = %s and owner_username = %s;

--query to get quantity on row in has_in_collection
select quantity from has_in_collection where owner_username = %s and isbn = %s;

--query to delete a row from has_in_collection
--this is when the owner removes all quantity of the book in their collection, 
--only one owner is allowed to sell one book at a time, so row in has_in_collection relation will be removed as well
--note the book is now free to be owned by any other owners
delete from has_in_collection where isbn = %s and owner_username = %s;

--query to update has_in_collection, this is when owner only wants to decrease the quantity, not fully removing it
update has_in_collection
set
quantity = quantity - %s
where owner_username = %s and isbn = %s;

--add_book(username), owner.py
--function to add books to collection (increment quantity or add completely new books - this may need to be followed by adding a new publisher)

--query to get has_in_collection
select * from has_in_collection where isbn = %s and owner_username = %s;

--query to update has_in_collection (increment quantity)
update has_in_collection
set
quantity = quantity + %s
where owner_username = %s and isbn = %s;

--query to get book info
select * from book where isbn = %s;

--query to get publisher info
select * from publisher where publisher_name = %s;

--query to create new publisher
insert into publisher values(%s, %s,%s, %s,%s);

--query to create new book
insert into book values (%s, %s, %s, %s, %s, %s, %s);

--query to relate the book with publisher
insert into book_publisher values (%s, %s);

--query to relate the book with owner by inserting it into has_in_collection
insert into has_in_collection values (%s, %s, %s);

--edit_info(username, name), owner.py
--function that is very similar to edit_info from user.py (copied and pasted then edited actually), just edits owner info

--query to get owner's information initially
select * from store_owner where owner_username = %s;

--query to update store_owner with info provided
update store_owner set password = %s, name = %s, owner_bank = %s, warehouse_address = %s, where owner_username = %s;

--delete the owner selected
--Rows in other tables that is on delete cascade to store_owner.owner_username will be deleted as well:owner_order, has_in_collection
delete from store_owner where owner_username = %s;

--report(username), owner.py
--function to generate reports on owner's sales

--query to create or replace the view
--this view contains all information regarded to this owner's sales, and is used as a basis for actual reports to be built on via aggregation
create or replace view total_sales as
select owner_order.order_id, store_order.ordered_date, book_ordered.quantity, book.*, to_char((book.price*(book.percentage_to_publisher/100)),'FM999999999.00') as send_to_pub
from owner_order
inner join store_order on store_order.order_id = owner_order.order_id
inner join book_ordered on book_ordered.order_id = owner_order.order_id
inner join book on book.isbn = book_ordered.isbn
where owner_order.owner_username = %s;

--query to show sales information per day
--based on view above, shows all sales made in between two dates input
--used to_chars() to format the data shown
select ordered_date, 
to_char(sum(price*quantity*1.13),'FM999999999.00') as total_sale_per_date, 
to_char(sum(price*quantity*0.13),'FM999999999.00') as tax, 
to_char(sum(price*quantity*percentage_to_publisher/100),'FM999999999.00') as sent_to_publisher, 
to_char(sum(price*quantity*1.13) - sum(price*quantity*percentage_to_publisher/100)  - sum(price*quantity*0.13),'FM999999999.00') as profit
from total_sales
where ordered_date >= date(%s) and ordered_date <= date(%s)
group by ordered_date;

--query to show sales information per genre,
--same as above, but just groups it by genre instead of date
select genre, 
to_char(sum(price*quantity*1.13),'FM999999999.00') as total_sale_per_date, 
to_char(sum(price*quantity*0.13),'FM999999999.00') as tax, 
to_char(sum(price*quantity*percentage_to_publisher/100),'FM999999999.00') as sent_to_publisher, 
to_char(sum(price*quantity*1.13) - sum(price*quantity*percentage_to_publisher/100)  - sum(price*quantity*0.13),'FM999999999.00') as profit
from total_sales
where ordered_date >= date(%s) and ordered_date <= date(%s)
group by genre;

--query to show sales information per author,
--same as above, but just groups it by author instead of genre
select author_name, 
to_char(sum(price*quantity*1.13),'FM999999999.00') as total_sale_per_date, 
to_char(sum(price*quantity*0.13),'FM999999999.00') as tax, 
to_char(sum(price*quantity*percentage_to_publisher/100),'FM999999999.00') as sent_to_publisher, 
to_char(sum(price*quantity*1.13) - sum(price*quantity*percentage_to_publisher/100)  - sum(price*quantity*0.13),'FM999999999.00') as profit
from total_sales
where ordered_date >= date(%s) and ordered_date <= date(%s)
group by author_name;

--view_books_in_collection(username), owner.py
--function to simply list all books in the owner's collection

--query to list all books in owner's collection, inner join with book to display book's information as well
select book.*, has_in_collection.quantity from has_in_collection
inner join book on book.isbn = has_in_collection.isbn
where owner_username = %s;