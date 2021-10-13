from youtube_dl import YoutubeDL
import os


ydl_opts = {
            'outtmpl':"video.%(ext)s",
            'format': 'best',
            'noplaylist' : True
}

def download_video(link):
	if os.path.isfile("video.mp4"):
		os.remove("video.mp4")
	with YoutubeDL(ydl_opts) as ydl:
		return ydl.download([link])


#low_res_video = zip(video)

#download_video('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
#get_video_title('https://www.youtube.com/watch?v=dQw4w9WgXcQ')