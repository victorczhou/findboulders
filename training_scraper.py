import requests			# html get requests
import psycopg2			# postgres
import os			# file searching
import csv			# parsing files
import re 			# regex for MP csv
from bs4 import BeautifulSoup 	# parse HTML

hostname = "localhost"
username = "boulder_user"
password = "boulders"
database = "boulder_training"
trainingfile = "bishop_3star.csv"

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cur = conn.cursor()

file_ext = os.getcwd()+"/"+trainingfile
with open(file_ext, 'r', encoding='utf-8') as csvfile:
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

		if "Traverse" in row[0]:
			holdstyle = "traverse"
		else:
			page = requests.get(url) 	# MP has static HTML
			soup = BeautifulSoup(page.content, 'html.parser')
			desc_element = soup.find('div', class_='fr-view') 	# MP has two <div class="fr-view"> for desc and location, respectively
			if desc_element is None:
				print("Error: cannot find description for climb ", row[0], ".")
				continue
			else:
				holdstyle = parse_style(desc_element.text.strip())
				holdangle = parse_angle(desc_element.text.strip())
			
		cur.execute("INSERT INTO ca_boulders (name, grade, rating, climb_style, climb_angle, lat, lon, url, location, climb_risk) \
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", \
			(row[0], grade, row[3], holdstyle, holdangle, row[9], row[10], url, holdlocation, risk))
		conn.commit()


conn.close()