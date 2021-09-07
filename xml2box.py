import sys, os
import re, codecs
import csv
import marshmallow
from bs4 import BeautifulSoup, Tag

def open_xml(path):
	with open(path, "r", encoding="utf-8") as f:
		return re.sub("[\r\n]+?( +)?", "", f.read())
		
def intify(str):
	return int(re.match("\d*", str).group(0))
def return_line_nr(nr):
	if nr < 10:
		return "0"+str(nr)
	else:
		return str(nr)
		
def extract_lines(read_path, save_path, first, last):
	raw = open_xml(read_path)
	soup = BeautifulSoup(raw, "html.parser")
	print("have read the file")
	
	page_a = intify(first.split(",")[0])
	line_a = intify(first.split(",")[1])
	page_z = intify(last.split(",")[0])
	line_z = intify(last.split(",")[1])
	
	doc_title = soup.document["title"]
	output = "\\_sh v3.0  621  Text\n\n\\id {id}\n\n".format(id=doc_title)
	
	store = []
	for page in soup.document.find_all("lpp"):
		page_nr = intify(page["nr"]) # "56a"
		if not (page_nr < page_a or page_nr > page_z):
			for line in page.find_all("z"):
				if line["nr"] in ["re", "title"]:
					continue
					
				line_nr = intify(line["nr"])
				if not ((page_nr == page_a and line_nr < line_a) or (page_nr == page_z and line_nr > line_z)):
					text = line.text
					reference = "{title}_{page}.{line}".format(title=doc_title, page=page["nr"], line=return_line_nr(line_nr))
					
					store.append([reference, text])
		elif page_nr > page_z:
			break
	
	konkordanz = []
	for i in range(len(store)):
		if store[i][1][-1] == "-":
			next_line = store[i+1][1].split(" ", 1)
			
			store[i][1] = store[i][1][:-1] + "=|" + next_line[0]
			store[i+1][1] = next_line[1]
			
		output += "\\ref {ref}\n\\tx {tx}\n\\std\n\\mrph\n\\lm\n\\PoS\n\\gD\n\n".format(ref=store[i][0], tx=store[i][1])
		
		for word in store[i][1].split(" "):
			word_ = re.sub("=|", "", word)
			if not word_ in konkordanz:
				konkordanz.append(word_)
			
	with open(save_path, "w", encoding="utf-8") as f:
		f.write(output)
		print("printed", save_path)
	
	save_path = re.sub(".txt", "_konk.txt", save_path)
	konkordanz.sort()
	with open(save_path, "w", encoding="utf-8") as f:
		f.write("\n".join(konkordanz))
		print("printed", save_path)

def extract_sentences(read_path, save_path, first, last):
	raw = open_xml(read_path)
	soup = BeautifulSoup(raw, "html.parser")
	print("have read the file")
	
	page_a = intify(first.split(",")[0])
	line_a = intify(first.split(",")[1])
	page_z = intify(last.split(",")[0])
	line_z = intify(last.split(",")[1])
	
	doc_title = soup.document["title"]
	output = "\\_sh v3.0  621  Text\n\n\\id {id}\n\n".format(id=doc_title)
	
	store = []
	line_first = 0
	sentence = ""
	delimiter = " [.:?!] ?"
	for page in soup.document.find_all("lpp"):
		page_nr = intify(page["nr"]) # "56a"
		if not (page_nr < page_a or page_nr > page_z):
			for line in page.find_all("z"):
				if line["nr"] in ["re", "title"]:
					continue
					
				line_nr = intify(line["nr"])
				if not ((page_nr == page_a and line_nr < line_a) or (page_nr == page_z and line_nr > line_z)):
					if line_first == 0:
						line_first = return_line_nr(line_nr)
						
					text = line.text
					
					if not re.search(delimiter, text):
						sentence += text
						
						if sentence[-1] == "-":
							sentence = sentence[:-1]
						elif not sentence[-1] == " ":
							sentence += " "
					else:
						m = re.search(delimiter, text)
						while m:
							sentence += text[:m.end()]
							
							text = text[m.end():]
							m = re.search(delimiter, text)
							
							
							reference = "{title}_{page}.{l1}–{l2}".format(title=doc_title, page=page["nr"], l1=line_first, l2=return_line_nr(line_nr))
							line_first = line_nr
							
							store.append([reference, sentence])
							sentence = ""
		elif page_nr > page_z:
			break
		
	for i in range(len(store)):
		output += "\\ref {ref}\n\\tx {tx}\n\\std\n\\mrph\n\\lm\n\\PoS\n\\gD\n\n".format(ref=store[i][0], tx=store[i][1])
			
	save_path = re.sub(".txt", "_Sätze.txt", save_path)
	save_path = "Wortlisten/" + save_path
	with open(save_path, "w", encoding="utf-8") as f:
		f.write(output)
		print("printed", save_path)

git_dir_korr = "D:\\git\\korrektur"
git_dir_tool = "D:\\git\\mancelius-postille\\McP1"

input_path = os.path.join(git_dir_korr, sys.argv[1] + ".xml")
output_path = os.path.join(git_dir_tool, sys.argv[2] + ".txt")

by_phrase = False
by_line = False
if len(sys.argv) == 4:
	if sys.argv[3] == "p":
		by_phrase = True
	elif sys.argv[3] == "l":
		by_line = True
		
	

supervisor = True
while supervisor:
	first = input("read from page,line: ")
	last = input("to page,line: ")

	if re.match("\d*,\d*", first) and re.match("\d*,\d*", last):
		supervisor = False
		if by_phrase:
			extract_sentences(input_path, output_path, first, last)
		elif by_line:
			extract_lines(input_path, output_path, first, last)
		else:
			extract_lines(input_path, output_path, first, last)
			extract_sentences(input_path, output_path, first, last)
	else:
		print("page,line!")






