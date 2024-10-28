class Stream:
	def __init__(self, format_id:str, url:str, filesize:int):
		self.format_id = format_id
		self.url = url
		self.filesize = filesize
		self.isVideo = False
		self.isAudio = False
		self.isMuxed = False

	def get(self, attribute_name, default=0):
		return getattr(self, attribute_name, default)

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
			return f"Stream(id={self.format_id})"

	def __repr__(self):
		if self.isVideo:
			return f"Video({self.height}p)"
		elif self.isAudio:
			return f"Audio({self.audioBitrate}kbps)"
		elif self.isMuxed:
			return f"Muxed({self.height}p)"
		else:
			return f"Stream({self.format_id})"



class StreamsManager:
	def __init__(self, videoId, streams:list=None):
		self.videoId = videoId
		self.streams = streams if streams else []

	def __str__(self): return f"StreamsManager({self.videoId})"
	def __repr__(self): return self.__str__()
	def __len__(self): return len(self.streams)
	def __iter__(self): return iter(self.streams)

	def parse(self, formats:list) -> None:
		for format in formats:
			if format.get('format_note') == 'storyboard': continue
			if format.get('protocol') == "m3u8_native": continue

			allow_append = True
			stream = Stream(
				format_id=str(format.get('format_id')),
				url=format.get('url'),
				filesize = int(format.get('filesize_approx'))
			)
			if format.get('acodec') != 'none' and format.get('vcodec') != 'none':
				stream.add_muxed_info(
					videoCodec=format.get('vcodec'),
					videoExt=format.get('video_ext'),
					width=int(format.get('width')),
					height=int(format.get('height')),
					fps=int(format.get('fps')),
					audioCodec=format.get('acodec'),
					language=format.get('language'),
					audioSamplerate=int(format.get('asr'))
				)
			elif format.get('vcodec') != 'none':
				stream.add_video_info(
					videoCodec=format.get('vcodec'),
					videoExt=format.get('video_ext'),
					width=int(format.get('width')),
					height=int(format.get('height')),
					fps=int(format.get('fps'))
				)
			elif format.get('acodec') != 'none':
				stream.add_audio_info(
					audioCodec=format.get('acodec'),
					audioExt=format.get('audio_ext'),
					language=format.get('language'),
					audioBitrate=int(format.get('abr')),
					audioSamplerate=int(format.get('asr'))
				)
			else:
				allow_append = False

			if allow_append:
				self.streams.append(stream)

	def filter(self,
		only_video:bool=None,
		only_audio:bool=None,
		only_muxed:bool=None,
		no_muxed:bool=None,
		max_res:int=None, # max video height
		min_res:int=None, # min video height
		max_fps:int=None, # max video fps
		min_fps:int=None, # min video fps
		custom=None # custom filter function
	) -> "StreamsManager":
		filtered = self.streams
		if only_video:
			filtered = filter(lambda x: x.isVideo or x.isMuxed, filtered)
		elif only_audio:
			filtered = filter(lambda x: x.isAudio, filtered)
		elif only_muxed:
			filtered = filter(lambda x: x.isMuxed, filtered)

		if no_muxed:
			filtered = filter(lambda x: not x.isMuxed, filtered)

		if max_res:
			filtered = filter(lambda x: x.get("height") <= max_res, filtered)
		if min_res:
			filtered = filter(lambda x: x.get("height") >= min_res, filtered)
		if max_fps:
			filtered = filter(lambda x: x.get("fps") <= max_fps, filtered)
		if min_fps:
			filtered = filter(lambda x: x.get("fps") >= min_fps, filtered)

		if custom: filtered = filter(custom, filtered)
		return StreamsManager(self.videoId, list(filtered))

	def order_by(self, attribute_name: str, sub:str="", reverse=True) -> "StreamsManager":
		if sub:
			order_func = lambda x: (x.get(attribute_name), x.get(sub))
		else:
			order_func = lambda x: x.get(attribute_name)
		return StreamsManager(self.videoId, sorted(self.streams,
			key=order_func, reverse=reverse)
		)

	def reverse(self) -> "StreamsManager":
		return StreamsManager(self.videoId, list(reversed(self.streams)))

	def first(self) -> Stream:
		if len(self) > 0:
			return self.streams[0]
		raise ValueError("No Streams")

	def last(self) -> Stream:
		if len(self) > 0:
			return self.streams[-1]
		raise ValueError("No Streams")
