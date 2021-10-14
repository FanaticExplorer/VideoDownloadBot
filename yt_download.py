from youtube_dl import YoutubeDL
import os


ydl_opts = {
            'format': 'worst',
            'noplaylist' : True
}

def download_video(link):
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info("{}".format(link), download=False)
        filename=ydl.prepare_filename(result)
        if os.path.isfile(filename):
            os.remove(filename)
        ydl.download([link])
        return filename