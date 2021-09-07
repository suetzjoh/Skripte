import sys, os
import re, codecs
import csv

dir_path = os.getcwd()
files = [f for f in os.listdir(dir_path) if os.path.isfile(f) and f[-3:] == "xml"]

safe_regex = "([^ >]+(u((ſ)?(ſ|ẜ)(ch)?)(i|as|ee(s|ß))|(j|y)(i|ee)(s|ß)))( |<|/)"
unsafe_regex = "([^ >]{2,}(i|ee)(s|ß))( |<|/)"


def open_xml(path):
	with open(path, "r", encoding="utf-8") as f:
		lines = f.readlines()
	return lines
		
status = ""
part = 0
page = 0
results = [["part", "page", "line", "subpart", "match", "safeness"]]
for f in files:
	lines = open_xml(f)
	
	part += 1
	print("part", part)
	for line in lines:
		if "<h/>" in line:
			status = "head"
		elif "<e/>" in line:
			status = "intr"
		elif "<p/>" in line:
			status = "peri"
		elif "<a1/>" in line:
			status = "aus1"
		elif "<a2/>" in line:
			status = "aus2"
			
		page = re.search("<lpp nr=\"(\d+)\">", line).group(1) if re.search("<lpp nr=\"(\d+)\">", line) else page
		if re.search("<z nr=\"(\d+)\">", line):
			line_nr = re.search("<z nr=\"(\d+)\">", line).group(1) 
			
			safe_search = re.search(safe_regex, line)
			unsafe_serach = re.search(unsafe_regex, line)
			
			if safe_search:
				matches = re.findall(safe_regex, line)
				for match in matches:
					results.append([part, page, line_nr, status, match[0], "safe"])
			elif unsafe_serach:
				matches = re.findall(unsafe_regex, line)
				for match in matches:
					results.append([part, page, line_nr, status, match[0], "unsafe"])

with open("perfekt.csv", "w", encoding="utf-8-sig") as file:
	file.writelines([";".join([str(item) for item in result]) + "\n" for result in results])