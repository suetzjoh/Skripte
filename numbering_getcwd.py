import re, os

for file in [file for file in os.listdir(os.getcwd()) if os.path.isfile(file)]:
	with open(file, 'r', encoding="UTF-8") as file_:
		file_text = file_.read()
	
	file_text = re.sub("(?<=_)(\d+)\.(\d)(?!\d)", "\g<1>.0\g<2>", file_text)
	file_text = re.sub("(?<=\d)–(\d)(?!\d)", "–0\g<1>", file_text)
	file_text = re.sub("_(\d)\.", "_00\g<1>.", file_text)
	file_text = re.sub("_(\d\d)\.", "_0\g<1>.", file_text)
	
	with open(file, 'w', encoding="UTF-8") as file_:
		file_.write(file_text)
	
	