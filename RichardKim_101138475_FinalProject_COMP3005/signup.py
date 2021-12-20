import psycopg2
import constants

#access database to make sure username_input is not a duplicate
#return: 0 - good to use, 1 - already exists
def test_username(username_input):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #run loginFunc()
        try:
            cur.callproc('checkUserName', (username_input,))
            result = cur.fetchall()
            conn.commit()
            cur.close()
            return result[0][0]

        except Exception as functionerr:
            print("Could not run function: ", functionerr) 
            conn.rollback()

    except Exception as sqle:
        print("Exception : ", sqle)

#keep taking username and testing it till it is confirmed there are no duplicates
def set_username():
    flag = 1
    while flag == 1:
        username = input("Please enter your desired username\n(required field, needs to be unique, max 10 characters, if more than 10 characters are given, only first 10 will be taken): ")
        #if length is more than 10, take only first 10
        if len(username) > 10:
            username =username[0:10]

        flag = test_username(username)
        if flag == 1:
            print("Username already exist, try another username")
    
    print("Username test passed")
    return username

#add a storeOwner and warehouse using data provided
def add_owner(username_input, password_input, name_input, banking_input, warehouse_address):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #add owner
        try:
            cur.execute("insert into store_owner values (%s, %s, %s, %s, %s)", (username_input, password_input, name_input, banking_input, warehouse_address))
            conn.commit()
        except Exception as query_error:
            print("Could not execute query to add owner: ", query_error) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)

#take rest of the information required from an owner
# when complete, add owner data to database
def signup_owner(username):
    password = input("Please enter your password\n(max 10 characters, if more than 10 characters are given, only first 10 will be taken): ")
    if len(password) > 10:
        password =password[0:10]

    name = input("Please enter your name\n(max 30 characters, if more than 30 characters are given, only first 30 will be taken): ")
    if len(name) > 30:
        name =name[0:30]
    
    banking_flag = 0
    #check if payment_info is 8 digits and only contains numbers 
    while banking_flag == 0:
        banking_info = input("Please enter your banking information\n(required field, 7 digit number to mimic bank account number): ")
        if len(banking_info) == 7 and banking_info.isdecimal():
            banking_flag = 1
    
    warehouse_address = input("Please enter your warehouse address\n(required field, max 60 characters, if more than 60 characters are given, only first 60 will be taken):")
    if len(warehouse_address) > 60:
        warehouse_address =warehouse_address[0:60]
    
    add_owner(username, password, name, banking_info, warehouse_address)
    print("store owner added")

#add a storeuser using data provided
def add_user(username_input, password_input, name_input, payment_info, shipping_address, billing_address):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #add user
        try:
            cur.execute("insert into store_user values (%s, %s, %s, %s, %s, %s)", (username_input, password_input, name_input, payment_info, shipping_address, billing_address))
            conn.commit();

        except Exception as query_error:
            print("Could not execute query (add_user() - add user): ", query_error) 
            conn.rollback()
    except Exception as sqle:
        print("Exception : ", sqle)
    
#take rest of the information required from a user
# when complete, add user data to database
def signup_user(username):
    print("ALL FIELDS ARE REQUIRED, DO NOT HAVE ANY EMPTY INPUTS")
    password = input("Please enter your password\n(required field, max 10 characters, if more than 10 characters are given, only first 10 will be taken): ")
    if len(password) > 10:
        password =password[0:10]

    name = input("Please enter your name\n(required field, max 30 characters, if more than 30 characters are given, only first 30 will be taken): ")
    if len(name) > 30:
        name =name[0:30]

    payment_flag = 0
    #check if payment_info is 8 digits and only contains numbers 
    while payment_flag == 0:
        payment_info = input("Please enter your payment information\n(required field, 8 digit number to mimic credit card number): ")
        if len(payment_info) == 8 and payment_info.isdecimal():
            payment_flag = 1
    
    shipping_address = input("Please enter your shipping address\n(required field, max 60 characters, if more than 60 characters are given, only first 60 will be taken):")
    if len(shipping_address) > 60:
        shipping_address =shipping_address[0:60]
    billing_address_same = input("Enter 0 if your billing address is the same as shipping address, 1 if not:")
    if billing_address_same == '1':
        billing_address = input("Please enter your billing address\n(required field, max 60 characters, if more than 60 characters are given, only first 60 will be taken):")
        if len(billing_address) > 60:
            billing_address =billing_address[0:60]
    else:
        billing_address = shipping_address

    add_user(username, password, name, payment_info, shipping_address, billing_address)
    print("store user added")

#process main page for signup, routes into other functions as required
def signup():
    print("")
    print("SignUp page")

    username = set_username()
    user_type = input("Are you looking to purchase books or sell books? 0 to be a bookstore owner, 1 to be a user: ")
    completion_message = "\n\nCongrats! Signup is complete! Now Please Login from the Welcome Page."

    #owner
    if user_type=='0':
        signup_owner(username)
        print(completion_message)
    #user
    else:
        signup_user(username)
        print(completion_message)