import sys, os
import re, codecs
import csv

git_dir_korr = "D:\git\korrektur"
git_dir_tool = "D:\git\mancelius-epitaphium"

dir_path = sys.argv[1]

files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f[-4:] == ".xml"]

def open_xml(path):
	with open(path, "r", encoding="utf-8") as f:
		string = f.read()
		string = re.sub("\s*</?docu[^>]+>\s*", "", string)
		string = re.sub("\t+<z nr=\"re.+?</z>\s+", "", string)
		string = re.sub("<side>.+</side>", "", string)
		string = re.sub("\t*</?z([^>]+)?>", "", string)
		string = re.sub("\s*[\r\n]+?", " ", string)
	return string

y = 1
out = ""
for f in files:
	txt = open_xml(f)
	i = 1
	
	txt = re.sub("<lpp nr=\"(\d*(?:{\d+}|[ab])?)\">", " [S. {y}.\g<1>] ".format(y=y), txt)
	txt = re.sub("\s*</lpp>\s*", " ", txt)
	txt = re.sub("\s+", " ", txt)
	txt = re.sub("- ", "", txt)
	txt = re.sub("⸗ ", "⸗", txt)
	
	while re.search("<h[^>]*/>", txt):
		txt = re.sub("<h[^>]*/>", "\n\nTeil {y}.{i}\n\n".format(y=y,i=i), txt, count=1)
		
		i += 1
	y += 1
	
	txt = re.sub(" (\[.+?\]) \n\n(\S)", " \n\n\g<1> \g<2>", txt)
	
	txt = re.sub("<[^>]+?/>", "\n\n", txt)
	
	out += txt

with open(dir_path.split("\\")[-2] + "-leseversion.txt", "w", encoding="utf-8-sig") as file:
	file.write(out)