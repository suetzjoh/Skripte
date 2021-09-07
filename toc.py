import sys, os
import re, codecs
import csv

dir_path = os.getcwd()
files = [f for f in os.listdir(dir_path) if os.path.isfile(f) and f[-3:] == "xml"]

def open_xml(path):
	with open(path, "r", encoding="utf-8") as f:
		string = f.read()
		string = re.sub("[\r\n]+?(\t+)?", " ", string)
		string = re.sub("<z nr=\"re.+?</z>", "", string)
	return string
		
def intify(str):
	return int(re.match("\d*", str).group(0))
def return_line_nr(nr):
	if nr < 10:
		return "0"+str(nr)
	else:
		return str(nr)
		
def extract_lines(read_path, save_path, first, last):
	
	
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

git_dir_korr = "D:\\git\\korrektur"
git_dir_tool = "D:\\git\\mancelius-postille\\McP1"

out = "teil;index;dt;predigt;p-zeilen;auslegung1;a1-zeilen;auslegung2;a2-zeilen;a-zeilen;h-zeilen;e-zeilen\n"
template = "{part};{index};{head};{predigt};{pz};{aus1};{aus1z};{aus2};{aus2z};{ausz};{headz};{intrz}\n"

def find_last_page_before(ii):
	for match in re.finditer("<lpp nr=\"(\d+)", txt[:ii]):
		pass
	return match

i = 1
y = 1
for f in files:
	txt = open_xml(f)
	
	while re.search("<p/><z nr=\"(\d+)\">", txt):
		p_tag = re.search("<p/><z nr=\"(\d+)\">", txt)
		pi = p_tag.start()
		p_page = find_last_page_before(pi)
		
		h_tag = re.search("<h/><z nr=\"(\d+)\">", txt[:pi])
		hi, hy = h_tag.start(), h_tag.end()
		h_page = find_last_page_before(hi)
		e_tag = re.search("<e/><z nr=\"(\d+)\">", txt[:pi])
		ei = e_tag.start()
		e_page = find_last_page_before(ei)
		
		if re.search("<h/><z nr=\"(\d+)\">", txt[pi:]):
			next_tag = re.search("<h/><z nr=\"(\d+)\">", txt[pi:]) 
			ni = next_tag.start() + pi
			next_page = find_last_page_before(ni)
			next_pagei = next_page.start()
		else:
			ni = len(txt)
			next_pagei = ni
		
		a1_tag = re.search("<a1/><z nr=\"(\d+)\">", txt[pi:ni])
		a1i = a1_tag.start() + pi
		a1_page = find_last_page_before(a1i)
		a2_tag = re.search("<a2/><z nr=\"(\d+)\">", txt[pi:ni])
		a2i = a2_tag.start() + pi
		a2_page = find_last_page_before(a2i)
		
		h_znr = h_tag.group(1)
		h_pnr = h_page.group(1)
		h_lines = txt[hi:ei].count("<z")
		e_znr = e_tag.group(1)
		e_pnr = e_page.group(1)
		e_lines = txt[ei:pi].count("<z")
		
		p_znr = p_tag.group(1)
		p_pnr = p_page.group(1)
		p_lines = txt[pi:a1i].count("<z")
		
		a1_znr = a1_tag.group(1)
		a1_pnr = a1_page.group(1)
		a1_lines = txt[a1i:a2i].count("<z")
		a2_znr = a2_tag.group(1)
		a2_pnr = a2_page.group(1)
		a2_lines = txt[a2i:ni].count("<z")
		
		newline = template.format(
			index = i,
			part = y,
			head = "\"" + re.sub("<.+?>", "", txt[hy:ei]) + "\"",
			predigt = p_pnr + "," + p_znr,
			pz = p_lines,
			aus1 = a1_pnr + "," + a1_znr,
			aus1z = a1_lines,
			aus2 = a2_pnr + "," + a2_znr,
			aus2z = a2_lines,
			ausz = a1_lines + a2_lines,
			headz = h_lines,
			intrz = e_lines
		)
		out += newline
		
		#print(txt[:ni])
		
		txt = txt[next_pagei:]
		
		i += 1
	y += 1
	
with open("textorganisation.csv", "w", encoding="utf-8-sig") as file:
	file.write(out)
		
		
		
		
		