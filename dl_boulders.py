import psycopg2			# postgres
import csv			# parsing files

hostname = "localhost"
username = "boulder_user"
password = "boulders"
database = "ca_climbs"

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cur = conn.cursor()

filename = "boulder_training.csv"
pre = "SELECT name, grade, climb_angle, climb_style, description FROM boulder_training"
copymsg = "COPY ({0}) TO STDOUT WITH DELIMITER ',' CSV HEADER".format(pre)

with open(filename, "w", encoding='utf-8') as file:
    cur.copy_expert(copymsg, file)

conn.close()