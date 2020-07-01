import requests			# html get requests
import psycopg2			# postgres
import os			# file searching
import csv			# parsing files
import re 			# regex for MP csv

hostname = "localhost"
username = "boulder_user"
password = "boulders"
database = "ca_climbs"
dir_extension = "/boulders/"	# change this if your directory with csv is in different location/name

def parse_grade(gradestring):
	if gradestring == "V-easy":
		return 0
	else:
		holdmatch = re.search("V[0-9]+", gradestring)
		if holdmatch is not None:
			holdv = holdmatch.group()
			return holdv[1:]
		else:
			print("Error: invalid grade. -1 inserted.")
			return -1

def parse_risk(gradestring):
	if re.search("PG13", gradestring) or re.search("PG-13", gradestring):
		return "PG13"
	if re.search("R", gradestring):
		return "R"
	if re.search("X", gradestring):
		return "X"
	else:
		return "G"

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cur = conn.cursor()

boulder_dir = os.getcwd()+dir_extension
files = []
for (dirpath, dirnames, filenames) in os.walk(boulder_dir):
	for filename in filenames:
		if re.search("^route-finder.*\.csv", filename):
			files.append(filename)
		else:
			print("Warning: csv file many not be correctly formatted: ", filename)
	break

for file in files[:1]:
	file_ext = os.getcwd()+dir_extension+file
	with open(file_ext, 'r') as csvfile:
		csvreader = csv.reader(csvfile)
		next(csvreader)				# skips the first row of formatting
		for row in csvreader:
			# REFERENCE: from first line of MP csv
			# Route [0], Location [1], URL [2], "Avg Stars" [3], "Your Stars" [4], "Route Type" [5], Rating [6], Pitches [7], Length [8], "Area Latitude" [9], "Area Longitude" [10]

			url = row[2]
			grade = parse_grade(row[6])
			risk = parse_risk(row[6])
			holdstyle = "face"
			holdangle = "overhanging"
			holdlocation = "California"	# parse later not sorting by area

			cur.execute("INSERT INTO ca_boulders (name, grade, rating, climb_style, climb_angle, lat, lon, url, location, climb_risk) \
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", \
				(row[0], grade, row[3], holdstyle, holdangle, row[9], row[10], url, holdlocation, risk))
			conn.commit()


conn.close()