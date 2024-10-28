import MyTube

link = "https://www.youtube.com/watch?v=GB5KEphbIWc"
# link = "https://www.youtube.com/watch?v=kVJgey4F23c"
yt = MyTube.YouTube(link)


streams = yt.streams.filter(
	only_video=True, no_muxed=True, max_res=720, min_res=360
).order_by("height", "fps")


# streams = yt.streams.filter(only_audio=True,
# 	custom=lambda x: x.get("language") == "ru"
# ).order_by("audioBitrate").streams

for stream in streams:
	print(stream)
