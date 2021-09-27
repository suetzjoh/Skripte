import sys, os
import re, regex, codecs
import csv

from bs4 import BeautifulSoup


git_dir_korr = "D:\git\korrektur"
perfekt_file = "perfekt_gesichtet.csv"

def open_xml(path):
	print("open", path)
	with open(path, "r", encoding="utf-8") as f:
		read = f.read()
		soup = BeautifulSoup(read, "html.parser")
	return soup
	
library = BeautifulSoup("<library/>", "html.parser")

files = [os.path.join(git_dir_korr, f) for f in os.listdir(git_dir_korr) if f[-4:] == ".xml"]
for f in files:
	library.library.append(open_xml(f).document)

with open(perfekt_file, 'r', encoding="UTF-8-SIG") as csvfile:
	print("loading database")
	reader = csv.reader(csvfile, dialect='excel', delimiter=';')
	db = [row for row in reader]
	db.sort(key=lambda x: (int(x[0]), int(x[1]), int(x[2]))) # part, page, line

log = ""
def writelog():
	with open("log.txt", "w", encoding="UTF-8") as file:
		file.write(log)

pattern = "(?|^()({match})([ {{}}])|([ {{}}])({match})([ {{}}])|([ {{}}])({match})()$)"	
old_part = ""
# = [["part", "page", "line", "subpart", "match", "safeness", "Case", "Kommentar"]]
for i in range(len(db)):
	perfekt = db[i]
	if i % 200 == 0:
		print(perfekt[:3], "   ", end="\r")
	
	part = library.library.find("document", attrs={"nr" : re.compile("^{}({{\d+}})?".format(perfekt[0]))})
	page = part.find("lpp", attrs={"nr" : re.compile("^{}({{\d+}})?".format(perfekt[1]))})
	line = page.find("z", attrs={"nr" : re.compile("^{}({{\d+}})?".format(perfekt[2]))})
	
	if not perfekt[0] == old_part:
		print("annotating part", perfekt[0], " ")
		old_part = perfekt[0]
	
	text = line.text
	quant = len(regex.findall(pattern.format(match=perfekt[4]), text))
	if not quant == 1:
		log += "emergency: " + str(quant) + str(perfekt) + "\n" + text + "\n\n"
		writelog()
		
	text = regex.sub(pattern.format(match=perfekt[4]), "\g<1> <match ann=\"{ann}\">\g<2></match> \g<3>".format(ann=perfekt[7]), text, re.IGNORECASE)
	line.string.replace_with(text)
	

with open("perfekt.xml", "w", encoding="utf-8-sig") as file:
	string = str(library)
	string = re.sub(r"<(([^> ]+?)[^>]*)></\2>", "<\g<1>/>", string)
	string = re.sub("([^/]>)<", "\g<1>\n<", string)
	string = re.sub("(</?document)", "\t\g<1>", string)
	string = re.sub("(</?lpp)", "\t\t\g<1>", string)
	string = re.sub("^(<(a|e|h|p|s|z))", "\t\t\t\g<1>", string)
	string = re.sub("  ", " ", string)
	string = re.sub("&lt;", "<", string)
	string = re.sub("&gt;", ">", string)
	print("saving file       ")
	file.write(string)