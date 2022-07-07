import re, os, csv
from docx import Document

git_dir_korr = "D:\git\korrektur"
git_dir_tool = "D:\git\mancelius-postille\\McP1"

dir_path = git_dir_korr

files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f[-4:] == ".xml"]

def open_xml(path):
	with open(path, "r", encoding="utf-8") as f:
		string = f.readlines()
	return string

doctitle = ""
page_nr = ""
line_nr = ""
in_citation = False

result = "doc;page;line;type;source;marg;text\n"

def get_citet_text(string, status):
	global result, in_citation, doctitle, page_nr, line_nr
	
	if not status:
		if "<bf" in string:
			in_citation = True
			
			result += doctitle + ";" + page_nr + ";" + line_nr + ";\""
			
			string = string[string.find("<bf"):]
			
			get_citet_text(string, in_citation)
			
			
		elif "<nf" in string:
			result += doctitle + ";" + page_nr + ";" + line_nr + ";\"" + re.search("<nf([^>]+?)?/>", string).group(0) + "\"\n"
			
	else:
		if not "<nf" in string:
			result += string
		else:
			in_citation = False
			
			split_ = re.search("<nf([^>]+?)?/>", string).end()
			result += string[:split_] + "\"\n"
			
			get_citet_text(string[split_:], in_citation)
		
for f in files:
	print(f)
	txt = open_xml(f)
	
	for line in txt:	
		line = line.strip()
		
		if "<document" in line:
			doctitle = re.search("title=\"(.+?)\">", line).group(1)
		elif "<lpp" in line:
			page_nr = re.search("<lpp nr=\"(.+?)\">", line).group(1)
			if len(page_nr) == 1:
				page_nr = "00" + page_nr
			elif len(page_nr) == 2:
				page_nr = "0" + page_nr
		elif "<z" in line:
			line_nr = re.search("<z nr=\"(.+?)\">", line).group(1)
			
			if len(line_nr) == "1":
				line_nr = "0" + line_nr
				
			
			get_citet_text(line, in_citation)
				
					
result = re.sub("</z><z[^>]+>", " | ", result)
result = re.sub(";\"<bf/>", ";;;\"", result)
result = re.sub(";\"<bf src='([^>]*)' adp='([^>]*)'/>", ";\"\g<2>\";\"\g<1>\";\"", result)				
result = re.sub(";((?:[^;]+)(?:(?<= );(?= )[^;]*)*)<nf/>", ";;\g<1>", result)
result = re.sub(";\"((?:[^;]+)(?:(?<= );(?= )[^;]*)*)<nf marg='([^>]*)'/>\"", ";\"\g<2>\";\"\g<1>\"", result)
result = re.sub(";\"<nf marg='([^>]*)'/>\"", ";;;\"\g<1>\";", result)
result = re.sub("\"id.\";(\"[^\"]+\")", "\g<1>;\g<1>", result)

with open("zitatesammlung.csv", "w", encoding="utf-8-sig") as file:
	file.write(result)