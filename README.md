<img src="https://shields.io/badge/version-1.0.0-blue">

MyTube is a wrapper around [yt-dlp](https://github.com/yt-dlp/yt-dlp) that is similar in functionality to [pytube](https://github.com/pytube/pytube).

I made it because I was tired of pytube being unstable and throwing errors over time.

### Requirements

* [FFMPEG](https://ffmpeg.org/download.html) installed in $PATH
```
pip install yt-dlp
```

### Quick Start
```python
import MyTube
import asyncio

async def main():
	link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
	yt = MyTube.YouTube(link)
	stream = yt.streams.filter(only_muxed=True).order_by("res").first()
	file = await stream.download("downloads")

asyncio.run(main())
```
