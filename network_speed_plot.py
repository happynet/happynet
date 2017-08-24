
import pandas as pd
from pandas import DataFrame
import psycopg2
import matplotlib.pyplot as plt

conn = psycopg2.connect(database = "testdb", user = "postgres", password = "123",  host = "127.0.0.1", port="5432")
#create connection cursor
cur = conn.cursor()
#calculate average connection time
#cur.execute("SELECT from_machine, to_machine, minute, avg(connection_time) as average_time from network_speed_3 group by from_machine, to_machine, minute having from_machine =1 and to_machine =2 order by minute asc")
#calculate heatmap
cur.execute("SELECT 0, AVERAGE_TIME FROM (SELECT from_machine, to_machine, avg(connection_time) as average_time from network_speed_3 group by from_machine, to_machine having from_machine =1 and to_machine =2) a UNION SELECT AVERAGE_TIME, 0 FROM (SELECT from_machine, to_machine, avg(connection_time) as average_time from network_speed_3 group by from_machine, to_machine having from_machine =2 and to_machine =1) b")
rows = cur.fetchall()
print(rows)
conn.close()

Index=['1','2']
Cols=['1','2']
df = pd.DataFrame(rows, index=Index,columns=Cols)

#df.to_csv("file.csv")
#df.AvgTime = df.AvgTime.astype(float)
#df.FromMachine = df.FromMachine.astype(float)

#df = pd.read_csv('file.csv')
plt.pcolor(df)
#df[['AvgTime']].plot()
plt.show()

