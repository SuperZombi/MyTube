import os
import yt_dlp
from .utils import Channel
from .utils import get_cookie_file

class CommentsManager:
	def __init__(self, link, count, cookies=None):
		self.link = link
		self.count = count
		self.cookies = cookies
		self.data = []
	def __str__(self): return f"Comments({self.count})"
	def __len__(self): return self.count
	async def get(self) -> list:
		if not self.data:
			cookie_file = get_cookie_file(self.cookies) if self.cookies else None
			options = {
				'quiet': True,
				'noplaylist': True,
				"no_warnings": True,
				"getcomments": True,
				'skip_download': True,
				"cookiefile": cookie_file
			}
			with yt_dlp.YoutubeDL(options) as ydl:
				_vid_info = ydl.extract_info(self.link, download=False)
				self.data = _vid_info.get("comments")
			if cookie_file and os.path.exists(cookie_file): os.remove(cookie_file)
		return list(map(lambda x: Comment(x, video_url=self.link), self.data))

class Comment:
	def __init__(self, args, video_url):
		self.args = args
		self.id = args.get("id")
		self.url = f"{video_url}&lc={args.get('id')}"
		self.text = str(args.get("text", ""))
		self.likes = int(args.get("like_count", 0))
		self.is_pinned = args.get("is_pinned", False)
		self._parent = "root" if args.get("parent") == "root" else f"{video_url}&lc={args.get('parent')}"
	
	def __str__(self): return self.text
	def __repr__(self): return f"Comment({self.id})"
	@property
	def author(self) -> Channel:
		id = self.args.get("author_id")
		url = self.args.get("author_url")
		name = self.args.get("author")
		return Channel(id=id, url=url, name=name)
