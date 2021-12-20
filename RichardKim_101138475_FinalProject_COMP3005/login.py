import psycopg2
import constants
"""
opens up database to run attemptLogIn

params: usename and password inputed
return: 0 - username does not exist in database (both user and owner), 1 - username is a User, but wrong password
        2 - username is an Owner, but wrong password, 3 - login success, as user, 4 - login success, as owner
"""
def check_login_creds(username_input, password_input):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #run loginFunc()
        try:
            cur.callproc('attemptLogIn', (username_input, password_input))

            result = cur.fetchall()

            cur.close()
            return result[0][0]

        except Exception as function_err:
            print("Could not run function: ", function_err) 
            conn.rollback()

    except Exception as sqle:
        print("Exception : ", sqle)

#get name of the user that was able to successfully login
def get_users_name(username):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        try:
            cur.execute('select * from store_user where username = %s', ([username]))

            result = cur.fetchall()

            cur.close()
            return result[0][2]

        except Exception as qerr:
            print("Could not run query (get_users_name): ", qerr) 
            conn.rollback()

    except Exception as sqle:
        print("Exception : ", sqle)

#get name of the owner that was able to successfully login
def get_owners_name(username):
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        try:
            cur.execute('select * from store_owner where owner_username = %s', ([username]))

            result = cur.fetchall()

            cur.close()
            return result[0][2]

        except Exception as qerr:
            print("Could not run query (get_owners_name): ", qerr) 
            conn.rollback()

    except Exception as sqle:
        print("Exception : ", sqle)

"""
function to take user input and run check_login_creds
return: 0 - login failed, 1 - login success, as user, 2 - login success, as owner
"""
def login():
    print("")
    print("Login page")
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")

    login_val = check_login_creds(username, password)
    name = ""

    if login_val == 0:
        print("Username does not exist, try again")
        return 0, name, username
    
    elif login_val == 1:
        print("Wrong password, try again (User)")
        return 0, name, username
    
    elif login_val == 2:
        print("Wrong password, try again (Owner)")
        return 0, name, username
    
    elif login_val == 3:
        print("Login Success (User)")
        name = get_users_name(username)
        return 1, name, username
    
    elif login_val == 4:
        print("Login Success (Owner)")
        name = get_owners_name(username)
        return 2, name, username