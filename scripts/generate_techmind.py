#!/usr/bin/env python3
"""Free TechMind Shorts renderer: motion-graphics scenes + Edge TTS + FFmpeg."""
from __future__ import annotations
import subprocess
from pathlib import Path

OUT = Path("build")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 20

SCENES = [
    ("AI AGENTS", "AI agents ab sirf chat nahi karte.", "Computer par real actions le sakte hain."),
    ("OPEN APPS", "Apps khud open kar sakte hain.", "Mail, code aur terminal — sab ek workflow me."),
    ("BROWSE WEB", "Web ko samajhkar steps execute kar sakte hain.", "Search, navigate, compare aur act."),
    ("WRITE CODE", "Code likhkar bugs bhi fix kar sakte hain.", "Run, test, verify — phir retry."),
    ("TAKE ACTION", "Agent workflow simple hai.", "Plan -> Tool -> Verify -> Done."),
    ("TECHMIND", "AI jo aapke computer ke saath kaam karta hai.", "Follow TechMind for practical AI."),
]

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)

def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%").replace(",", "\\,")

def make_scene(i, title, line1, line2):
    p = OUT / f"scene_{i}.mp4"
    dur = 3.35
    common = (
        f"drawbox=x=55:y=90:w=970:h=1740:color=0x0b1220@0.96:t=fill,"
        f"drawbox=x=55:y=90:w=970:h=8:color=0x55d6ff@1:t=fill,"
        f"drawtext=text='{esc(title)}':fontcolor=white:fontsize=74:x=100:y=170,"
        f"drawtext=text='{esc(line1)}':fontcolor=white:fontsize=50:x=100:y=1180:line_spacing=16,"
        f"drawtext=text='{esc(line2)}':fontcolor=0xb8c7d9:fontsize=34:x=100:y=1410:line_spacing=12,"
        f"drawtext=text='TECHMIND  •  AI IN ACTION':fontcolor=0x55d6ff:fontsize=28:x=100:y=1710"
    )
    visuals = [
        "drawbox=x=100:y=360:w=880:h=650:color=0x101c2f:t=fill,"
        "drawbox=x=100:y=360:w=880:h=70:color=0x1d2b42:t=fill,"
        "drawtext=text='DESKTOP / AI CONTROL':fontcolor=0xdbeafe:fontsize=28:x=150:y=382,"
        "drawbox=x=150:y=500:w=240:h=120:color=0x22c55e@0.8:t=fill,"
        "drawbox=x=420:y=500:w=240:h=120:color=0x6366f1@0.8:t=fill,"
        "drawbox=x=690:y=500:w=240:h=120:color=0xf59e0b@0.8:t=fill,"
        "drawtext=text='MAIL':fontcolor=white:fontsize=30:x=225:y=545,"
        "drawtext=text='CODE':fontcolor=white:fontsize=30:x=495:y=545,"
        "drawtext=text='TERMINAL':fontcolor=white:fontsize=26:x=720:y=545,"
        "drawtext=text='AI AGENT  ->  OPEN  ->  ACT':fontcolor=0x86efac:fontsize=28:x=150:y=790",
        "drawbox=x=100:y=360:w=880:h=650:color=0x07101d:t=fill,"
        "drawbox=x=100:y=360:w=880:h=70:color=0x172338:t=fill,"
        "drawtext=text='WEB / SEARCH':fontcolor=0x55d6ff:fontsize=30:x=140:y=382,"
        "drawbox=x=150:y=500:w=780:h=90:color=0x101c2f:t=fill,"
        "drawtext=text='search  AI agent computer use':fontcolor=0xdbeafe:fontsize=30:x=180:y=528,"
        "drawbox=x=150:y=650:w=360:h=230:color=0x172338:t=fill,"
        "drawbox=x=540:y=650:w=390:h=230:color=0x172338:t=fill,"
        "drawtext=text='RESULT 01':fontcolor=white:fontsize=28:x=180:y=690,"
        "drawtext=text='RESULT 02':fontcolor=white:fontsize=28:x=570:y=690,"
        "drawtext=text='READ  ->  DECIDE  ->  NAVIGATE':fontcolor=0x86efac:fontsize=27:x=170:y=825",
        "drawbox=x=100:y=360:w=880:h=650:color=0x07101d:t=fill,"
        "drawbox=x=100:y=360:w=880:h=70:color=0x172338:t=fill,"
        "drawtext=text='CODE EDITOR':fontcolor=0x55d6ff:fontsize=30:x=140:y=382,"
        "drawtext=text='01  agent.run()':fontcolor=0x93c5fd:fontsize=32:x=150:y=510,"
        "drawtext=text='02  browser.open(url)':fontcolor=0x86efac:fontsize=32:x=150:y=590,"
        "drawtext=text='03  verify(result)':fontcolor=0xfcd34d:fontsize=32:x=150:y=670,"
        "drawtext=text='04  fix_and_retry()':fontcolor=0xf9a8d4:fontsize=32:x=150:y=750,"
        "drawtext=text='RUNNING  •  TESTS PASSED':fontcolor=0x86efac:fontsize=28:x=150:y=900",
        "drawbox=x=100:y=360:w=880:h=650:color=0x07101d:t=fill,"
        "drawtext=text='AGENT WORKFLOW':fontcolor=0x55d6ff:fontsize=30:x=150:y=420,"
        "drawbox=x=150:y=520:w=210:h=110:color=0x1d4ed8:t=fill,"
        "drawbox=x=435:y=520:w=210:h=110:color=0x0f766e:t=fill,"
        "drawbox=x=720:y=520:w=210:h=110:color=0x7c3aed:t=fill,"
        "drawtext=text='PLAN':fontcolor=white:fontsize=30:x=215:y=555,"
        "drawtext=text='TOOL':fontcolor=white:fontsize=30:x=500:y=555,"
        "drawtext=text='VERIFY':fontcolor=white:fontsize=30:x=770:y=555,"
        "drawtext=text='->':fontcolor=0x55d6ff:fontsize=50:x=375:y=545,"
        "drawtext=text='->':fontcolor=0x55d6ff:fontsize=50:x=660:y=545,"
        "drawtext=text='DONE':fontcolor=0x86efac:fontsize=38:x=480:y=780",
        "drawbox=x=100:y=360:w=880:h=650:color=0x07101d:t=fill,"
        "drawbox=x=150:y=440:w=780:h=430:color=0x111c31:t=fill,"
        "drawbox=x=190:y=500:w=700:h=70:color=0x1d2b42:t=fill,"
        "drawtext=text='TECHMIND':fontcolor=0x55d6ff:fontsize=34:x=220:y=520,"
        "drawtext=text='Computer + AI Agent':fontcolor=white:fontsize=44:x=220:y=650,"
        "drawtext=text='Plan  •  Act  •  Verify':fontcolor=0xb8c7d9:fontsize=32:x=220:y=750,"
        "drawbox=x=250:y=930:w=580:h=8:color=0x55d6ff@0.5:t=fill"
        ,
        "drawbox=x=100:y=360:w=880:h=650:color=0x07101d:t=fill,"
        "drawbox=x=150:y=440:w=780:h=430:color=0x111c31:t=fill,"
        "drawtext=text='TECHMIND':fontcolor=0x55d6ff:fontsize=34:x=220:y=520,"
        "drawtext=text='Computer + AI Agent':fontcolor=white:fontsize=44:x=220:y=650,"
        "drawtext=text='Plan  •  Act  •  Verify':fontcolor=0xb8c7d9:fontsize=32:x=220:y=750,"
        "drawtext=text='READY':fontcolor=0x86efac:fontsize=38:x=220:y=850,"
        "drawbox=x='250+120*sin(2*PI*t/2)':y=930:w=580:h=8:color=0x55d6ff@0.5:t=fill"
    ]
    vf = common + "," + visuals[i]
    run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x030712:s={W}x{H}:r={FPS}:d={dur}",
         "-vf",vf,"-an","-c:v","libx264","-preset","veryfast","-crf","23","-pix_fmt","yuv420p",str(p)])
    return p

def main():
    text = ("AI Agents ab sirf chat nahi karte. Ye agents computer par apps khol sakte hain, "
            "web browse kar sakte hain, code likh sakte hain aur tasks execute kar sakte hain. "
            "TechMind: AI jo aapke computer ke saath kaam karta hai.")
    run(["python","-m","pip","install","--quiet","edge-tts"])
    run(["edge-tts","--voice","hi-IN-MadhurNeural","--rate","+5%","--text",text,"--write-media",str(OUT/"voice.mp3")])
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
