#!/usr/bin/env python3
"""Free TechMind Shorts renderer: motion-graphics scenes + Edge TTS + FFmpeg."""
from __future__ import annotations
import os, subprocess, textwrap
from pathlib import Path

OUT = Path("build")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 20

SCENES = [
    ("AI AGENTS", "AI agents ab sirf chat nahi karte.", "They can actually operate your computer."),
    ("OPEN APPS", "Apps khud open kar sakte hain.", "No more copy-paste for every small task."),
    ("BROWSE WEB", "Web ko samajhkar steps execute kar sakte hain.", "Search, navigate, compare and act."),
    ("WRITE CODE", "Code likhkar bugs bhi fix kar sakte hain.", "The agent can test, debug and iterate."),
    ("TAKE ACTION", "Real tasks ko tools ke through execute karte hain.", "Plan → Tool → Verify → Done."),
    ("TECHMIND", "AI jo aapke computer ke saath kaam karta hai.", "Follow TechMind for practical AI."),
]

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)

def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%").replace(",", "\\,")

def make_scene(i, title, line1, line2):
    p = OUT / f"scene_{i}.mp4"
    dur = 5
    # Animated tech-card scene. Everything is generated locally; no paid media API.
    vf = (
        f"drawbox=x=55:y=90:w=970:h=1740:color=0x152238@0.72:t=fill,"
        f"drawbox=x=55:y=90:w=970:h=8:color=0x55d6ff@1:t=fill,"
        f"drawbox=x='80+40*sin(2*PI*t/4)':y=340:w=900:h=2:color=0x55d6ff@0.18:t=fill,"
        f"drawbox=x=110:y=470:w=860:h=520:color=0x08111f@0.96:t=fill,"
        f"drawbox=x='150+180*sin(2*PI*t/3)':y=540:w=170:h=110:color=0x2dd4bf@0.9:t=fill,"
        f"drawbox=x='600+130*cos(2*PI*t/2.5)':y=700:w=220:h=130:color=0x6366f1@0.9:t=fill,"
        f"drawbox=x='250+100*cos(2*PI*t/3.2)':y=830:w=300:h=70:color=0xf59e0b@0.9:t=fill,"
        f"drawtext=text='{esc(title)}':fontcolor=white:fontsize=78:x=110:y=180,"
        f"drawtext=text='{esc(line1)}':fontcolor=white:fontsize=55:x=110:y=1120:line_spacing=18,"
        f"drawtext=text='{esc(line2)}':fontcolor=0xb8c7d9:fontsize=39:x=110:y=1370:line_spacing=14,"
        f"drawtext=text='TECHMIND':fontcolor=0x55d6ff:fontsize=30:x=110:y=1710"
    )
    run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x030712:s={W}x{H}:r={FPS}:d={dur}",
         "-vf",vf,"-an","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p",str(p)])
    return p

def main():
    text = ("AI Agents ab sirf chat nahi karte. "
            "Ye agents computer par apps khol sakte hain, web browse kar sakte hain, "
            "code likh sakte hain aur tasks execute kar sakte hain. "
            "TechMind: AI jo aapke computer ke saath kaam karta hai.")
    (OUT/"voice.txt").write_text(text, encoding="utf-8")
    run(["python","-m","pip","install","--quiet","edge-tts"])
    run(["edge-tts","--voice","en-US-AriaNeural","--rate","+8%","--text",text,"--write-media",str(OUT/"voice.mp3")])

    clips = [make_scene(i, *scene) for i, scene in enumerate(SCENES)]
    concat = OUT/"concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")
    silent = OUT/"silent.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    final = OUT/"techmind-daily.mp4"
    run(["ffmpeg","-y","-i",str(silent),"-i",str(OUT/"voice.mp3"),"-map","0:v:0","-map","1:a:0",
         "-c:v","copy","-c:a","aac","-b:a","128k","-shortest",str(final)])
    run(["ffprobe","-v","error","-show_entries","format=duration,size","-of","default=noprint_wrappers=1",str(final)])
    print(f"FINAL={final}")

if __name__ == "__main__":
    main()
