import MyTube
import asyncio
# import requests

# file = tempfile.mkstemp()
# file.close()
# print(file)


# link = "https://www.youtube.com/watch?v=GB5KEphbIWc"
link = "https://www.youtube.com/watch?v=kVJgey4F23c"
yt = MyTube.YouTube(link)

# streams = yt.streams.filter(
# 	only_video=True, no_muxed=True, max_res=720, min_res=360
# ).order_by("res", "fps")

# streams = yt.streams.filter(only_audio=True,
# 	custom=lambda x: x.get("language") == "ru"
# ).order_by("audioBitrate").streams

# print(yt.streams.best_video())
# print(yt.streams.best_audio())

# for stream in streams:
# 	print(stream)

# stream = yt.streams.filter(only_muxed=True).first()
# file = stream.download("downloads")
# print(file)


video = yt.streams.filter(only_video=True, no_muxed=True, max_res=720).order_by("res").first()
audio = yt.streams.best_audio()
stream = yt.streams.filter(only_muxed=True).first()
# file = yt.download(video=stream)("downloads")
# print(file)

def mb(bytes_value):
	return f"{round(bytes_value / (1024 * 1024))} MB"


# print(video)
# video.download()


async def progress(current, total):
	print(mb(current), "/", mb(total), end="\r")


async def main():
	file = await yt.download(video=video, audio=audio)("downloads", on_progress=progress)

asyncio.run(main())
