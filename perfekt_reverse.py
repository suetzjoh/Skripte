import sys, os
import re, regex, codecs
import csv

from bs4 import BeautifulSoup, Tag, NavigableString
import pandas as pd


git_dir_korr = "D:\git\korrektur"
perfekt_file = "perfekt_gesichtet.csv"
out_path = "perfekt.xml"

first_time = False

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
			cc = re.sub("(?<! )[{}](?! )", " \g<0> ", cc)
			for token in cc.split():
				splitt.append(token)
		else:
			input(cc, type(cc))
	
	return splitt
def new_line(lnr, content):
	tag = BeautifulSoup("z", "html.parser").new_tag('z', nr=lnr)
	tag.string = content.strip()
	
	return tag
	
	
if os.path.isfile(out_path):
	library = open_xml(out_path)
	
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

log = ""
def writelog():
	with open("log.txt", "w", encoding="UTF-8-sig") as file:
		file.write(log)

cite_stat = 0
i = 0

debugging = False
log = ""

pattern = "(?|^()({match})([ {{}}])|([ {{}}])({match})([ {{}}])|([ {{}}])({match})()$)"	
old_part = ""
# = [["part", "page", "line", "subpart", "match", "safeness", "Case", "Kommentar"]]
for part in library.library.find_all("document", attrs={"nr" : re.compile("^\d+?({\d+})?")}):
	part_nr = part["nr"]
	for page in part.find_all("lpp", attrs={"nr" : re.compile("^\d+?({{\d+}}|a|b)?")}):
		page_nr = re.search("\d+", page["nr"]).group(0)
		
		log = re.sub("^[\s\S]+(page {})".format(str(int(page_nr)-1)), "", log)
		log += "\n" + "page " + page_nr + "\n"
		
		for line in page.find_all("z", attrs={"nr" : re.compile("^\d+?({{\d+}})?")}):
			line_nr = line["nr"]
			
			if len(perfekta) == 0:
				break
			
			log += "\n" + part_nr + "," + page_nr + "," + line_nr + " " + line.text + "\n"
			text = split_contents(line)
			
			if text == []:
				continue
				
			matches = []
			for row in perfekta:
				if row[:2] == perfekta[0][:2]:
					row[4] = re.sub(".+?-", "", row[4])
					matches.append(row[:5])
					#matches.append(re.sub(".+?-", "", row).casefold())
				else:
					break
								
			
			log += str(matches) + "\n"
			matches = [row[4] for row in matches]
			
			newstring = ""
			
			int_page_nr = "".join([ch for ch in page_nr if ch.isdigit()])
			if int(part_nr) > int(perfekta[0][0]) or int(part_nr) == int(perfekta[0][0]) and int(int_page_nr) > int(perfekta[0][1]): #or int(part_nr) == int(perfekta[0][0]) and int(int_page_nr) == int(perfekta[0][1]) and int(line_nr) > int(perfekta[0][2]):
				print(log)
				input("emergency")
			
			for word in text:
				if len(perfekta) == 0:
					break
				
				word_ = re.search("(?:.+?>)([^<>]+)(?:</.+?>)", word).group(1) if word[0] == "<" else word
				
				log += word_ + " " + str(word_ in matches) + "\n"
				match = re.sub(".+?-", "", perfekta[0][4])
				
				if word_ in matches:
					ii = matches.index(word_)
					
					#log += str(ii) + "\n"
					
					if perfekta[ii][:3] != [part_nr, page_nr, line_nr]:
						continue
					
					new_ann = perfekta[ii][7]
					new_zit = cite_stat
					if word[0] == "<":
						soup_ = BeautifulSoup(word, "html.parser")
						if soup_.match.has_attr("ann"):
							new_ann = soup_.match["ann"]
						if soup_.match.has_attr("zit"):
							new_zit = soup_.match["zit"]	
						
					#newstring += "<match ann=\"{ann}\">".format(ann=new_ann, cit=new_zit) + match + "</match> "
					#newstring += "<match ann=\"{ann}\" zit=\"{cit}\">".format(ann=new_ann, cit=new_zit) + match + "</match> "
					newstring += "<match ann=\"{ann}\">".format(ann=new_ann, cit=new_zit) + word_ + "</match> "
					
					if not perfekta[0][0] == old_part:
						print("annotating part", perfekta[0][0], " ")
						old_part = perfekta[0][0]
					
					i += 1
					if i % 200 == 0:
						print(perfekta[0][:3], "   ", end="\r")
					
					#log += perfekta[ii][4] 
					
					perfekta.pop(ii)
					matches.pop(ii)
					
					#log += "\n" + newstring + "\n" + "popped: " + str(matches) + "\n"
					
				else:
					if word in ["„", "‚"]:
						cite_stat += 1
					elif word in ["“", "‘"]:
						cite_stat -= 1
					else:
						newstring += word + " "
					
			
			newstring = newstring[:-1] if newstring[-2:] == "> " else newstring
			newstring = re.sub("{ ([^<]+?) }", "{\g<1>}", newstring)
			newstring = re.sub("([^>]) { ?", "\g<1>{", newstring)
			log += newstring + "\n"
			
			line.replace_with(new_line(line_nr, newstring))
			
		#input(log)

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
	print("saving file       ")
	file.write(string)