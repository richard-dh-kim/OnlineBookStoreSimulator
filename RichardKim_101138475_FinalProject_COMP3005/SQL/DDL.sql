--This file gets called from the initializer.py when the program first starts

--Initializes the schema with name 'public'.

--Deletes all previous tables / data, recreates it, then restore the default grants
--Hoping this removes TA's efforts in having to manually do this
drop schema public cascade;
create schema public;
grant all on schema public to postgres;
grant all on schema public to public;

--enable pg_trgm extension to be used to search similar books
CREATE EXTENSION pg_trgm;

--create tables
--entity store user - ones who will order books
--all attributes are requried, and so must be not null
--assumed only username is unique
create table store_user
	(
		username varchar(10),
		password varchar(10) not null,
		name varchar(30) not null,
		payment_info varchar(8) not null,
		shipping_address varchar(60) not null,
		billing_address varchar(60) not null,
		primary key (username)
	);
--entity book
--all attributes are requried, and so must be not null
--assumed only isbn is unique
create table book
	(
		isbn varchar(13),
		title varchar(60) not null,
		author_name varchar(30) not null,
		genre varchar(20) not null,
		total_pages numeric(5,0) not null,
		price numeric(8,2) not null,
		percentage_to_publisher numeric(5,2) not null,
		primary key (isbn)
	);
--relation book_in_user_basket, it connects store_user and books.
--functions as a 'basket' entity for each user
--on delete cascade to book and store_user
--username, isbn used as primary key
create table book_in_user_basket
	(
		username varchar(10),
		isbn varchar(13),
		quantity numeric(9,0) not null,
		foreign key (isbn) references book
		on delete cascade,
		foreign key (username) references store_user
		on delete cascade,
		primary key(username, isbn)
	);
--entity store_order, for each order that is made
--all attributes are required, and so are not null
--only order_id is unique
create table store_order
	(
		order_id varchar(36),
		paid_by varchar(8) not null,
		total_price numeric(10,2) not null,
		sent_address varchar(60) not null,
		billed_address varchar(60) not null,
		current_status varchar(50) not null,
		ordered_date date not null,
		estimated_days_in_transit numeric(1,0) not null,
		estiamte_delivery_date date not null,
		primary key (order_id)
	);
--relation book_ordered, connects book to store_order
--on delete cascade to store_order and book
--order_id, isbn used as primary key
create table book_ordered
	(	
		order_id varchar(36),
		isbn varchar(13),
		quantity numeric(9,0) not null,
		foreign key (order_id) references store_order
		on delete cascade,
		foreign key (isbn) references book
		on delete cascade,
		primary key (order_id, isbn)
	);
--relation user_order, connects store_user to store_order
--on delete cascade to store_order and store_user
--username, order_id used as primary key
create table user_order
	(
		username varchar(10) not null,
		order_id varchar(36),
		primary key (order_id),
		foreign key (username) references store_user
		on delete cascade,
		foreign key (order_id) references store_order
		on delete cascade
	);
--entity store_owner, represents any owners
--all attributes are required, and so not null
--assumed only owner_username is unique
create table store_owner
	(
		owner_username varchar(10),
		password varchar(10) not null,
		name varchar(30) not null,
		owner_bank varchar(7) not null,
		warehouse_address varchar(60) not null,
		primary key (owner_username)
	);
--relation owner_order, connects store_owner to store_order
--on delete cascade to store_order and store_owner
--owner_username, order_id used as primary key
create table owner_order
	(
		owner_username varchar(10),
		order_id varchar(36),
		primary key (owner_username, order_id),
		foreign key (owner_username) references store_owner
		on delete cascade,
		foreign key (order_id) references store_order
		on delete cascade
	);
--relation has_in_collection, connects store_owner to book
--as the name suggests, it represents an owner having a book in their collection (available for sale)
--on delete cascade to book and store_owner
--owner_username, isbn used as primary key
create table has_in_collection
	(	
		owner_username varchar(10) not null,
		isbn varchar(13),
		quantity numeric(9,0) not null,
		past_month_sale numeric(9,0) default 0,
		primary key (isbn),
		foreign key (owner_username) references store_owner
		on delete cascade,
		foreign key (isbn) references book
		on delete cascade
	);
--entity publisher, represents each publisher
--all attributes are required and so not null
--assumed only name is unique, 
--some amateur small publishers do share locations, and some only uses different names to sell different genres when they are actually the same company
create table publisher
	(	
		publisher_name varchar(60),
		publisher_address varchar(60) not null,
		publisher_email varchar(60) not null,
		publisher_phone varchar(15) not null,
		publisher_bank_account varchar(8) not null,
		primary key (publisher_name)
	);
--relation book_publisher, connects book to publisher
--as the name suggests, it represents an publisher having a book (being the one to receive percentage from book sales)
--isbn, publisher_name used as primary key
create table book_publisher
	(	
		isbn varchar(13),
		publisher_name varchar(60),
		primary key (isbn, publisher_name),
		foreign key (isbn) references book
		on delete cascade,
		foreign key (publisher_name) references publisher
		on delete cascade
	);
