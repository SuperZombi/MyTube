import os
import yt_dlp
import tempfile
from datetime import datetime
from .utils import Channel, Thumbnail
from .utils import convert_to_netscape
from .streams_manager import StreamsManager
from .subtitles import SubtitlesManager
from .downloader import Downloader



class YouTube:
	def __init__(self, link, cookies:list=None):
		self.link = link
		self._url = ""
		self._vid_info = None
		self._formats = None

		self.cookies = cookies
		self.cookie_file = None

		if self.cookies:
			self._cookies_netscape = convert_to_netscape(self.cookies)
			self.cookie_file = tempfile.TemporaryFile(suffix=".txt", delete=False).name
			with open(self.cookie_file, 'w') as f:
				f.write(self._cookies_netscape)

		options = {
			'quiet': True,
			'noplaylist': True,
			"no_warnings": True,
			"cookiefile": self.cookie_file
		}
		with yt_dlp.YoutubeDL(options) as ydl:
			self._vid_info = ydl.extract_info(self.link, download=False)
			self._url = self._vid_info.get("webpage_url")

		if self.cookie_file and os.path.exists(self.cookie_file): os.remove(self.cookie_file)

	def __str__(self):
		return f'MyTube({self.videoId})'
	def __repr__(self):
		return f'MyTube({self.videoId})'

	@property
	def videoId(self) -> str:
		return str(self._vid_info.get("id"))
	
	@property
	def title(self) -> str:
		return str(self._vid_info.get("title"))

	@property
	def author(self) -> str:
		trash = " - Topic"
		channel_name = self._vid_info.get("channel")
		if channel_name.endswith(trash):
			channel_name = channel_name[:-len(trash)]
		return str(channel_name)

	@property
	def type(self) -> str:
		'''"video" or "music"'''
		if any(e.lower() == "music" for e in self._vid_info.get("categories")):
			return "music"
		if "music.youtube" in self.link:
			return "music"
		return "video"

	@property
	def description(self) -> str:
		return str(self._vid_info.get("description"))

	@property
	def duration(self) -> int:
		"""Duration in seconds"""
		return int(self._vid_info.get("duration"))

	@property
	def views(self) -> int:
		"""Views count"""
		return int(self._vid_info.get("view_count"))
	
	@property
	def likes(self) -> int:
		"""Likes count"""
		return int(self._vid_info.get("like_count"))
	
	@property
	def comments(self) -> int:
		"""Comments count"""
		return int(self._vid_info.get("comment_count"))
	
	@property
	def thumbnail(self) -> Thumbnail:
		return Thumbnail(self._vid_info.get("thumbnail"))

	@property
	def upload_date(self) -> datetime:
		ts = int(self._vid_info.get("timestamp"))
		return datetime.utcfromtimestamp(ts)

	@property
	def subtitles(self) -> SubtitlesManager:
		return SubtitlesManager(self._vid_info.get("subtitles"))

	@property
	def streams(self) -> StreamsManager:
		self._formats = self._vid_info.get('formats', [])
		streamsManager = StreamsManager()
		streamsManager.parse(self._formats, metadata=self.metadata)
		return streamsManager

	@property
	def metadata(self) -> dict:
		return {
			"title": self.title,
			"author": self.author,
			"thumbnail": self.thumbnail
		}

	@property
	def channel(self) -> Channel:
		id = self._vid_info.get("channel_id")
		url = self._vid_info.get("channel_url")
		name = self.author
		followers = int(self._vid_info.get("channel_follower_count"))
		return Channel(id=id, url=url, name=name, followers=followers)

	def download(self, video=None, audio=None, metadata=None) -> Downloader:
		return Downloader(video, audio, (metadata or self.metadata))
