from yt_dlp import YoutubeDL
import os



class Downloader:
    ydl_opts = {
            'outtmpl':"%(title)s.mp4",
            'format':"mp4"
    }
    def __init__(self,download_link):
        self.download_link=download_link

    def download_video(self):
        with YoutubeDL(self.ydl_opts) as ydl:
            result = ydl.extract_info("{}".format(self.download_link))
            filename=ydl.prepare_filename(result)
            return filename

#downloader_from_the_link=Downloader('https://www.youtube.com/watch?v=SKvIyDB5FRU')
#print(downloader_from_the_link.download_video())