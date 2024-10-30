from .utils import get_file_path
import requests
# from tqdm import tqdm

class Stream:
	def __init__(self, itag:str, url:str, filesize:int, metadata:dict=None):
		self.itag = itag
		self.url = url
		self.filesize = filesize
		self.metadata = metadata or {}
		self.isVideo = False
		self.isAudio = False
		self.isMuxed = False

	def get(self, attribute_name, default=0):
		return getattr(self, attribute_name, default)

	@property
	def w(self): return self.width
	@property
	def h(self): return self.height
	@property
	def res(self): return min(self.height, self.width)
	
	def add_video_info(self,
		videoCodec:str,
		videoExt:str,
		width:int,
		height:int,
		fps:int
	):
		self.videoCodec = videoCodec
		self.videoExt = videoExt
		self.width = width
		self.height = height
		self.fps = fps
		self.isVideo = True

	def add_audio_info(self,
		audioCodec:str,
		audioExt:str,
		language:str,
		audioBitrate:int,
		audioSamplerate:int
	):
		self.audioCodec = audioCodec
		self.audioExt = audioExt
		self.language = language
		self.audioBitrate = audioBitrate
		self.audioSamplerate = audioSamplerate
		self.isAudio = True

	def add_muxed_info(self,
		videoCodec:str,
		videoExt:str,
		width:int,
		height:int,
		fps:int,
		audioCodec:str,
		language:str,
		audioSamplerate:int
	):
		self.videoCodec = videoCodec
		self.videoExt = videoExt
		self.width = width
		self.height = height
		self.fps = fps
		self.audioCodec = audioCodec
		self.language = language
		self.audioSamplerate = audioSamplerate
		self.isMuxed = True

	def __str__(self):
		if self.isVideo:
			return f"Video({self.width}x{self.height}.{self.videoExt} [{self.fps}fps] {self.videoCodec})"
		elif self.isAudio:
			return f"Audio({self.audioBitrate}.{self.audioExt}{' ['+self.language+']' if self.language else ''} {self.audioCodec})"
		elif self.isMuxed:
			return f"Muxed({self.width}x{self.height}.{self.videoExt} [{self.fps}fps]{' ['+self.language+']' if self.language else ''} {self.videoCodec}+{self.audioCodec})"
		else:
			return f"Stream(id={self.itag})"

	def __repr__(self):
		if self.isVideo:
			return f"Video({self.res}p)"
		elif self.isAudio:
			return f"Audio({self.audioBitrate}kbps)"
		elif self.isMuxed:
			return f"Muxed({self.res}p)"
		else:
			return f"Stream({self.itag})"


	def download(self,
		output_folder:str=None,
		filename:str=None,
		on_progress=None,
		on_complete=None
	) -> str:
		if self.isVideo or self.isMuxed:
			extension = self.videoExt
		elif self.isAudio:
			extension = self.audioExt

		file_path = get_file_path(
			filename=filename or self.metadata.get("title"),
			prefix=extension,
			folder=output_folder
		)


		bytes_remaining = self.filesize
		print(bytes_remaining)
		with open(file_path, "wb") as file:
			for chunk in self._stream(self.url):
				bytes_remaining -= len(chunk)
				file.write(chunk)
				print(bytes_remaining)




		# bytes_remaining = self.filesize
		# response = requests.get(self.url, stream=True)
		# with open(file_path, "wb") as handle:
		# 	# for data in tqdm(response.iter_content()):
		# 	for data in response.iter_content():
		# 		handle.write(data)


		# with open(file_path, "wb") as file:
		# 	try:
		# 		for chunk in request.stream(stream.url):
		# 			bytes_remaining -= len(chunk)
		# 			file.write(chunk)
		# 			if on_progress: await on_progress(stream, chunk, bytes_remaining)
		# 	except HTTPError as e:
		# 		if e.code != 404: raise

		# 		for chunk in request.seq_stream(stream.url):
		# 			bytes_remaining -= len(chunk)
		# 			file.write(chunk)
		# 			if on_progress: await on_progress(stream, chunk, bytes_remaining)

		
		# if on_complete:
		# 	on_complete(file_path)
		return file_path


	def _stream(self, url):
		CHUNK_SIZE = 10*1024*1024
		downloaded = 0
		file_size = self.filesize
		while downloaded < file_size:
			stop_pos = min(downloaded + CHUNK_SIZE, file_size) - 1
			response = requests.get(self.url + f"&range={downloaded}-{stop_pos}")
			chunk = response.content
			if not chunk: break
			downloaded += len(chunk)
			yield chunk
	