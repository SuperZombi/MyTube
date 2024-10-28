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
