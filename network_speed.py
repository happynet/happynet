#!/usr/bin/python
import re
import psycopg2
from psycopg2 import sql

filename= "PC1toPC2.txt"
text_file = open(filename, "r")
regex2=re.compile(r'\d{2,}.\d{2,}') # look for time
regex3=re.compile(r'\d+') #look for all the digits in the string


conn = psycopg2.connect(database = "testdb", user = "postgres", password = "123",  host = "127.0.0.1", port="5432")
print ("Opened database successfully")

#create connection cursor
cur = conn.cursor()
#cur.execute("DROP TABLE NETWORK_SPEED_3;")
# create table:
# cur.execute('''CREATE TABLE NETWORK_SPEED_3
#       (ID SERIAL PRIMARY KEY     NOT NULL,
#       FROM_MACHINE             INT,
#       TO_MACHINE               INT,
#       ROW_NUMBER               INT,
#       MINUTE                   INT,
#       SEQUENCE_NUMBER          INT    NOT NULL,
#       CONNECTION_TIME          REAL     NOT NULL
#        );''')
# print ("Table NETWORK_SPEED_3 created successfully")


# #insert records
# for line in text_file:
#     list1= line.strip('\n').split(',')
#     if not line.strip(): continue   #remove the empty line
#     time = regex2.findall(list1[0])
#     all_digits=regex3.findall(list1[0])
#     if not len(all_digits)>5: continue   # remove timeout lines
#     cur.execute(
#         sql.SQL("INSERT INTO {} (FROM_MACHINE,TO_MACHINE,SEQUENCE_NUMBER,CONNECTION_TIME) VALUES ('1','2',%s,%s)")
#             .format(sql.Identifier('network_speed_3')),
#         [all_digits[5],time[1]]
#     )
#
# print ("Insert records into NETWORK_SPEED_3 succeeded")

#delete statement for testing purpose
#cur.execute("DELETE from NETWORK_SPEED_2")

#update statement
#row_number
# cur.execute("UPDATE network_speed_3 as t1 SET ROW_NUMBER = t2.row_num from (SELECT row_number() over(order by sequence_number) row_num, sequence_number from network_speed_3) t2  where t1.sequence_number = t2.sequence_number ")
# #minute
# cur.execute("UPDATE network_speed_3 as t1 SET MINUTE = t2.min from (SELECT ceil(ROW_NUMBER/61) min, sequence_number from NETWORK_SPEED_3) t2 where t1.sequence_number = t2.sequence_number ")

#cur.execute("INSERT INTO network_speed_3(FROM_MACHINE,TO_MACHINE,ROW_NUMBER,MINUTE,SEQUENCE_NUMBER,CONNECTION_TIME) VALUES('1','1',1,0,0,0)")

#select statement
cur.execute("SELECT * from network_speed_3 ")
rows = cur.fetchall()
print(rows)

conn.commit()
