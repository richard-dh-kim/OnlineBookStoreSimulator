--this file gets called from the initializer.py when the program first starts
--contains list of functions that are added the scheme and used in the program

/*
function to log the user in, used by check_login_creds(username_input, password_input) in login.py
params:
    uname - username of user logging in
    psswrd - password of user logging in
returns:
    0 - login failed (username does not exist in both users and owners)
    1 - login failed (username exist in users, but password wrong)
    2 - login failed (username exist in owners, but password wrong)
    3 - login success (user)
    4 - login success (owner)
*/
create function attemptlogin (uname varchar(10), psswrd varchar(10))
returns integer as
$$
declare
	flag int;
begin
    --flag to save the result, default will be 0. so if result is 0, we know the username does not exist in both users and owners
	flag := 0;
    --flag will be 1 if username provided is for a users
	if exists (select 1 from store_user u where u.username = uname) then
    flag := 1;
	end if;
	--flag will be 2 if username provided is for an owners
	if exists (select 1 from store_owner o where o.owner_username = uname) then
    flag := 2;
	end if;
    --if flag is 1, see if password matches to the user, if matches, set flag to 3
    if exists (select 1 from store_user u where u.username = uname and u.password = psswrd) then
    flag := 3;
	end if;
    --if flag is 2, see if password matches to the owner, if matches, set flag to 4
    if exists (select 1 from store_owner o where o.owner_username = uname and o.password = psswrd) then
    flag := 4;
	end if;

	return flag;
end;$$
language plpgsql;

/*
function to see if username already exists, used by test_username(username_input) in signup.py
params:
    uname - username to check
returns:
    0 - good to use 
    1 - already exists
*/
create function checkusername (uname varchar(10))
returns integer as
$$
declare
	flag int;
begin
    /*
    flag to save the result, default will be 0.
    flag = 0 if username is not found (good to use)
    flag = 1 if username is found (cant use)
    */
	flag := 0;
    --flag will be 1 if username provided is found from users
	if exists (select 1 from store_user u where u.username = uname) then
    flag := 1;
	end if;

    --flag will be 1 if username provided is found from owners
	if exists (select 1 from store_owner o where o.owner_username = uname) then
    flag := 1;
	end if;

	return flag;
end;$$
language plpgsql;

/*
function to set status of the order depending on the current date set by the user
delivery_estimate is number of days the delivery is estimated to take IN TRANSIT, this is a random integer between 1 and 9 (inclusive)
sets the current_status of the order depending on the current date
*/
create function set_status (ordered_date date, curr_date date, delivery_estimate int, order_id_input varchar(36))
returns integer as
$$
declare
	flag int;
begin
    flag:=0;
    --Day 0, 1: Preparing for shipment
	if curr_date <= (ordered_date + 1) then
	update store_order
    set current_status = 'Preparing for Shipment'
    where order_id = order_id_input;

    --Day 2 ~ delivery_estimate +1 (cause day 1 is prep time): In transit
    elsif curr_date > (ordered_date + 1) and curr_date < (ordered_date + 2 + delivery_estimate) then
    update store_order
    set current_status = 'In Transit'
    where order_id = order_id_input;

    --Day delivery_estimate + 2 (+1 cause day 1 is prep time): Out for Delivery
	elsif curr_date = (ordered_date + 2 + delivery_estimate) then
    update store_order
    set current_status = 'Out for Delivery'
    where order_id = order_id_input;

	--Day delivery_estimate + 3 ~ (+1 cause day 1 is prep time): Delivery Complete
	else
    update store_order
    set current_status = 'Delivery Complete'
    where order_id = order_id_input;
	end if;

	return flag;
end;$$
language plpgsql;