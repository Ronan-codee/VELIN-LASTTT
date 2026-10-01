"""Dynamise source.mp4 (sans audio) et incruste des sous-titres mot par mot."""
import subprocess

SRC = "source.mp4"
# (début, fin, vitesse, sous-titre) dans la vidéo source
SEGS = [
    (0.0, 3.75, 1.30, "LAVABLE EN MACHINE"),
    (3.75, 6.80, 1.20, "SÈCHE À L'AIR LIBRE"),
    (6.80, 9.85, 1.20, "SE FAIT EN UN GESTE"),
    (9.85, 12.9, 1.20, "DOUCEUR AU QUOTIDIEN"),
]
ZOOM = 0.12  # zoom progressif 100% -> 112% par plan
ACCENT = "&H004FC1F2&"  # BGR : jaune doré
WHITE = "&H00FFFFFF&"

def ts(t):
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h}:{m:02d}:{t % 60:05.2f}"

filters, labels, events, t0 = [], [], [], 0.0
for i, (a, b, sp, text) in enumerate(SEGS):
    d = (b - a) / sp
    filters.append(
        f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps=30,"
        f"scale='trunc(1080*(1+{ZOOM}*t/{d:.3f})/2)*2':'trunc(1080*(1+{ZOOM}*t/{d:.3f})/2)*2':eval=frame,"
        f"crop=1080:1080,setsar=1[v{i}]"
    )
    labels.append(f"[v{i}]")
    words = text.split()
    n = len(words)
    start = t0 + 0.15
    step = min(0.28, (d - 0.5) / n)
    for k in range(n):
        s = start + k * step
        e = t0 + d - 0.1 if k == n - 1 else start + (k + 1) * step
        parts = []
        for j, w in enumerate(words):
            if j < k:
                parts.append(f"{{\\1c{WHITE}}}{w}")
            elif j == k:
                parts.append(f"{{\\1c{ACCENT}}}{w}")
            else:
                parts.append(f"{{\\alpha&HFF&}}{w}{{\\alpha&H00&}}")
        pop = "{\\fscx85\\fscy85\\t(0,110,\\fscx100\\fscy100)}"
        events.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{pop}{' '.join(parts)}")
    t0 += d

ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,DejaVu Sans,78,{WHITE},{WHITE},&H00000000&,&H80000000&,-1,0,0,0,100,100,0,0,1,7,2,2,60,60,120,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
""" + "\n".join(events) + "\n"
open("subtitles.ass", "w", encoding="utf-8").write(ass)

fc = ";".join(filters) + ";" + "".join(labels) + f"concat=n={len(SEGS)}:v=1:a=0,ass=subtitles.ass[out]"
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-i", SRC, "-filter_complex", fc, "-map", "[out]",
    "-an", "-c:v", "libx264", "-crf", "23", "-preset", "slow", "-pix_fmt", "yuv420p",
    "-movflags", "+faststart", "final.mp4",
], check=True)
print(f"durée finale ≈ {t0:.2f}s")
