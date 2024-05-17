import sqlite3

def add_user(acc:str, name:str, Tel:str, passwd:str):
    connection=sqlite3.connect('db/coffee.db')
    cur=connection.cursor()

    #insert member table
    insert_member="INSERT INTO Member (Email, Name, Tel, Password) VALUES (?, ?, ?, ?)"
    member_data=(acc,name,Tel,passwd)
    cur.execute(insert_member,member_data)
    connection.commit()
    connection.close()
