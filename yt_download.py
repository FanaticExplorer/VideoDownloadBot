from yt_dlp import YoutubeDL
import os


ydl_opts = {
            'outtmpl':"%(title)s.mp4",
            'noplaylist' : True
}

def download_video(link):
    with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info("{}".format(link))
        filename=ydl.prepare_filename(result)
        if os.path.isfile(filename):
            os.remove(filename)
        ydl.download([link])
        return filename

#print(download_video('https://www.instagram.com/tv/CU-1Dt_D6Fy/?utm_source=ig_web_copy_link'))
#print(download_video('https://www.reddit.com/r/PhoenixSC/comments/q87nat/why_im_voting_for_the_allay_for_minecraft_mob/?utm_source=share&utm_medium=web2x&context=3'))