import psycopg2
import constants
import sys
#funtion to initialize the database, resets the schema (hopefully it is named public) then inserts all tables, relations, functions, and triggers
def initialize():
    #open database
    try:
        conn = psycopg2.connect(host=constants.HOST, port=constants.PORT, dbname=constants.DBNAME, user=constants.USERID, password=constants.PASSWORD)
        cur = conn.cursor() 
        #run DDL.sql to add tables
        try:
            cur.execute(open('./SQL/DDL.sql','r').read())
            conn.commit();
            print("Tables added to the database")
            #run DML.sql to insert relations
            try:
                cur.execute(open('./SQL/DML.sql','r').read())
                conn.commit();
                print("Relations inserted to the database")
                #run Functions.sql to add functions
                try:
                    cur.execute(open('./SQL/Functions.sql','r').read())
                    conn.commit();
                    print("Functions added to the database")
                    #run Triggers.sql to add triggers and the functions they run
                    try:
                        cur.execute(open('./SQL/Triggers.sql','r').read())
                        conn.commit();
                        print("Triggers added to the database")
                        cur.close()

                    except Exception as functions_err:
                        print("Could not run Functions.sql ", functions_err)
                        conn.rollback()
                        sys.exit()
                except Exception as functions_err:
                    print("Could not run Functions.sql ", functions_err)
                    conn.rollback()
                    sys.exit()
            except Exception as dml_err:
                print("Could not run DML.sql ", dml_err)
                conn.rollback()
                sys.exit()
        except Exception as ddl_err:
            print("Could not run DDL.sql ", ddl_err) 
            conn.rollback()
            sys.exit()
    except Exception as initial_err:
        print("Exception : ", initial_err)
        sys.exit()
