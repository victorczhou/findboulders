import requests		# html get requests
import psycopg2		# postgres
import os			# file searching
import csv			# parsing files

hostname = "localhost"
username = "boulder_user"
password = "boulders"
database = "ca_boulders"

# query func goes here

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)




conn.close()