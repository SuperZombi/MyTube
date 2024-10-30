import os
import re
import aiohttp
import tempfile
import subprocess
from .utils import get_file_path, to_seconds


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
		self._DURATION_REG = re.compile(
			r"Duration: (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})"
		)
		self._TIME_REG = re.compile(
			r"time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})"
		)

	async def _default_progress(self, current, total): return

	async def __call__(self,
		output_folder:str=None,
		filename:str=None,
		on_progress=None,
		ffmpeg_progress=None
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

		on_progress = on_progress or self._default_progress
		ffmpeg_progress = ffmpeg_progress or self._default_progress

		if self.videoStream and self.audioStream:
			filesize = self.videoStream.filesize + self.audioStream.filesize
			async def progressOne(current, total):
				await on_progress(current, filesize)
			async def progressTwo(current, total):
				await on_progress(self.videoStream.filesize+current, filesize)

			videofile = tempfile.TemporaryFile(delete=False).name
			await self._download_stream(self.videoStream.url, videofile, progressOne)

			audiofile = tempfile.TemporaryFile(delete=False).name
			await self._download_stream(self.audioStream.url, audiofile, progressTwo)

			await self._mix(videofile, audiofile, target_filepath, ffmpeg_progress)

			os.remove(videofile)
			os.remove(audiofile)
			return target_filepath


		elif self.videoStream:
			await self._download_stream(self.videoStream.url, target_filepath, on_progress)
			return filename

		elif self.audioStream:
			await self._download_stream(self.audioStream.url, target_filepath, on_progress)
			return filename



	async def _mix(self, video, audio, target, progress=None):
		if os.path.exists(target): os.remove(target)
		await self._ffmpeg(["ffmpeg", "-hide_banner", "-i", video, "-i", audio, target], progress)


	async def _download_stream(self, url, filename, on_progress=None):
		on_progress = on_progress or self._default_progress
		async with aiohttp.ClientSession(headers=self.HEADERS) as session:
			resp_head = await session.head(url)
			file_size = int(resp_head.headers.get('Content-Length'))
			downloaded = 0
			await on_progress(downloaded, file_size)
			with open(filename, "wb") as file:
				while downloaded < file_size:
					stop_pos = min(downloaded + self.CHUNK_SIZE, file_size) - 1
					resp = await session.get(url + f"&range={downloaded}-{stop_pos}")
					chunk = await resp.content.read()
					if not chunk: break
					file.write(chunk)
					downloaded += len(chunk)
					await on_progress(downloaded, file_size)


	async def _ffmpeg(self, command, on_progress=None):
		on_progress = on_progress or self._default_progress
		total_duration = 0
		process = subprocess.Popen(command, encoding=os.device_encoding(0), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		with process.stdout as pipe:
			for raw_line in pipe:
				line = raw_line.strip()
				if total_duration == 0:
					if "Duration:" in line:
						match = self._DURATION_REG.search(line)
						total_duration = to_seconds(match.groupdict())
						await on_progress(0, total_duration)
				else:
					if "time=" in line:
						match = self._TIME_REG.search(line)
						if match:
							current = to_seconds(match.groupdict())
							await on_progress(current, total_duration)
		return process.wait()
	