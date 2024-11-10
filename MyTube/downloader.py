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
		self.can_download = True
		self.CHUNK_SIZE = 10*1024*1024
		self.HEADERS = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
			"Accept-Language": "en-US,en"
		}
		self.FFMPEG = "ffmpeg"
		self._DURATION_REG = re.compile(
			r"Duration: (?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})"
		)
		self._TIME_REG = re.compile(
			r"time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})"
		)

	async def _default_progress(self, current, total): return

	def abort(self):
		self.can_download = False

	async def __call__(self,
		output_folder:str=None,
		filename:str=None,
		video_ext:str=None,
		audio_ext:str="mp3",
		add_audio_metadata:bool=True,
		on_progress=None,
		ffmpeg_progress=None
	) -> str:
		if self.videoStream:
			extension = self.videoStream.videoExt
			prefer_ext = video_ext or extension
		elif self.audioStream:
			extension = self.audioStream.audioExt
			prefer_ext = audio_ext or extension

		target_filename = filename or self.metadata.get("title", "")
		target_filepath = get_file_path(
			filename=target_filename, prefix=extension, folder=output_folder
		)
		filepath_prefer = get_file_path(
			filename=target_filename, prefix=prefer_ext, folder=output_folder
		)
		return_file = target_filepath

		on_progress = on_progress or self._default_progress
		ffmpeg_progress = ffmpeg_progress or self._default_progress

		if self.videoStream and self.audioStream:
			filesize = self.videoStream.filesize + self.audioStream.filesize
			async def progressOne(current, total):
				await on_progress(current, filesize)
			async def progressTwo(current, total):
				await on_progress(self.videoStream.filesize+current, filesize)

			videofile = tempfile.TemporaryFile(delete=False).name
			audiofile = tempfile.TemporaryFile(delete=False).name

			if self.can_download:
				await self._download_stream(self.videoStream.url, videofile, progressOne)

			if self.can_download:
				await self._download_stream(self.audioStream.url, audiofile, progressTwo)

			if self.can_download:
				if extension != prefer_ext:
					await self._mix(videofile, audiofile, filepath_prefer, ffmpeg_progress, v_copy=False)
					return_file = filepath_prefer
				else:
					await self._mix(videofile, audiofile, target_filepath, ffmpeg_progress)
			
			os.remove(videofile)
			os.remove(audiofile)
			return return_file


		elif self.videoStream:
			if extension != prefer_ext:
				videofile = tempfile.TemporaryFile(delete=False).name
				await self._download_stream(self.videoStream.url, videofile, on_progress)
				await self._convert(videofile, filepath_prefer, ffmpeg_progress)
				os.remove(videofile)
				return_file = filepath_prefer
			else:
				await self._download_stream(self.videoStream.url, target_filepath, on_progress)
			return return_file

		elif self.audioStream:
			if extension != prefer_ext:
				audiofile = tempfile.TemporaryFile(delete=False).name
				await self._download_stream(self.audioStream.url, audiofile, on_progress)
				if add_audio_metadata:
					await self._convert(audiofile, filepath_prefer, ffmpeg_progress, self.metadata)
				else:
					await self._convert(audiofile, filepath_prefer, ffmpeg_progress)
				os.remove(audiofile)
				return_file = filepath_prefer
			else:
				await self._download_stream(self.audioStream.url, target_filepath, on_progress)
			return return_file



	async def _mix(self, video, audio, target, progress=None, v_copy=True):
		if os.path.exists(target): os.remove(target)
		codecs = []
		if target.endswith(".mp4") or target.endswith(".m4a"):
			if v_copy:
				codecs.extend(["-c:v", "copy"])
			codecs.extend(["-c:a", "libmp3lame"])
		else:
			codecs.extend(["-c:v", "copy"])
		await self._ffmpeg(["-i", video, "-i", audio, *codecs, target], progress)


	async def _convert(self, inputFile, output, progress=None, metadata=None):
		if os.path.exists(output): os.remove(output)
		codecs = []
		need_detele_thrumb = False
		if output.endswith(".mp3"):
			if metadata:
				if metadata.get('thumbnail'):
					thumb = metadata.get('thumbnail').temp
					need_detele_thrumb = True
					codecs.extend(["-i", thumb, "-map", "0:0", "-map", "1:0"])
				codecs.extend(["-ar", "48000", "-b:a", "192k"])
				if metadata.get('title'):
					title = metadata.get('title').replace('"', '')
					codecs.extend(["-metadata", f"title={title}"])
				if metadata.get('author'):
					artist = metadata.get('author').replace('"', '')
					codecs.extend(["-metadata", f"artist={artist}"])
				codecs.extend(["-id3v2_version", "3"])
				
		await self._ffmpeg(["-i", inputFile, *codecs, output], progress)
		if need_detele_thrumb: os.remove(thumb)


	async def _download_stream(self, url, filename, on_progress=None):
		on_progress = on_progress or self._default_progress
		async with aiohttp.ClientSession(headers=self.HEADERS) as session:
			resp_head = await session.get(url)
			file_size = int(resp_head.headers.get('Content-Length'))
			downloaded = 0
			await on_progress(downloaded, file_size)
			with open(filename, "wb") as file:
				while downloaded < file_size:
					if self.can_download:
						stop_pos = min(downloaded + self.CHUNK_SIZE, file_size) - 1
						resp = await session.get(url + f"&range={downloaded}-{stop_pos}")
						chunk = await resp.content.read()
						if not chunk: break
						file.write(chunk)
						downloaded += len(chunk)
						await on_progress(downloaded, file_size)
					else: break


	async def _ffmpeg(self, command, on_progress=None):
		on_progress = on_progress or self._default_progress
		total_duration = 0
		if not self.can_download: return 1
		process = subprocess.Popen([self.FFMPEG, "-hide_banner"] + command, encoding=os.device_encoding(0), universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		with process.stdout as pipe:
			history = []
			for raw_line in pipe:
				if not self.can_download:
					process.terminate()
					process.wait()
					return 1
				line = raw_line.strip()
				history.append(line)
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
		process.wait()
		if process.returncode != 0:
			print("\n".join(history))
			raise RuntimeError(f"FFMPEG error occurred: [{history[-1]}]")
		return process.returncode
