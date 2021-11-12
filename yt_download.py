from yt_dlp import YoutubeDL
import os

from yt_dlp.utils import DownloadError



class Downloader:
    ydl_opts_with_format = {
            'format':"mp4"
    }
    ydl_opts_with_outtmpl = {
            'outtmpl':"%(title)s.mp4"
    }
    ydl_opts_with_no_opts={}

    def __init__(self,download_link):
        self.download_link=download_link
        with YoutubeDL(self.ydl_opts_with_format) as ydl:
            self.result = ydl.extract_info("{}".format(self.download_link), download=False)


    def get_service_name(self):
        return self.result['extractor']

    def download_video(self):
        with YoutubeDL(self.ydl_opts_with_format) as ydl:
            try:
                ydl.download([self.download_link])
            except DownloadError:
                try:
                    with YoutubeDL(self.ydl_opts_with_outtmpl) as ydl:
                            ydl.download([self.download_link])
                except DownloadError:
                    with YoutubeDL(self.ydl_opts_with_no_opts) as ydl:
                            ydl.download([self.download_link])
            
        filename=ydl.prepare_filename(self.result)
        return filename

    def get_size(self):
        print(self.result['filesize_approx'])
        return self.result['filesize_approx']

#downloader_from_the_link=Downloader('https://www.youtube.com/watch?v=SKvIyDB5FRU')
#print(downloader_from_the_link.download_video())