import sys, os
import re, regex, codecs
import csv

from bs4 import BeautifulSoup, Tag, NavigableString
import pandas as pd


git_dir_korr = "D:\git\korrektur"
perfekt_file = "perfekt_gesichtet.csv"
out_path = "perfekt.xml"


auswertung = [["part", "page", "line", "match", "Kommentar", "subpart", "obliqua"]]


debugging = False
debug = ""
log = ""
logged = 0
def writelog():
	global logged, log
	logged = log.count("\n")
	with open("log.txt", "w", encoding="UTF-8-sig") as file:
		file.write(log)
		

def new_line(lnr, content):
	tag = BeautifulSoup("z", "html.parser").new_tag('z', nr=lnr)
	tag.string = content.strip()
	
	return tag
	
def open_xml(path):
	print("open", path)
	with open(path, "r", encoding="utf-8-sig") as f:
		read = f.read()
		soup = BeautifulSoup(read, "html.parser")
	return soup
	
def split_contents(soup):
	contents = soup.contents
	splitt = []
	
	for cc in contents:
		if isinstance(cc, Tag):
			splitt.append(str(cc))
		elif isinstance(cc, NavigableString):
			cc = re.sub("[{}](?! )", "\g<0> ", cc)
			cc = re.sub("(?<! )[{{}}]", " \g<0>", cc)
			for token in cc.split():
				splitt.append(token)
		else:
			input(cc, type(cc))
	
	return splitt
	
first_time = False
if os.path.isfile(out_path):
	ann_library = open_xml(out_path)
	
	library = BeautifulSoup("<library/>", "html.parser")

	files = [os.path.join(git_dir_korr, f) for f in os.listdir(git_dir_korr) if f[-4:] == ".xml"]
	for f in files:
		library.library.append(open_xml(f).document)
	
	first_time = False
else:
	library = BeautifulSoup("<library/>", "html.parser")

	files = [os.path.join(git_dir_korr, f) for f in os.listdir(git_dir_korr) if f[-4:] == ".xml"]
	for f in files:
		library.library.append(open_xml(f).document)
		
	first_time = True

with open(perfekt_file, 'r', encoding="UTF-8-SIG") as csvfile:
	print("loading database")
	reader = csv.reader(csvfile, dialect='excel', delimiter=';')
	perfekta = [row for row in reader if len(row) > 1]
	perfekta.sort(key=lambda x: (int(x[0]), int("".join([ch for ch in x[1] if ch.isdigit()])), int(x[2]))) # part, page, line

pattern = "(?|^()({match})([ {{}}])|([ {{}}])({match})([ {{}}])|([ {{}}])({match})()$)"	
cite_stat = 0 # Erzählebenen (obliquus)
count_abs = 0
old_part = ""

# = [["part", "page", "line", "subpart", "match", "safeness", "Case", "Kommentar"]]
for part in library.library.find_all("document", attrs={"nr" : re.compile("^\d+?({{\d+}})?")}):
	part_nr = part["nr"]
	ann_part = ann_library.library.find("document", attrs={"nr" : part["nr"]})
	
	for page in part.find_all("lpp", attrs={"nr" : re.compile("^\d+?({{\d+}}|a|b)?")}):
		page_nr = re.search("\d+", page["nr"]).group(0)
		ann_page = ann_part.find("lpp", attrs={"nr" : page["nr"]})
		
		debug = re.sub("^[\s\S]+(page {})".format(str(int(page_nr)-1)), "", debug)
		debug += "\n" + "page " + page_nr + "\n"
		
		for line in page.find_all("z", attrs={"nr" : re.compile("^\d+?({{\d+}})?")}):
			line_nr = line["nr"]
			ann_line = ann_page.find("z", attrs={"nr" : line["nr"]})
			
			if len(perfekta) == 0:
				break
			
			orig_text = split_contents(line)
			ann_text = split_contents(ann_line)
			
			debug += "\n" + part_nr + "," + page_nr + "," + line_nr + " " + " ".join(orig_text) + "\n" + " ".join(ann_text) + "\n"
			
			if orig_text == []:
				continue
				
			#da die Matches in der csv-Tabelle nicht immer in der Reihenfolge ihres Fundes aufgelistet sind, werden alle Matches auf derselben Seite geladen
			matches = []
			for row in perfekta:
				if row[:2] == perfekta[0][:2]:
					matches.append(row[:5])
				else:
					break
			debug += str(matches) + "\n"
			matches = [row[:3] + [re.sub(".+?-", "", row[4])] for row in matches]
			
			int_page_nr = "".join([ch for ch in page_nr if ch.isdigit()])
			if int(part_nr) > int(perfekta[0][0]) or int(part_nr) == int(perfekta[0][0]) and int(int_page_nr) > int(perfekta[0][1]):
				
				log += debug + "\n====="
				writelog()
	
				for jj in range(len(matches)):
					perfekta.pop(0)
					matches.pop(0)
			
			newstring = ""
			yy = 0
			for xx in range(len(orig_text)):
				orig_word = orig_text[xx]
				
				if len(perfekta) == 0:
					break
					
				if orig_word in ["„", "‚"]:
					cite_stat += 1
					
					if xx-yy >= len(ann_text) or orig_word != ann_text[xx-yy]:
						yy += 1
						
					#continue
					newstring += orig_word + " "
				elif orig_word in ["“", "‘"]:
					cite_stat -= 1
					
					if xx-yy >= len(ann_text) or orig_word != ann_text[xx-yy]:
						yy += 1
						
					#continue
					newstring += orig_word + " "
				else:
					ann_word = ann_text[xx-yy]
					
					debug += orig_word + " " + ann_word + " " + str([part_nr, page_nr, line_nr, orig_word] in matches) + "\n"
					
					if [part_nr, page_nr, line_nr, orig_word] in matches:
						ii = matches.index([part_nr, page_nr, line_nr, orig_word])
						if perfekta[ii][:3] != [part_nr, page_nr, line_nr]:
							continue
						
						if debugging: 
							debug += str(ii) + "\n"
						
						new_ann = perfekta[ii][7]
						new_obl = cite_stat
						if ann_word[0] == "<":
							soup_ = BeautifulSoup(ann_word, "html.parser")
							if soup_.match.has_attr("ann"):
								new_ann = soup_.match["ann"]
						else:
							#print(debug)
							
							answer = ""
							while answer != "j":
								answer = "j" #input("Huch, ein Missmatch bei einem match! Soll ich den annotieren oder nicht? (j/n)\n")
								if answer == "n":
									newstring += orig_word + " "
									continue
							
							
						#newstring += "<match ann=\"{ann}\">".format(ann=new_ann, cit=new_obl) + orig_word + "</match> "
						newstring += "<match ann=\"{ann}\" obl=\"{cit}\">".format(ann=new_ann, cit=new_obl) + orig_word + "</match> "
						#newstring += "<match ann=\"{ann}\">".format(ann=new_ann, cit=new_obl) + orig_word + "</match> "
						
						#teil, seite, linie, wort, kommentar, abschnitt-typ, erzählebene
						auswertung.append([part_nr, page_nr, line_nr, perfekta[ii][4], new_ann, perfekta[ii][3], new_obl])
						
						if not perfekta[0][0] == old_part:
							print("annotating part", perfekta[0][0], " ")
							old_part = perfekta[0][0]
						
						count_abs += 1
						if count_abs % 200 == 0:
							print(perfekta[0][:3], "   ", end="\r")
						
						if debugging: 
							debug += perfekta[ii][4] 
							
						if debugging: 
							debug += "\n" + newstring + "\n" + "popped: " + str(matches[ii]) + "\n"
						
						perfekta.pop(ii)
						matches.pop(ii)
						
					
					else:
						if ann_word[0] == "<": #wenn das Wort annotiert ist aber kein Match ist, dann ist es aus den Matches verloren gegangen
							debug = re.sub("^[\s\S]+(page {})".format(page_nr), "", debug)
							
							log += debug + "\n----"
							writelog()
							
							newstring += ann_word + " "
						else:
							newstring += orig_word + " "
			
			
			newstring = newstring[:-1] if newstring[-2:] == "> " else newstring
			newstring = re.sub("{ ([^<]+?) }", "{\g<1>}", newstring)
			newstring = re.sub("([^>]) { ?", "\g<1>{", newstring)
			debug += newstring + "\n"
			
			line.replace_with(new_line(line_nr, newstring))
				
		if debugging: 
			print(debug)

with open(out_path, "w", encoding="utf-8-sig") as file:
	string = str(library)
	while string[0] == " ":
		string = string[1:]
		
	string = re.sub(r"<(([^> ]+?)[^>]*)></\2>", "<\g<1>/>", string)
	string = re.sub("([^/]>)<", "\g<1>\n<", string)
	string = re.sub("(</?document)", "\t\g<1>", string)
	string = re.sub("(?<!\t)(</?lpp)", "\t\t\g<1>", string)
	string = re.sub("\n</side>", "</side>", string)
	string = re.sub("(?<![>\t])(<(a|e|h|p|s|z))", "\t\t\t\g<1>", string)
	string = re.sub("  ", " ", string)
	string = re.sub("&lt;", "<", string)
	string = re.sub("&gt;", ">", string)
	print("saving files      ")
	file.write(string)

with open("perfekt_auswertung.csv", "w", encoding="utf-8-sig", newline='') as csvfile:
	writer = csv.writer(csvfile, dialect='excel', delimiter=';')
	for row in auswertung:
		writer.writerow(row)
		
print(logged)
if logged > 0:
	print("log saved: {} lines".format(logged))
