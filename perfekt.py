import sys, os
import re, codecs
import csv

git_dir_korr = "D:\git\korrektur"
git_dir_tool = "D:\git\mancelius-postille\\McP1"

dir_path = git_dir_korr #os.getcwd()

files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f[-4:] == ".xml"]

safe_regex = "([^ >{]+(u(ſ)?(ſ|ẜ)(i|ee(s|ß))|u((ſ)?(ſ|ẜ)ch)(i|as|ee(s|ß))|(j|y)(i|ee)(s|ß)))([ </{}])"
unsafe_regex = "([^ >{]{2,}(i|ee)(s|ß))([ </{}])"
second_regex = ">jis"


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
	for i in range(len(lines)):
		line = lines[i]
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
			
		page = re.search("<lpp nr=\"(\d+)", line).group(1) if re.search("<lpp nr=\"(\d+)", line) else page
		if re.search("<z nr=\"(\d+)\">", line):
			line_nr = re.search("<z nr=\"(\d+)\">", line).group(1) 
			
			safe_search = re.search(safe_regex, line)
			unsafe_serach = re.search(unsafe_regex, line)
			second_search = re.search(second_regex, line)
			
			if safe_search:
				matches = re.findall(safe_regex, line)
				for match in matches:
					results.append([part, page, line_nr, status, match[0], "safe"])
			if unsafe_serach:
				matches = re.findall(unsafe_regex, line)
				for match in matches:
					results.append([part, page, line_nr, status, match[0], "unsafe"])
			if second_search:
				if re.search("-<", lines[i-1]):
					results.append([part, page, line_nr, status, "jis", "trash"])

with open("perfekt.csv", "w", encoding="utf-8-sig") as file:
	file.writelines([";".join([str(item) for item in result]) + "\n" for result in results])