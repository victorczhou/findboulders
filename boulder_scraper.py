import requests			# html get requests
import psycopg2			# postgres
import os			# file searching
import csv			# parsing files

hostname = "localhost"
username = "boulder_user"
password = "boulders"
database = "ca_climbs"

dir_extension = "/boulders/"	# change this if your directory with csv is in different location/name

# query func goes here

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cur = conn.cursor()

boulder_dir = os.getcwd()+dir_extension
files = []
for (dirpath, dirnames, filenames) in os.walk(boulder_dir):
	files.extend(filenames)
	break
print ("# files: ", len(files))

for file in files[:1]:
	file_ext = os.getcwd()+dir_extension+file
	with open(file_ext, 'r') as csvfile:
		csvreader = csv.reader(csvfile)
		next(csvreader)				# skips the first row of formatting
		for row in csvreader:
			url = row[2]
conn.close()