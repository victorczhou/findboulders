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
dir_extension = "/boulders/"	# change this if your directory with csv is in different location/name

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

def parse_risk(gradestring):
	if "PG13" in gradestring or "PG-13" in gradestring:
		return "PG13"
	if "R" in gradestring:
		return "R"
	if "X" in gradestring:
		return "X"
	else:
		return "G"

dyno_words = ["dyno", "toss", "jump", "throw"]
crack_words = ["crack", "fist", "offwidth", "off-width", "jam", "splitter", "fingerlock", "ringlock"]
traverse_words = ["traverse", "traversing"]
steep_words = ["steep", "roof", "overhang", "overhung", "cave"]
technical_words = ["technical", "slab", "crimp", "razor", "insecure", "stem", "friction", "thin", "balance", "micro", "tiny", "blank"]
mantle_words = ["mantle", "mantling", "beach", "beached", "whale"]

slab_words = ["slab", "friction"]
# overhang_words is the same as steep_words
vertical_words = ["vertical"]

def parse_style(description):
	for word in dyno_words:
		if word in description:
			return "dyno"
	for word in crack_words:
		if word in description:
			return "crack"
	for word in traverse_words:
		if word in description:
			if re.match("[Ll]eft", description) and re.match("[Rr]ight", description):
				return "traverse"
	for word in steep_words:
		if word in description:
			return "steep"
	for word in technical_words:
		if word in description:
			return "technical"
	for word in mantle_words:
		if word in description:
			return "mantle"
	return "face"

def parse_angle(description):
	for word in slab_words:
		if word in description:
			return "slab"
	for word in steep_words:
		if word in description:
			holda = "overhang"
	return "vertical"

conn = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
cur = conn.cursor()

boulder_dir = os.getcwd()+dir_extension
files = []
for (dirpath, dirnames, filenames) in os.walk(boulder_dir):
	for filename in filenames:
		if re.search('^route-finder.*\.csv', filename):
			files.append(filename)
		else:
			print("Warning: csv file many not be correctly formatted: ", filename)
	break

for file in files:
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

			if "Traverse" in row[0]:
				holdstyle = "traverse"
			else:
				page = requests.get(url) 	# MP has static HTML
				soup = BeautifulSoup(page.content, 'html.parser')
				desc_element = soup.find('div', class_='fr-view') 	# MP has two <div class="fr-view"> for desc and location, respectively
				if desc_element is None:
					print("Error: cannot find description for climb ", row[0], ".")
				else:
					holdstyle = parse_style(desc_element.text.strip())
					holdangle = parse_angle(desc_element.text.strip())
				

			cur.execute("INSERT INTO ca_boulders (name, grade, rating, climb_style, climb_angle, lat, lon, url, location, climb_risk) \
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", \
				(row[0], grade, row[3], holdstyle, holdangle, row[9], row[10], url, holdlocation, risk))
			conn.commit()


conn.close()