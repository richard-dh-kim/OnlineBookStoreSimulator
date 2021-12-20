--This file gets called from the initializer.py when the program first starts
--only adds few users, one owner, and few books to play around with.
--adds all the books to the one owner

--insert relations
--insert store_user
insert into store_user values ('aa', 'aaa', 'afirst alast', '11111111', 'testshipping address 1111', 'test billing address asdifoj');
insert into store_user values ('bb', 'bbb', 'bfirst blast', '22222222', 'testshipping address 1324', 'test billing address zxcvxzcv');
--insert publisher
insert into publisher values('HARPERCOLLINS PUBLISHERS', 'HARPERCOLLINS PUBLISHERS address','HARPERCOLLINS PUBLISHERS email', '123456789123456', '12345678');
insert into publisher values('Faber & Faber', 'faber address', 'faber email', '123456789123455', '11111111');
insert into publisher values('testpulisher', 'test address', 'tes email', '123456789123444', '22222222');
--books that actually exist
insert into book values ('9780261102354', 'The Lord of The Rings: The Fellowship of the Ring', 'J. R. R. Tolkien', 'Fantasy', 448, 10.99, 10);
insert into book values ('9780261102361', 'The Lord of The Rings: The Two Towers', 'J. R. R. Tolkien', 'Fantasy', 464, 10.99, 20);
insert into book values ('9780261102378', 'The Lord of The Rings: The Return of the King', 'J. R. R. Tolkien', 'Fantasy', 464, 10.99, 30);
insert into book values ('9780007458424', 'The Hobbit', 'J. R. R. Tolkien', 'Fantasy', 368, 10.99, 40);
insert into book values ('9780571084838', 'Lord of The Flies', 'William Golding', 'Classics', 240, 14.50, 50);
--test books that does not exist
insert into book values ('2345134521534', 'testbook1', 'test authorname one', 'Fantasy', 240, 14.50, 50);
insert into book values ('3547654865748', 'testbook2', 'test authorname one', 'Classics', 240, 14.50, 50);
insert into book values ('1651455665133', 'testbook3', 'test authorname two', 'Fantasy', 240, 14.50, 50);
insert into book values ('4981116484684', 'testbook4', 'test authorname two', 'Classics', 240, 14.50, 50);
--relate book to publisher
insert into book_publisher values ('9780261102354', 'HARPERCOLLINS PUBLISHERS');
insert into book_publisher values ('9780261102361', 'HARPERCOLLINS PUBLISHERS');
insert into book_publisher values ('9780261102378', 'HARPERCOLLINS PUBLISHERS');
insert into book_publisher values ('9780007458424', 'HARPERCOLLINS PUBLISHERS');

insert into book_publisher values ('9780571084838', 'Faber & Faber');

insert into book_publisher values ('2345134521534', 'testpulisher');
insert into book_publisher values ('3547654865748', 'testpulisher');
insert into book_publisher values ('1651455665133', 'testpulisher');
insert into book_publisher values ('4981116484684', 'testpulisher');
--insert store_owner
insert into store_owner values ('cc', 'ccc', 'ccName', '1234567', 'test warehouse address 1111');
--insert has_in_collection
insert into has_in_collection values ('cc', '9780261102354', 50);
insert into has_in_collection values ('cc', '9780261102361', 50);
insert into has_in_collection values ('cc', '9780261102378', 50);
insert into has_in_collection values ('cc', '9780007458424', 50);
insert into has_in_collection values ('cc', '9780571084838', 50);
insert into has_in_collection values ('cc', '2345134521534', 50);
insert into has_in_collection values ('cc', '3547654865748', 50);
insert into has_in_collection values ('cc', '1651455665133', 50);
insert into has_in_collection values ('cc', '4981116484684', 50);