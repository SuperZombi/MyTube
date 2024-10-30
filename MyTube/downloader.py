import os
import aiohttp
import tempfile
from .utils import get_file_path


class Downloader:
	def __init__(self, video:"Stream"=None, audio:"Stream"=None, metadata:dict=None):
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
	) -> str:
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

			print("Downloading video")
			videofile = tempfile.TemporaryFile(delete=False).name
			await self._download_stream(self.videoStream.url, videofile, progressOne)

			print("Downloading audio")
			audiofile = tempfile.TemporaryFile(delete=False).name
			await self._download_stream(self.audioStream.url, audiofile, progressTwo)

			print(videofile)
			print(audiofile)


		elif self.videoStream:
			print("Downloading video")
			await self._download_stream(self.videoStream.url, target_filepath, on_progress)
			return filename

		elif self.audioStream:
			print("Downloading audio")
			await self._download_stream(self.audioStream.url, target_filepath, on_progress)
			return filename



	async def _download_stream(self, url, filename, on_progress=None):
		on_progress = on_progress or (lambda x,y:None)
		async with aiohttp.ClientSession(headers=self.HEADERS) as session:
			resp_head = await session.head(url)
			file_size = int(resp_head.headers.get('Content-Length'))
			downloaded = 0
			with open(filename, "wb") as file:
				while downloaded < file_size:
					stop_pos = min(downloaded + self.CHUNK_SIZE, file_size) - 1
					resp = await session.get(url + f"&range={downloaded}-{stop_pos}")
					chunk = await resp.content.read()
					if not chunk: break
					file.write(chunk)
					downloaded += len(chunk)
					await on_progress(downloaded, file_size)
	