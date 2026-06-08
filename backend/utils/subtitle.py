import os
from typing import List, Optional


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


# 섹션 타입별 시간 가중치 (줄 수 × 가중치 → 전체 비율 결정)
_SECTION_WEIGHTS = {
    "인트로":   0.5,   # 짧은 기악 인트로
    "벌스":     1.8,
    "벌스1":    1.8,
    "벌스2":    1.8,
    "코러스":   2.2,   # 코러스는 반복/강조로 더 긴 체감
    "브릿지":   1.2,
    "아웃트로": 0.5,
}
_INTRO_OFFSET_RATIO = 0.04   # 전체 길이의 4% = 기악 인트로 여유


def _section_weight(section: str, is_chorus: bool) -> float:
    if is_chorus:
        return _SECTION_WEIGHTS["코러스"]
    s = section.lower()
    for key, w in _SECTION_WEIGHTS.items():
        if key in s or s.startswith(key[:3]):
            return w
    return 1.5


def _redistribute_lyrics(lyrics: list, music_duration: float) -> list:
    """
    섹션 구조를 인식해 타임스탬프를 재분배.
    단순 비례 스케일링 대신 섹션 타입별 가중치로 각 구간 길이를 결정한다.
    """
    if not lyrics:
        return []

    # 연속된 섹션으로 그룹화
    groups: list = []
    cur_key = None
    cur_grp: list = []
    for line in lyrics:
        key = (line.get("section", ""), bool(line.get("is_chorus")))
        if key != cur_key:
            if cur_grp:
                groups.append(cur_grp)
            cur_key = key
            cur_grp = [line]
        else:
            cur_grp.append(line)
    if cur_grp:
        groups.append(cur_grp)

    # 각 그룹의 가중치 계산
    weights = [
        _section_weight(g[0].get("section", ""), bool(g[0].get("is_chorus"))) * len(g)
        for g in groups
    ]
    total_w = sum(weights) or 1.0

    intro_gap = music_duration * _INTRO_OFFSET_RATIO
    available  = music_duration - intro_gap

    result = []
    t = intro_gap
    for grp, w in zip(groups, weights):
        sec_dur  = (w / total_w) * available
        line_dur = sec_dur / len(grp)
        for j, line in enumerate(grp):
            t_start = t + j * line_dur
            t_end   = min(t_start + line_dur * 0.90, music_duration - 0.1)
            result.append({
                **line,
                "time_start": round(t_start, 2),
                "time_end":   round(t_end,   2),
            })
        t += sec_dur

    return result


def build_synced_srt(lyrics: list, music_duration: float, output_path: str) -> str:
    """가사 타임스탬프를 섹션 구조 기반으로 재분배해 SRT 생성."""
    return generate_srt(_redistribute_lyrics(lyrics, music_duration) if lyrics else [], output_path)


def build_synced_ass(
    lyrics: list,
    music_duration: float,
    output_path: str,
    chorus_color: bool = True,
) -> str:
    """가사 타임스탬프를 섹션 구조 기반으로 재분배해 ASS 생성."""
    return generate_ass(
        _redistribute_lyrics(lyrics, music_duration) if lyrics else [],
        output_path,
        chorus_color,
    )
