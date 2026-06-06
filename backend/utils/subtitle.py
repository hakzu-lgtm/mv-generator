import os
from typing import List


def seconds_to_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def generate_srt(lyrics: list, output_path: str) -> str:
    lines = []
    idx = 1
    for item in lyrics:
        start = seconds_to_srt_time(item.get("time_start", 0))
        end = seconds_to_srt_time(item.get("time_end", item.get("time_start", 0) + 3))
        text = item.get("text", "")
        lines.append(f"{idx}\n{start} --> {end}\n{text}\n")
        idx += 1

    srt_content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    return output_path


def generate_ass(lyrics: list, output_path: str, chorus_color: bool = True) -> str:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Malgun Gothic,56,&H00F1F5F9,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,60,60,40,1
Style: Chorus,Malgun Gothic,68,&H00F59E0B,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,2,2,60,60,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def to_ass_time(s: float) -> str:
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        return f"{h}:{m:02d}:{sec:05.2f}"

    events = []
    for item in lyrics:
        start = to_ass_time(item.get("time_start", 0))
        end = to_ass_time(item.get("time_end", item.get("time_start", 0) + 3))
        text = item.get("text", "").replace("\n", "\\N")
        style = "Chorus" if (item.get("is_chorus") and chorus_color) else "Default"
        events.append(f"Dialogue: 0,{start},{end},{style},,0,0,0,,{text}")

    content = header + "\n".join(events)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path
