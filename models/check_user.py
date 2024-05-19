from enum import Enum
import sqlite3


class login_state(Enum):
    NOT_EXIST=1
    EXIST_BUT_WRONG=2
    EXIST_AND_IS_MEMBER=3
    EXIST_AND_IS_EMPLOYEE=4

def check_user(acc:str, passwd:str):
    connection=sqlite3.connect('db/coffee.db')
    cur=connection.cursor()
   #get schema
    cur.execute("PRAGMA table_info(Member)")
    results=cur.fetchall()
    attrs=[row[1]for row in results]
    schema_member=dict(zip(attrs,range(0,len(attrs))))
    cur.execute("PRAGMA table_info(Employee)")
    results=cur.fetchall()
    attrs=[row[1]for row in results]
    schema_employee=dict(zip(attrs,range(0,len(attrs))))
 
    #check whether this user account is in our DB.
    query_member="SELECT * FROM Member"
    query_employee="SELECT * FROM Employee"
    cur.execute(query_member)
    results=cur.fetchall()
    user_acc=None
    state=None
    member=True
    for row in results:
        if acc==row[schema_member["Email"]]:
            user_acc=row
            break
    print(user_acc)
    if user_acc==None:
        cur.execute(query_employee)
        results=cur.fetchall()
        for row in results:
            if acc==row[schema_employee["E_ID"]]:
                user_acc=row
                break
        if user_acc==None:
            state=login_state.NOT_EXIST.value
            return state
        else:
            member=False
    connection.close()
    #if this user account is in our DB, check its password is correct.
    if member==True:
        password=user_acc[schema_member["Password"]]
    else:
        password=user_acc[schema_employee["Password"]]
    if passwd!=password:
        state=login_state.EXIST_BUT_WRONG.value
    elif member==True:
        state=login_state.EXIST_AND_IS_MEMBER.value
    else:
        state=login_state.EXIST_AND_IS_EMPLOYEE.value
    return state

