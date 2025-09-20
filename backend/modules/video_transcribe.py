import os
import tempfile
import librosa
import soundfile as sf
import yt_dlp
from modules.transcribe_generator import transcribe_audio_with_gemini  

SUPPORTED_VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".avi")

def download_youtube_video(youtube_url: str, out_dir: str) -> str:
    """Download YouTube video and return file path."""
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        return os.path.join(out_dir, f"{info['id']}.{info['ext']}")

def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from video and return temporary WAV path."""
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_audio_file.close()  # Close so we can write to it
    
    try:
        # Use librosa to load audio from video (requires ffmpeg)
        # librosa can handle video files and extract audio automatically
        audio_data, sample_rate = librosa.load(video_path, sr=None)
        
        # Save as WAV file
        sf.write(temp_audio_file.name, audio_data, sample_rate)
        return temp_audio_file.name
        
    except Exception as e:
        # Fallback: use ffmpeg directly if librosa fails
        try:
            import subprocess
            cmd = [
                'ffmpeg', '-i', video_path, 
                '-vn', '-acodec', 'pcm_s16le', 
                '-ar', '16000', '-ac', '1',
                '-y', temp_audio_file.name
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return temp_audio_file.name
        except subprocess.CalledProcessError as ffmpeg_error:
            raise RuntimeError(f"Failed to extract audio: {str(e)}, FFmpeg error: {str(ffmpeg_error)}")

def transcribe_video(path_or_url: str, is_youtube: bool = False) -> str:
    """Download/extract audio from video and transcribe."""
    temp_files = []

    try:
        # Use a temp directory for YouTube download
        if is_youtube:
            tmpdir = tempfile.mkdtemp()
            video_path = download_youtube_video(path_or_url, tmpdir)
            temp_files.append(video_path)
        else:
            video_path = path_or_url
            if not video_path.lower().endswith(SUPPORTED_VIDEO_EXTENSIONS):
                raise ValueError(f"Unsupported video format: {video_path}")

        # Extract audio to temp file
        audio_path = extract_audio_from_video(video_path)
        temp_files.append(audio_path)

        # Transcribe audio
        transcript = transcribe_audio_with_gemini(audio_path)
        if not transcript or not transcript.strip():
            raise RuntimeError("Transcription returned empty text.")

        return transcript

    finally:
        # Cleanup temporary files
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)