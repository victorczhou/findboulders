import requests			# html get requests
import psycopg2			# postgres
import os			# file searching
import csv			# parsing files
import re 			# regex for MP csv
from bs4 import BeautifulSoup 	# parse HTML

hostname = "localhost"
username = "boulder_user"
password = "boulders"
database = "ca_climbs"
trainingfile = "/training/devilslake_3star.csv"

styles = ["dyno", "crack", "traverse", "steep", "technical", "mantle", "face"]
angles = ["slab", "overhanging", "vertical"]

def parse_grade(gradestring):
	if  "V-easy" in gradestring:
		return 0
	else:
		holdmatch = re.search("V[0-9]+", gradestring)
		if holdmatch is not None:
			holdv = holdmatch.group()
			return holdv[1:]
		else:
			print("Error: invalid grade. -1 inserted.")
			return -1

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
		desc = ""
		holdangle = "0"
		holdstyle = "0"

		page = requests.get(url) 	# MP has static HTML
		soup = BeautifulSoup(page.content, 'html.parser')
		desc_element = soup.find('div', class_='fr-view') 	# MP has two <div class="fr-view"> for desc and location, respectively
		if desc_element is None:
			print("Error: cannot find description for climb ", row[0], ".")
			continue
		else:
			desc = desc_element.text.strip()
			print(row[0], " V", grade)
			print("STYLE: dyno, crack, traverse, steep, technical, mantle, face")
			while holdstyle not in styles:
				holdstyle = input()
			print("ANGLE: slab, overhanging, vertical")
			while holdangle not in angles:
				holdangle = input()
			
		cur.execute("INSERT INTO boulder_training (name, grade, climb_angle, climb_style, description, url) \
			VALUES (%s, %s, %s, %s, %s, %s);", \
			(row[0], grade, holdangle, holdstyle, desc, url))
		conn.commit()


conn.close()