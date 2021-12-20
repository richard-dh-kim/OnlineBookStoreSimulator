from initializer import initialize
import sys
import login, signup, guest, user, owner

#initialize database
initialize()

while(1):
    welcome_msg = """
COMP3005 Final Project
Richard Kim, 101138475

**************************************************************************************************************
Welcome to Look Inna Book!

    If you have an account, please enter: 1
    If you would like to search books as a guest or signup, please enter: 2
    0 to exit the program

Please note you will note be able to purchase books as a guest, you will only be able to search them.

We highly recommend that you sign up, and log in.

**************************************************************************************************************
PLEASE MAKE SURE YOU HAVE READ THE README FILE, IT CONSISTS OF INFORMATION NEEDED TO PROPERLY RUN THIS PROGRAM
**************************************************************************************************************
    """
    print(welcome_msg)

    #1 to login, 2 to continue as guest, rest to exit
    mode_select_input = input("Enter in your choice: ")

    if mode_select_input == '1':
        login_var = login.login()

        while login_var[0] == 0:
            login_var = login.login()
        
        if login_var[0] == 1:
            user.user_mode(login_var[1], login_var[2])
        
        elif login_var[0] == 2:
            owner.owner_mode(login_var[1], login_var[2])

    elif mode_select_input == '2':
        guest_selected = """
    If you would like to continue as a guest, please enter: 1
    If you would like to create an account, please enter: 2
        """
        print(guest_selected)

        #1 for guest mode, 2 to signup
        account_select_input = input("Enter in your choice: ")
        if account_select_input == '1':
            print("Entering Guest Mode")
            guest.guest_mode()
        elif account_select_input == '2':
            signup.signup()

    else:
        print("Thank you for using Look Inna Book! See you soon")
        sys.exit()