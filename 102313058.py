import sys
import os
import shutil
import yt_dlp
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

# ----------------------------
# Function to validate inputs
# ----------------------------
def validate_inputs(args):
    if len(args) != 5:
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer = args[1]
    
    try:
        number = int(args[2])
        duration = int(args[3])
    except ValueError:
        print("NumberOfVideos and AudioDuration must be integers.")
        sys.exit(1)

    output_file = args[4]

    if number <= 10:
        print("NumberOfVideos must be greater than 10.")
        sys.exit(1)

    if duration <= 20:
        print("AudioDuration must be greater than 20 seconds.")
        sys.exit(1)

    if not output_file.endswith(".mp3"):
        print("Output file must end with .mp3")
        sys.exit(1)

    return singer, number, duration, output_file


# ----------------------------
# Download YouTube Videos
# ----------------------------
def download_videos(singer, number):
    os.makedirs("videos", exist_ok=True)

    search_query = f"ytsearch{number}:{singer} official song"

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'videos/%(title)s.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
    except Exception as e:
        print("Error downloading videos:", e)
        sys.exit(1)


# ----------------------------
# Convert Videos to Audio
# ----------------------------
def convert_to_audio():
    os.makedirs("audios", exist_ok=True)

    for file in os.listdir("videos"):
        if file.endswith((".mp4", ".mkv", ".webm")):
            video_path = os.path.join("videos", file)
            audio_path = os.path.join("audios", file.split(".")[0] + ".mp3")

            try:
                clip = VideoFileClip(video_path)
                clip.audio.write_audiofile(audio_path, logger=None)
                clip.close()
            except Exception as e:
                print("Error converting video:", e)


# ----------------------------
# Trim Audio Files
# ----------------------------
def trim_audios(duration):
    trimmed_files = []

    for file in os.listdir("audios"):
        if file.endswith(".mp3"):
            path = os.path.join("audios", file)
            try:
                audio = AudioSegment.from_mp3(path)
                trimmed = audio[:duration * 1000]  # milliseconds
                trimmed.export(path, format="mp3")
                trimmed_files.append(path)
            except Exception as e:
                print("Error trimming audio:", e)

    return trimmed_files


# ----------------------------
# Merge Audios
# ----------------------------
def merge_audios(files, output_file):
    final_audio = AudioSegment.empty()

    for file in files:
        try:
            audio = AudioSegment.from_mp3(file)
            final_audio += audio
        except Exception as e:
            print("Error merging:", e)

    final_audio.export(output_file, format="mp3")

# ----------------------------
# Reusable function for Web App
# ----------------------------
def create_mashup(singer, number, duration, output_file):
    download_videos(singer, number)
    convert_to_audio()
    trimmed_files = trim_audios(duration)
    merge_audios(trimmed_files, output_file)

    shutil.rmtree("videos")
    shutil.rmtree("audios")

# ----------------------------
# Main Function
# ----------------------------
def main():
    singer, number, duration, output_file = validate_inputs(sys.argv)

    print("Downloading videos...")
    download_videos(singer, number)

    print("Converting videos to audio...")
    convert_to_audio()

    print("Trimming audio files...")
    trimmed_files = trim_audios(duration)

    print("Merging audio files...")
    merge_audios(trimmed_files, output_file)

    print("Mashup created successfully:", output_file)

    shutil.rmtree("videos")
    shutil.rmtree("audios")


if __name__ == "__main__":
    main()