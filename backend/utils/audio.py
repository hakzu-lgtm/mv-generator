import os
import subprocess


def wav_to_mp3(wav_path: str, mp3_path: str, bitrate: str = "192k") -> str:
    cmd = [
        "ffmpeg", "-y", "-i", wav_path,
        "-codec:a", "libmp3lame", "-b:a", bitrate,
        mp3_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return mp3_path


def get_audio_duration(path: str) -> float:
    try:
        import librosa
        duration = librosa.get_duration(path=path)
        return duration
    except Exception:
        return 0.0


def analyze_bpm(path: str) -> float:
    try:
        import librosa
        y, sr = librosa.load(path, duration=60)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return float(tempo)
    except Exception:
        return 120.0
