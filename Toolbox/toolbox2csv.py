import sys, os
import regex as re
import csv
import pandas
from copy import deepcopy

mcp_path = r"D:\git\mancelius-postille\McP1"
brp_path = r"D:\git\bretke-postille\BrP 2021-09-22\BrP"
aksl_path = r"D:\Hannes\Dateien\Uni\Baltoslavisch\Slavisch\Altkirchenslavisch\AkslToolbox"
tocharisch_path =  r"D:\Hannes\Dateien\Uni\Tocharisch\TochToolbox"

toolbox_folder_path = mcp_path
folder_path = os.path.basename(toolbox_folder_path)
log_path = os.path.basename(toolbox_folder_path) + "_log.csv"
out_path = os.path.basename(toolbox_folder_path) + "_annotation.csv"

if len(sys.argv) > 1:
	reexport = True
	print("gonna print")
	if not os.path.exists(folder_path):
		os.mkdir(folder_path)
	
else:
	print("not gonna print. otherwise, call function with 'print' ")
	reexport = False


#Generation der Listen mit den Dateien
toolbox_folder = list(os.walk(toolbox_folder_path))
	
other_files = [os.path.join(path, file) for path, dirs, files in toolbox_folder for file in files if file[-3:] == "txt" and file != "ReadmeAfter.txt" and not file[-8:] == "konk.txt" or "." not in file] #Datenbanken können im Prinzip als jede Datei gespeichert werden, naheliegend sind .txt und engungslose Dateien. Das Readme und die generierten Konkordanzen (die sollten vlt. gelöscht werden) müssen ausgenommen werden

#hier wird eine Liste mit den Datenbanktypen generiert
typ_files = {file[:-4] : os.path.join(path, file) for path, dirs, files in toolbox_folder for file in files if file[-3:] == "typ"}

types = {} 
for typ in typ_files:
	file_text = open(typ_files[typ], "r", encoding="UTF-8").read().replace("\\", "\\\\")
	type_name = re.search("\\\\\+DatabaseType (\S+)", file_text).group(1)
	
	#input(file_text)
	mkr_record = re.search("\\\\mkrRecord (\S+)", file_text).group(1)
	gloss_seperator = re.search("\\\\GlossSeparator (\S)", file_text).group(1) if re.search("GlossSeparator", file_text) else None

	
	markers = {}
	mkr_texts = re.findall("\\\\\+mkr [\s\S]+?\\\\-mkr", file_text)
	for mkr_text in mkr_texts: 
		
		keys = {}
		for match in re.findall("(?<=[\\\\+])([a-zA-Z]+) (.+?)\\n", mkr_text):
			keys[match[0]] = match[1]
			if match[0] == "mkr":
				key = match[1]
		
		markers[key] = keys
		
	jumps = {}
	jmp_texts = re.findall("\\\\\+intprc [\s\S]+?\\\\-intprc", file_text)
	for jmp_text in jmp_texts:
		
		keys = {}
		for match in re.findall("(?<=[\\\\+])([a-zA-Z]+) (.+?)\\n", jmp_text):
			keys[match[0]] = match[1]
			if match[0] == "mkr":
				key = match[1]
			
		if "jumps" in markers[key]:
			markers[key]["jumps"].append(keys)
		else:
			markers[key]["jumps"] = [keys]
		
	types[type_name] = [{"mkrRecord" : mkr_record, "GlossSeparator" : gloss_seperator, "markers" : [markers]}]

#mit der Liste der Sprachtypen soll das Verhalten von Toolbox nachgeahmt werden, nur vordefinierte Zeichen zu zählen
#lng_files = [os.path.join(path, file) for path, dirs, files in toolbox_folder for file in files if file[-3:] == "lng"]
#languages = {}
#for lng in lng_files:
	#file_text = open(lng, "r", encoding="UTF-8").read().replace("\\", "\\\\")
	#input(file_text)
	

#brauch ich eigentlich nicht, steht nichts drinne
prj_files = [os.path.join(path, file) for path, dirs, files in toolbox_folder for file in files  if file[-3:] == "prj"]	
project_file = prj_files[0]


#das sind dann die Dateien, aus denen tatsächlich Informationen extrahiert werden
databases = [[file, open(file, "r", encoding="UTF-8").readlines()[0].split(" ", 4)[4].strip()] for file in other_files] #Bsp.: "\_sh v3.0  621  Text". Wichtig: doppelte Leerzeichen
db_files = [tuple for tuple in databases if tuple[1] != "Text"]
text_files = [tuple for tuple in databases if tuple[1] == "Text"]




#wird verwendet, um alle Datenbanken, ob Text- oder Wörterbuch, einzulesen
def decode_toolbox_map(string, marker):
	def next_block(string, marker):
		if marker in string:
			this_line = re.search("\\\\({}) ?(.+?)?\n".format(marker), string)
			
			this_annotation = this_line.group(2)
		else:
			return
		
		if "mkrFollowingThis" in markers[marker]:
			new_marker = markers[marker]["mkrFollowingThis"]
		else:
			#print(marker, this_annotation, "$")
			return 
		
		if not "jumps" in markers[marker]: #ich verwende das vorhandensein von Lookup-Funktionen als Indikator dafür, dass wir es nicht mit einem Id- oder Record-Marker zu tun haben, sondern mit einem zu interlinearisierenden Eintrag. Das setzt voraus, dass auch in den Datenbanken solche Lookup-Funktionen beim höchsten Eintrag angesetzt werden, ansonsten werden die Wörterbucheinträge nicht interlinearisiert dargestellt
			aaa = {marker : {}}
			
			new_subset = re.split("(?V1)(?=\\\\{})".format(marker), string)
			for sub_string in new_subset[1:]:
				if marker in sub_string:
					this_line = re.search("\\\\({}) ?(.+?)?\n".format(marker), sub_string)
					
					this_annotation = this_line.group(2)
				else:
					return
				
				map = next_block(sub_string, new_marker)
				aaa[marker][this_annotation] = map
			
			return aaa
		else:
			aaa = []
			
			new_subset = re.split("(?V1)(?=\\\\{})".format(marker), string)
			for sub_string in new_subset[1:]:
				aaa.append(next_line(sub_string, marker))
			
			return aaa
		
	def next_line(string, marker):
		def get_line(string, marker):
			if re.search("\\\\({}) ?(.+?\n)?".format(marker), string):
				this_line = re.search("\\\\({}) ?(.+?\n)?".format(marker), string)
				this_annotation = this_line.group(2)
				
				return {marker : this_annotation}
			else:
				return {marker : ""}
		
		if "mkrFollowingThis" in markers[marker]:
			new_marker = markers[marker]["mkrFollowingThis"]
		else: #der letzte Marker ist die Übersetzung
			return get_line(string, marker)
		
		nnn = next_line(string, new_marker)
		ttt = get_line(string, marker)
		
		ttt.update(nnn)
		
		return ttt
		
	return next_block(string, marker)

#hier werden die Wörterbücher geladen, damit in Realtime verglichen werden kann, was konsistent ist und was nicht
db_words = {}
for db_file in db_files:
	file_path, typ = db_file[0], db_file[1]
	
	with open(file_path, "r", encoding="UTF-8") as file:
		
		file_text = file.read()
		if not file_text[-1] == "\n":
			file_text += "\n"
		
		if not typ in types:
			continue
			
		root_marker = types[typ][0]["mkrRecord"]
		markers = types[typ][0]["markers"][0]
		
		map = decode_toolbox_map(file_text, root_marker)
		
		if map:
			pd = pandas.DataFrame.from_records(map)
			dpl = pd[pd.duplicated(keep='first')]
			if not dpl.empty:
				print(typ, "has duplicates:") 
				print(dpl.to_string())
			
				input("press enter to continue")
			
		db_words[typ] = map

		
#hiermit werden die Text-Datenbanken gelesen
words = []
log = []
def decode_toolbox_json(map, marker, prefix):	#prefix = { marker : marker_value }	 (fName, id, rec)
	global words, log
	def get_index_of_marker(marker, table):
		markers_ = [item[0] for item in table]
		return markers_.index(marker) if marker in markers_ else None
	
	#macht aus dem json-Objekt ein Tabellen-Objekt
	def decode_alignment(map, marker):
		if "mkrFollowingThis" in markers[marker]:
			new_marker = markers[marker]["mkrFollowingThis"]
		else:
			return [[marker, bytes(map[marker], encoding="UTF-8")]] if map[marker] else None
		
		next_line = decode_alignment(map, new_marker)
		
		if next_line:
			this_line = [marker, bytes(map[marker], encoding="UTF-8")]
			
			next_line.append(this_line)
			
			return next_line
		else:
			return [[marker, bytes(map[marker], encoding="UTF-8")]] if map[marker] else None
		#print
	
	def decode_words(marker, table, prefix, min=0, yy=-1): #check von min bis xx
		current_index = get_index_of_marker(marker, table)
		if current_index is None:
			return []
		
		if current_index < len(table):
			current_row = table[current_index][1]
		else:#kann eigentlich weg
			print(marker, current_index, "\n\n")
			for row in table:
				continue
				print(row)
		
			input()
			return []
		
		xx_ = min
		if yy != -1:
			max = yy 
			#print(marker, max, current_row[max:max+1])
			if max < len(current_row):
				if current_row[max] == 32 and "jumps" in markers[marker]:
					#print("#", min, max, current_row[min:max+1], current_row)
					return None
		else:
			max = len(current_row)
		
		
		if min > 0 and min < len(current_row):
			if current_row[min-1] != 32:
				#wenn das Zeichen (in einem rekursiven Aufruf der Funktion mit bestimmtem min und max) vor dem min kein Leerzeichen ist, können die Zeilen nicht aliniert sein. Deswegen gehen wir vorsichtshalber weiter (→ if following_words == None)
				return None
		
		
		spalten = []
		if "jumps" in markers[marker]:
			
			found = False
			for xx in range(min, max):
				if xx >= len(current_row):
					#input()
					#print(marker, min, max, xx, current_row[xx], current_row[xx+1])
					break
				
				cond2 = xx == len(current_row)-1
				#das Ende der Zeile bedeutet auch das Ende eines Wortes, aber die Zeilen sind nicht notwendigerweise gleich lang, weswegen ein anderer Funktionsaufruf benötigt wird
				cond1 = current_row[xx] == 32 and current_row[xx+1] != 32 if not cond2 else False
				#das Ende von Leerzeichen bedeutet das Ende eines Wortes
				
				
				if cond1 or cond2:
					found = True
					
					#hier wird der Eintrag aus der Annotation in die Datenbank eingetragen, strip(" ") um den Zeilenumbruch am Ende zu behalten. Dasselbe gilt aber auch für die Wörterbücher, wo folglich bei jedem Eintrag \n-chars verbleiben
					current_word = {marker : current_row[xx_:xx+1].decode("UTF-8").strip()} if cond1 else {marker : current_row[xx_:].decode("UTF-8").strip(" ")}
					
					#print(cond1, cond2)
					#print(current_word)
					
					
					zeilen = []
					for jump in markers[marker]["jumps"]:
						next_marker = jump["mkrTo"]
						
						following_words = decode_words(next_marker, table, prefix, xx_, xx+1) if cond1 else decode_words(next_marker, table, prefix, xx_)
						
						if following_words == None:
							break
							#Es wird nur None zurückgegeben, wenn bei der Alinierung ein Leerzeichen nicht über einem anderen Leerzeichen steht. Das deutet auf eine Spannenannotation in der folgenden Zeile, daher wird die for-Schleife gebrochen und die Zählung xx_ = xx+1 nicht ausgelöst, es wird also bis zum nächsten Leerzeichen gesucht
						
						if following_words == []:
							#log.append({**prefix, **current_word})
							#hier sollte an allen Stellen gemeckert werden, wo die Annotation entweder fehlerhaft ist oder fehlt
							continue
							#andere Möglichkeit: beim Überprüfen der Konsistenz loggen
							
						following_words = [[following_words[i][y] for i in range(len(following_words))] for y in range(len(following_words[0]))]
						
						for word in following_words:
							zeilen.append(word)
						
					else: #folgendes wird nicht aufgeführt, wenn zuvor None zurückgegeben wurde
						#das Array muss symmetrisch sein, damit es rotiert werden kann, das wird durch Verdopplung erreicht. Verdopplung heißt aber, dass eine Spannenannotation vorliegt, wodurch '@' vorgeschaltet werden muss
						for zz in reversed(range(len(zeilen))):
							if len(zeilen[zz-1]) < len(zeilen[zz]):
								to_append = deepcopy(zeilen[zz-1])[-1]
								
								for key in zeilen[zz-1][-1]:
									zeilen[zz-1][-1][key] = '@' + zeilen[zz-1][-1][key]
									break #idR muss nur der erste Eintrag markiert werden
								
								zeilen[zz-1].append(to_append)
								#Python verweist auf Elemente stets mit Referenzen. Wenn hier keine Kopie eingesetzt wird, werden im Folgenden beim Merging der dictionaries alle Einträge gleich verändert
						
						if zeilen == []:
							if cond2: #wenn am Ende der Zeile immer noch keine Annotationen gefunden wurden, ist die gnaze Zeile leer und wird ohne Annotation in die Datenbank aufgenommen
								spalten.append([current_word])
								
							continue
							
						zeilen = [[zeilen[i][y] for i in range(len(zeilen))] for y in range(len(zeilen[0]))]
						
						
						for zz in range(len(zeilen)):
							zeile = zeilen[zz]
							
							if len(zeilen) > 1 and zz < len(zeilen) - 1: 
								zeile.append({key : "@" + current_word[key] for key in current_word})
								#mit einem @ am Anfang werden Spannenannotationen markiert, damit sie später wieder zusammengesetzt werden können, das letzte wird dabei ausgelassen um das Ende zu markieren (wichtig bei Zeilenumbrüchen)
							else:
								zeile.append(current_word)
							
							for i in range(len(zeile)):
								zeile[0].update(zeile[i])
							
							zeile = [zeile[0]] #für logging reasons (???)
							spalten.append([zeile[0]])
							
						
					
						xx_ = xx+1
			if not found:
				if min < yy:
					return None #wenn er von vorne bis hinten durchgegangen ist, ohne das cond1 oder cond2 gegriffen haben, muss ein Fehler in der Alignierung vorliegen. Deswegen geht es weiter (→ if following_words == None)
				elif min > yy:
					return [] #wenn er gar nicht erst durch die Schleife durchgehen konnte, dann weil die Zeile zu kurz ist. Das passiert, wenn das letzte Wort der Mutter-Zeile gar keine Annotation hat.
		else:
			current_word = {marker : current_row[min:max].decode("UTF-8").strip()} if yy != -1 else {marker : current_row[min:].decode("UTF-8").strip()}
			spalten.append([current_word])
			
		for spalte in spalten:
			for word in spalte:
				word.update(prefix)
		
		#input(spalten)
		
		return spalten if spalten != [] else []
	
	#ich glaube das brauche ich gar nicht
	if "mkrFollowingThis" in markers[marker]:
		new_marker = markers[marker]["mkrFollowingThis"]
	else:
		return
		
	if not "jumps" in markers[marker]: #vgl. oben. mit dem Vorhandensein wird zwischen Id- und Record-Markern und zu interlinearisierenden Einträgen unterschieden. Bei den Text-Datenbanken ist das nativ von Toolbox vorgesehen
		for element in map[marker]: #dictionarys für Knoten
			if not element is None:
				prefix.update({marker : element})
				decode_toolbox_json(map[marker][element], new_marker, prefix)
		
	else:
		for element in map: #listen für Inhalte
			
			table = decode_alignment(element, marker)
			if table is None:
				continue
			
			
			for word in decode_words(marker, table, prefix):
				
				for dict in word:
					#wenn die Wörter hier korrigiert werden, wird die Laufzeit um mehrere Stunden verkürzt
					words.extend(check_word_for_consistency(dict, marker))

#gibt bei geladenen Wörterbüchern das korrigierte Wort zurück. Wenn die Annotationen eindeutig sind, werden sie automatisch aufgefüllt, wenn nicht, bleiben sie unangetastet
spannenindex = {}		
def check_word_for_consistency(word, marker):
	def check_word_for_consistency_(word, marker):
		global spannenindex
		if not marker in spannenindex:
			spannenindex.update({marker : 0})
		
		def strip_plus(string):
			if string is not None:
				return string.strip('@').strip() #doppeltes Strip wegen Spannenannotation und \n-Markern
			else:
				return None
			
			
		#diese Funktion läuft durch alle Marker, die Teil einer jump-Funktion sind, also die erste Zeile in einer Datenbank sind
		#print(marker + " " + str(word[marker]) + " " + str(word))
		for jump in markers[marker]["jumps"]:
			jumpFrom = jump["mkr"]
			jumpTo = jump["mkrTo"]
			jumpToDb = jump["dbtyp"]
			jumpOut = jump["mkrOut"]
			
			word[marker] = word[marker].replace(" ", " ") #für den Import in ANNIS müssen Zeilenzusammenrückungen durch Nobreak-Spaces gelöst werden. Da nur jump-Marker in dieser Funktion durchgenommen werden, wird die Integrität der Toolboxdateien nicht gefährdet.
			
			#strip(), weil in der Datenbank überall und in der Annotationsdatei an Zeilenumbrüchen noch \n-chars sind
			db_words_ = [db_word for db_word in db_words[jumpToDb] if strip_plus(db_word[jumpFrom]) == strip_plus(word[marker])]
			
			database_annotations = [db_word[jumpOut].strip() for db_word in db_words_ if db_word[jumpOut] is not None]
			database_annotations = [ann for gloss in database_annotations for ann in gloss.split(jump['GlossSeparator'])]
			if "jumps" in markers[jumpTo]:
				database_annotations = [gloss.split() for gloss in database_annotations]
				#für alle Datenbankeinträge: in allen durch den GlossSeparator abgetrennten Glossen: alle durch Leerzeichen getrennten Teilwörtern sind eligible für die Interlinearisierung auf der nächsten Zeile
			else:
				database_annotations = [[gloss] for gloss in database_annotations]
				#bei Zeilen, die nicht weiter segmentiert werden, sind die Leerzeichen Teil des Annotationswertes und dürfen nicht gesplittet werden
			
			#print(database_annotations)
			#print(jumpTo, jumpTo in word, any(strip_plus(word[jumpTo]) in dba for dba in database_annotations))
			
			if len(database_annotations) == 1:
				if spannenindex[marker] >= len(database_annotations[0]):
					from_database = database_annotations[0][-1]
					log.append({**{"tofix" : "possible duplicate"}, **word})
					print("possible duplicate: ", database_annotations[0], marker, spannenindex[marker], str(word))
					
				else:
					from_database = database_annotations[0][spannenindex[marker]]
					
				if not jumpTo in word:
					word.update({jumpTo : from_database})
					log.append({**{"fixed" : jumpTo}, **word})
				elif not any(strip_plus(word[jumpTo]) in dba for dba in database_annotations):
					
					word[jumpTo] = from_database
					log.append({**{"fixed" : jumpTo}, **word})
				else:
					if word[jumpTo][-1] == "\n":
						word[jumpTo] = word[jumpTo][:-1]
						
			else:
				if not jumpTo in word:
					log.append({**{"tofix" : jumpTo + ": " + str(database_annotations)}, **word})
					return word
				elif not any(strip_plus(word[jumpTo]) in dba for dba in database_annotations):
					log.append({**{"tofix" : jumpTo}, **word})
			
			if len(word[marker]):
				if word[marker][0] == '@':
					spannenindex[marker] += 1
				elif word[marker][0] != '@' and spannenindex[marker] != 0:
					#print(spannenindex, word)
					for marker in spannenindex:
						spannenindex[marker] = 0
			else:
				print("what?", word)
			
			if "jumps" in markers[jumpTo]:
				word = check_word_for_consistency_(word, jumpTo)	
		
		return word
	def automatically_annotate(word, marker):
		list = []
		for splitt in word[marker].split(" "):
			new_word = word.copy()
			new_word[marker] = splitt
			list.append(check_word_for_consistency_(new_word, marker))
		
		return list
	
	if len(word) > 4: #fName, id, ref, tx → keine Annotationen
		return [check_word_for_consistency_(word, marker)]
	else:
		return automatically_annotate(word, marker)

#bring the action
for text_file in text_files[1:2]: 
	file_path, typ = text_file[0], text_file[1]
	with open(file_path, "r", encoding="UTF-8") as file:
		print(file_path)
		
		file_text = file.read()
		if not file_text[-1] == "\n":
			file_text += "\n"
		
		root_marker = types[typ][0]["mkrRecord"]
		markers = types[typ][0]["markers"][0]
		
		map = decode_toolbox_map(file_text, root_marker)
		
		filename = os.path.basename(file_path)
		filename = filename[:-4] if ".txt" in filename else filename
		decode_toolbox_json(map, root_marker, { "fName" : filename})
			
def list_to_toolbox(words, root_marker):
	def repl(m):
		return " " * len(m.group())
	def last_char_after_strip(string, char):
		string = string.strip(" ")
		if len(string) > 0:
			if string[-1] == char:
				return True
		return False
	
	current_block = {}
	in_spann = {}
	def compose_block(word, marker):
		new_block = {}
		
		while True:
			new_block[marker] = bytes(word[marker], encoding="UTF-8") if marker in word else b''
			if "mkrFollowingThis" in markers[marker]:
				marker = markers[marker]["mkrFollowingThis"]
			else:
				break
		
		target_length = len(max(new_block.values(), key=len)) + 1 #wir brauchen ein Leerzeichen als Trenner
		
		for key in new_block:
			if len(new_block[key]) > 0 and new_block[key][0:1] != b'@' or len(new_block[key]) == 0:
				
				if not key in in_spann:
					in_spann[key] = False
				
				new_value = new_block[key]
				new_value += b' ' * (target_length-len(new_value))
				new_value = new_value.decode("UTF-8")
				
			elif len(new_block[key]) > 0 and new_block[key][0:1] == b'@':
				new_value = b'@' * target_length
				new_value = new_value.decode("UTF-8")
				
				if not key in in_spann:
					in_spann[key] = True
					
			if not key in current_block:
				current_block[key] = new_value
			else:
				current_block[key] += new_value
			
	def dict_to_text(dict):
		string = ""
		for key in dict:
			if not dict[key] == "":
				string += "\\" + key + " " + dict[key].strip() + "\n"
				dict[key] = ""
		
		if string == "":
			return ""
		
		#string += "\n"
		
		#Spannenannotation werden aufgelöst
		string = re.sub("(@+)([^ \@\n]+)", "\g<2>\g<1>", string)
		string = re.sub("@+", repl, string)
			
		return string
		
	def current_file_path():
		path = os.path.join(os.path.basename(toolbox_folder_path), current_file_name + ".txt")
		#path = os.path.join(toolbox_folder_path, current_file_name + "_ed.txt")
		return path
	current_file_name = ""
	current_file_content = "\\_sh v3.0  621  Text\n"
	
	current_record = {}
	for entry in words:
		if current_file_name == "":
			current_file_name = entry["fName"]
		elif entry["fName"] != current_file_name:
			open(current_file_path(), "w", encoding="utf-8").write(current_file_content)
			print(current_file_name + " written")
			
			current_file_name = entry["fName"]
			current_file_content = "\\_sh v3.0  621  Text\n"
		
		marker = root_marker
		while "mkrFollowingThis" in markers[marker]: #iteriert durch die Spalten id und ref, solange bis die Annotation erreicht ist
			if not "jumps" in markers[marker]: #id und ref
				if not marker in current_record:
					current_record.update({marker : entry[marker]})
					current_file_content += "\n\\" + marker + " " + entry[marker] + "\n"
				else:
					if current_record[marker] != entry[marker]:
						current_file_content += dict_to_text(current_block)
					
						current_file_content += "\n\\" + marker + " " + entry[marker] + "\n"
						current_record[marker] = entry[marker]
						
			
				marker = markers[marker]["mkrFollowingThis"]
			else: #Annotation ist erreicht, neues Protokoll
				compose_block(entry, marker)
				
				if last_char_after_strip(current_block[marker], "\n"):
					current_file_content += dict_to_text(current_block)
				
				break #die restlichen Spalten wurden ja schon in der compose_block Funktion durchiteriert
	
	###
	#scheint obsolet zu sein
	###
	current_file_content += dict_to_text(current_block)
	
	open(current_file_path(), "w", encoding="utf-8").write(current_file_content)
	print(current_file_name + " written")

if reexport:	
	list_to_toolbox(words, root_marker)

pd = pandas.DataFrame.from_records(words)
pd = pd.replace(r'\n','', regex=True) 
pd.to_csv(out_path, sep=';', encoding="UTF-8-SIG", index=False, header=True)

pd = pandas.DataFrame.from_records(log)
pd = pd.replace(r'\n','', regex=True)
print("\nlength of log:")
print(pd["fName"].value_counts())
pd.to_csv(log_path, sep=';', encoding="UTF-8-SIG", index=False, header=True)

print(len(words))		
			