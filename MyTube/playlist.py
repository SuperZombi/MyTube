import os
import json
import subprocess
from .playlist_manager import PlaylistManager, PlaylistVideo, DeletedVideo
from .utils import Thumbnail, Channel
from .utils import get_cookie_file
from .errors import YoutubeDLError


class Playlist:
	def __init__(self, link, cookies:list=None, yt_dlp="yt-dlp"):
		self.link = link
		self._info = None
		self._videos = []
		self.cookies = cookies
		self.yt_dlp = yt_dlp
		cookie_file = get_cookie_file(cookies) if cookies else None
		cmd = [
			self.yt_dlp,
			"--quiet",
			"--flat-playlist",
			"--skip-download",
			"--no-warnings",
			*(["--cookies", cookie_file] if cookie_file else []),
			"--dump-single-json",
			link
		]
		process = subprocess.Popen(cmd, encoding='utf-8', universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
		stdout, stderr = process.communicate()
		if stderr: raise YoutubeDLError(stderr)
		self._info = json.loads(stdout)

		if cookie_file and os.path.exists(cookie_file): os.remove(cookie_file)
		if self._info.get('_type') != 'playlist': raise TypeError(f"[Not playlist]: {link}")

		for item in self._info.get('entries'):
			if not item.get('duration'):
				self._videos.append(DeletedVideo(link=item.get('url')))
			else:
				best_image = max(item.get('thumbnails'), key=lambda img: img['width']*img['height'])
				channel = Channel(
					id=item.get('channel_id'),
					url=item.get('channel_url'),
					name=item.get('channel')
				)
				self._videos.append(
					PlaylistVideo(
						title=item.get('title'),
						link=item.get('url'),
						duration=int(item.get('duration')),
						channel=channel,
						thumbnail=Thumbnail(best_image.get('url')),
						cookies=self.cookies,
						yt_dlp=self.yt_dlp
					)
				)

	@property
	def playlistId(self) -> str:
		return str(self._info.get('id'))
	@property
	def title(self) -> str:
		return str(self._info.get('title'))
	@property
	def description(self) -> str:
		return str(self._info.get('description'))
	
	@property
	def type(self):
		'''"private" or "public"'''
		return "private" if self._info.get('availability') == "private" else "public"

	@property
	def videos(self) -> PlaylistManager:
		return PlaylistManager([v for v in self._videos if isinstance(v, PlaylistVideo)])
	@property
	def raw_videos(self) -> list: return self._videos

	def __str__(self): return f"Playlist(«{self.title}»)"
	def __repr__(self): return str(self)
