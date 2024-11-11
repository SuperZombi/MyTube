<h1 align="center">MyTube</h1>

<p align="center">
    <img src="https://raw.githubusercontent.com/SuperZombi/MyTube/main/github/images/icon.png" height="128px" align="center">
</p>
<p align="center">
    <img src="https://shields.io/badge/version-1.2.0-blue">
</p>
<p align="center">
    <a href="https://superzombi.github.io/MyTube/">Documentation</a>
</p>
<p align="center">
    MyTube is a wrapper around <a href="https://github.com/yt-dlp/yt-dlp">yt-dlp</a> that is similar in functionality to <a href="https://github.com/pytube/pytube">pytube</a>.<br>
    I made it because I was tired of pytube being unstable and throwing errors over time. 
</p>

### Requirements:

* [FFMPEG](https://ffmpeg.org/download.html) installed in $PATH

### Quick Start
```
pip install MyTube-dlp
```
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