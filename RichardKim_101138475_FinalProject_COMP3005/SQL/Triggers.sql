/*
this file gets called from the initializer.py when the program first starts
contains list of triggers, and the procedures the triggers run that are added the scheme and used in the program

I do know that the 'procedures' are technically functions, and so they should be in the 'Functions.sql',
But I thought it is better to organize the procedure right next to each trigger it gets called by, to make TA/Prof's life easier as they mark my program
*/

/*
trigger to run after every update of 'has_in_collection'.
if quantity is below 10, it will automatically "send an email" to the publisher, reordering the quantity sold in the past month (past 30 days).

Of course, I did not implement the actual emailing, and made the new order from the publisher arrive immediately,
restocking the book in has_in_collection right away.

Basically a automatic restocking trigger/function.
*/
create function stock_books() 
returns trigger as $$
begin
	--if quantity is below 10
	if new.quantity < 10 then
		update has_in_collection
		set
		--'order' and restock
		quantity = quantity + new.past_month_sale
		where isbn=new.isbn;
	end if;
	return new;
end;$$
language plpgsql;

create trigger trigger_stock_book 
after update on has_in_collection 
for each row execute procedure stock_books();