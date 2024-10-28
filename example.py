import MyTube

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
