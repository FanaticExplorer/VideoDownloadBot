import os
import yt_dlp
import pretty_errors
from rich.console import Console
from rich import print as rprint
def download(link, name='%(title)s'):
    # Define the download options
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'videos/{}.%(ext)s'.format(name),
        'quiet': True,
        # 'verbose':True,
        # 'forcefilename': True,
        'nooverwrites': False,
    }
    c = Console()
    # Create the "videos" folder if it doesn't exist
    if not os.path.exists('videos'):
        os.mkdir('videos')
    
    with c.status(f"Downloading video from site: [i blue u]{link}", spinner='bounce') as status:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            downloaded_file_path = ydl.prepare_filename(info_dict)
        
    c.log(f"Video [i u blue]{downloaded_file_path}[/i u blue] downloaded!")
    video_size = os.path.getsize(downloaded_file_path) / (1024 * 1024)
    video_size = round(video_size, 2)
    c.log(f'Size: {video_size} MB')
    return downloaded_file_path

# download('https://www.reddit.com/r/shitposting/comments/11iqb81/huge_cake/?utm_source=share&utm_medium=web2x&context=3', 'test')
# download('https://www.tiktok.com/@mmeowmmia/video/7202978058284846341?is_from_webapp=1&sender_device=pc', 'test')
# download(link = 'https://www.instagram.com/reel/CpVclz4At_-/?utm_source=ig_web_copy_link')
# download(link = 'https://www.facebook.com/NASA/videos/736659094817458/?locale=ru_RU', name='progress_test')