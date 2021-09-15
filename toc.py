import sys, os
import re, codecs
import csv

git_dir_korr = "D:\git\korrektur"
git_dir_tool = "D:\git\mancelius-postille\\McP1"

dir_path = git_dir_korr #os.getcwd()

files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f[-4:] == ".xml"]

def open_xml(path):
	with open(path, "r", encoding="utf-8") as f:
		string = f.read()
		string = re.sub("[\r\n]+?(\t+)?", " ", string)
		string = re.sub("<z nr=\"re.+?</z>", "", string)
	return string

out = "teil;index;dt;bibelstelle;predigt;p-zeilen;auslegung1;a1-zeilen;auslegung2;a2-zeilen;a-zeilen;h-zeilen;e-zeilen\n"
template = "{part};{index};{head};{bibel};{predigt};{pz};{aus1};{aus1z};{aus2};{aus2z};{ausz};{headz};{intrz}\n"

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
		p_page = find_last_page_before(pi) #suche alles bis zum Perikopenanfang
		
		h_tag = re.search("<h(?: teil=\"(.+?)\")?/><z nr=\"(\d+)\">", txt[:pi]) 
		hi, hy = h_tag.start(), h_tag.end()
		h_page = find_last_page_before(hi)
		bibelstelle = h_tag.group(1)
		e_tag = re.search("<e/>(?:<z nr=\"(\d+)\">)?", txt[:pi])
		ei = e_tag.start()
		e_page = find_last_page_before(ei)
		
		if re.search("<h( teil=\"(.+?)\")?/><z nr=\"(\d+)\">", txt[pi:]):
			next_tag = re.search("<h( teil=\"(.+?)\")?/><z nr=\"(\d+)\">", txt[pi:]) 
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
			bibel = bibelstelle,
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