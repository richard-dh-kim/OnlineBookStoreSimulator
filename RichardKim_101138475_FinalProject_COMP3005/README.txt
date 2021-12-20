COMP3005A
Richard Kim
101138475

Instruction to run the program:
    1. BE SURE TO FOLLOW THE ISNTRUCTION PROMPTED, this program was meant to show knowledge in database and so I did not fully implement all error handling 
    (I did do quite a bit, but still please do not poke around to purposely get errors) 
    2. Unzip the files into a directory
    3. find the constsants.py, change the information in it to fit your database (username, password, ect)
    4. run main.py
    5. follow the instructions prompted

    Important Notes: 
    1. upon starting, initializer.py will run DDL.sql which will COMPLETELY DELETE YOUR SCHEMA NAMED PUBLIC **********************.
    If you do not want that to happen, comment out the line that calls initializer.py (line 6, main.py).
    Have a look at initializer.py, it will wipe out your entire schema named public, then add few rows of entity / relations.
    (few users, one owner, few books)'

    2. all SQL files are inside the directory SQL, mind you, most of the files do actually get used and ran.
    I do understand that we were suppose to use it to just document our queries, but I decided to take one more step and actually use the files.
    All flies except Queries.sql are used. Do not edit them mistakenly.

List of files with a brief description:

Inside 'SQL':
    __init__.py - needed to run the .sql files
    DDL.sql - set public schema to its natural state, then add tables needed
    DML.sql - insert few relations
    Functions.sql - inserts functions that will be used
    Queries.sql - list of all queries used in this program and explainations (there are few redundancies)
    Triggers.sql - inserts trigger that will be used

constants.py - defines the constants (database info)
guest.py - handles all action take by a guest user
initializer.py - initalizes the database to be used by this program
login.py - handles all action relating to logging in
main.py - main control file that routes out to all other files
owner.py - handles all actions taken by an owner
signup.py - handles all actions related to signning up
user.py - handles all actions taken by a user, and handles all actions while making an order (controlling owner's collection of books as well)
