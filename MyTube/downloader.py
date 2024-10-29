# import requests
from .stream import Stream
from .utils import get_file_path
import aiohttp
# import asyncio
import tempfile


class Downloader:
	def __init__(self, video:Stream=None, audio:Stream=None, metadata:dict=None):
		self.videoStream = video if (video and (video.isVideo or video.isMuxed)) else None
		self.audioStream = audio if (audio and audio.isAudio) else None
		self.metadata = metadata or {}
		self.CHUNK_SIZE = 10*1024*1024
		self.HEADERS = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
			"Accept-Language": "en-US,en"
		}


	async def __call__(self,
		output_folder:str=None,
		filename:str=None,
		on_progress=None
	):
		if self.videoStream:
			extension = self.videoStream.videoExt
		elif self.audioStream:
			extension = self.audioStream.audioExt

		target_filepath = get_file_path(
			filename=filename or self.metadata.get("title", ""),
			prefix=extension,
			folder=output_folder
		)

		on_progress = on_progress or (lambda x,y:None)

		if self.videoStream and self.audioStream:
			filesize = self.videoStream.filesize + self.audioStream.filesize
			async def progressOne(current, total):
				await on_progress(current, filesize)
			async def progressTwo(current, total):
				await on_progress(self.videoStream.filesize+current, filesize)

			print("Downloading video", self.videoStream.filesize)
			videofile = tempfile.TemporaryFile(suffix=f'.{self.videoStream.videoExt}',delete=False).name
			await self._download_stream(self.videoStream.url, videofile, progressOne)

			print("Downloading audio", self.audioStream.filesize)
			audiofile = tempfile.TemporaryFile(delete=False).name
			await self._download_stream(self.audioStream.url, audiofile, progressTwo)

			print(videofile)
			print(audiofile)


		# elif self.videoStream:
		# 	filesize = self.videoStream.filesize
		# 	print("Downloading video")
		# 	filename = tempfile.TemporaryFile(suffix=f".{self.videoStream.videoExt}", delete=False).name
		# 	await self._download_stream(self.videoStream.url, filename)
		# 	return filename



	async def _download_stream(self, url, filename, on_progress=None):
		on_progress = on_progress or (lambda x,y:None)
		async with aiohttp.ClientSession(headers=self.HEADERS) as session:
			async with session.get(url) as resp:
				file_size = int(resp.headers.get('Content-Length', 0))
				with open(filename, "wb") as file:
					downloaded = 0
					async for chunk in resp.content.iter_chunked(self.CHUNK_SIZE):
						file.write(chunk)
						downloaded += len(chunk)
						await on_progress(downloaded, file_size)
					# while True:
					# 	chunk = await response.content.read(self.CHUNK_SIZE)
					# 	if not chunk: break
					# 	file.write(chunk)
					# 	downloaded += len(chunk)
					# 	await on_progress(downloaded, file_size)




		# response = requests.get(url, stream=True)
		# file_size = int(response.headers.get('content-length', 0))
		# print(f"File size: {file_size}")

		# with open(filename, "wb") as file:
		# 	for chunk in response.iter_content(self.CHUNK_SIZE):
		# 		if chunk:
		# 			file.write(chunk)
		# 			print(f"Downloaded {file.tell()} / {file_size}")
