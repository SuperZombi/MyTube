import re
import os

class YouTube_Channel:
	def __init__(self, id:str, url:str, name:str, followers:int):
		self.id = id
		self.url = url
		self.name = name
		self.followers = followers

	def __str__(self):
		return f'Channel({self.name})'
	def __repr__(self):
		return f'Channel({self.name})'

def safe_filename(s:str, max_length:int=255) -> str:
	ntfs_characters = [chr(i) for i in range(0, 31)]
	characters = [r'"',r"\#",r"\$",r"\%",r"'",r"\*",r"\,",r"\.",r"\/",r"\:",r'"',r"\;",r"\<",r"\>",r"\?",r"\\",r"\^",r"\|",r"\~",r"\\\\"]
	pattern = "|".join(ntfs_characters + characters)
	regex = re.compile(pattern, re.UNICODE)
	filename = regex.sub("", s)
	return filename[:max_length].rsplit(" ", 0)[0]

def get_file_path(filename, prefix, folder=""):
	filename = f"{safe_filename(filename)}.{prefix}"
	folder = os.path.abspath(folder) if folder else os.getcwd()
	path = os.path.join(folder, filename)
	os.makedirs(folder, exist_ok=True)
	return file_exists(path)

def file_exists(file:str) -> str:
	if os.path.exists(file):
		name, extension = os.path.splitext(file)

		match = re.search(r'\((\d+)\)$', name)
		if match:
			number = int(match.group(1)) + 1
			new_name = re.sub(r'\(\d+\)$', f'({number})', name)
		else:
			new_name = f"{name} (1)"
		return file_exists(new_name+extension)
	return file

def to_seconds(kwargs: dict) -> int:
	hour = int(kwargs.get("hour", 0))
	minute = int(kwargs.get("min", 0))
	sec = int(kwargs.get("sec", 0))
	return (hour*3600) + (minute*60) + sec
