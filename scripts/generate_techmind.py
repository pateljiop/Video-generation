#!/usr/bin/env python3
"""Free TechMind Shorts renderer: animated computer-UI motion graphics + Hindi Edge TTS + FFmpeg."""
from __future__ import annotations

import subprocess
from pathlib import Path

OUT = Path("build")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 20

# Short-form narration is intentionally written to match six visual beats.
NARRATION = (
    "AI agents ab sirf chat nahi karte. "
    "Ye computer par apps khol sakte hain, web browse kar sakte hain, code likh sakte hain, "
    "aur task complete hone tak khud verify bhi kar sakte hain. "
    "TechMind — AI jo aapke computer ke saath kaam karta hai."
)

SCENES = [
    ("AI AGENT", "CHAT SE AAGE", "Agent ko task do.", "Computer par action start.", "desktop"),
    ("OPEN", "APPS", "Mail  →  Code  →  Terminal", "Ek workflow, multiple tools.", "apps"),
    ("BROWSE", "THE WEB", "Search  →  Read  →  Decide", "Agent page ko samajhkar next step leta hai.", "browser"),
    ("WRITE", "CODE", "Write  →  Run  →  Test", "Bug mile? Fix karo. Phir verify.", "code"),
    ("EXECUTE", "THE TASK", "PLAN  →  TOOL  →  VERIFY", "Result sahi hai tabhi DONE.", "agent"),
    ("TECHMIND", "COMPUTER + AI", "AI jo aapke computer ke saath kaam karta hai.", "Follow for practical AI.", "end"),
]

def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)

def esc(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace(",", "\\,")
    )

def text_filter(txt: str, x: str, y: str, size: int, color: str = "white",
                alpha: str = "1", enable: str | None = None) -> str:
    f = f"drawtext=text='{esc(txt)}':fontcolor={color}@{alpha}:fontsize={size}:x={x}:y={y}"
    if enable:
        f += f":enable='{enable}'"
    return f

def base_bg() -> list[str]:
    return [
        "drawbox=x=0:y=0:w=1080:h=1920:color=0x020617:t=fill",
        "drawbox=x=0:y=0:w=1080:h=1920:color=0x0b1220@0.35:t=fill",
        # Moving scanline/grid gives the background life without external media.
        "drawbox=x=0:y='mod(80*t,1920)':w=1080:h=2:color=0x38bdf8@0.10:t=fill",
        "drawbox=x='mod(150*t,1080)':y=0:w=2:h=1920:color=0x38bdf8@0.05:t=fill",
        text_filter("TECHMIND", "70", "78", 30, "0x67e8f9"),
        text_filter("AI IN ACTION", "70", "118", 20, "0x94a3b8"),
    ]

def scene_filter(kind: str, dur: float, title: str, kicker: str, line1: str, line2: str) -> str:
    f = base_bg()

    # Top title changes by scene; no giant repeated card.
    f += [
        text_filter(kicker, "70", "250", 28, "0x67e8f9"),
        text_filter(title, "70", "292", 82, "white"),
        text_filter(line1, "70", "390", 34, "0xcbd5e1"),
    ]

    if kind == "desktop":
        # Simulated desktop with moving active window and cursor.
        f += [
            "drawbox=x=60:y=500:w=960:h=980:color=0x0f172a@0.98:t=fill",
            "drawbox=x=60:y=500:w=960:h=72:color=0x111c31:t=fill",
            "drawbox=x=86:y=524:w=18:h=18:color=0xf87171:t=fill",
            "drawbox=x=116:y=524:w=18:h=18:color=0xfbbf24:t=fill",
            "drawbox=x=146:y=524:w=18:h=18:color=0x4ade80:t=fill",
            text_filter("AI AGENT CONTROL", "205", "518", 24, "0xe2e8f0"),
            "drawbox=x=100:y=650:w=270:h=210:color=0x172554:t=fill",
            "drawbox=x=405:y=650:w=270:h=210:color=0x14532d:t=fill",
            "drawbox=x=710:y=650:w=220:h=210:color=0x3f1d1d:t=fill",
            text_filter("MAIL", "190", "735", 34, "white"),
            text_filter("CODE", "485", "735", 34, "white"),
            text_filter("TERMINAL", "735", "735", 27, "white"),
            text_filter("OPENING...", "170", "805", 22, "0x67e8f9"),
            text_filter("READY", "490", "805", 22, "0x86efac"),
            text_filter("WAIT", "755", "805", 22, "0xfbbf24"),
            "drawbox=x=120:y=980:w=820:h=260:color=0x07111f:t=fill",
            text_filter("TASK", "150", "1030", 22, "0x94a3b8"),
            text_filter("Open mail, find the latest report", "150", "1090", 31, "white"),
            "drawbox=x=150:y=1165:w='560*min(t/2\\,1)':h=10:color=0x38bdf8:t=fill",
            text_filter("AGENT WORKING", "150", "1205", 20, "0x67e8f9"),
            "drawbox=x='180+650*min(t/3\\,1)':y='900+70*sin(3*t)':w=12:h=18:color=0xffffff:t=fill",
        ]
    elif kind == "apps":
        # App launcher / workflow visual.
        f += [
            "drawbox=x=55:y=500:w=970:h=1030:color=0x0b1220:t=fill",
            text_filter("WORKSPACE", "95", "555", 24, "0x94a3b8"),
            "drawbox=x=95:y=620:w=270:h=300:color=0x172554:t=fill",
            "drawbox=x=405:y=620:w=270:h=300:color=0x052e16:t=fill",
            "drawbox=x=715:y=620:w=215:h=300:color=0x1c1917:t=fill",
            text_filter("MAIL", "155", "715", 42, "white"),
            text_filter("OPEN", "155", "785", 22, "0x67e8f9"),
            text_filter("CODE", "465", "715", 42, "white"),
            text_filter("RUN", "465", "785", 22, "0x86efac"),
            text_filter("TERM", "755", "715", 34, "white"),
            text_filter("EXEC", "755", "785", 22, "0xfbbf24"),
            "drawbox=x=190:y=1040:w=700:h=12:color=0x1e293b:t=fill",
            "drawbox=x=190:y=1040:w='700*min(t/3\\,1)':h=12:color=0x38bdf8:t=fill",
            text_filter("OPEN  →  READ  →  ACT", "220", "1090", 32, "white"),
            "drawbox=x=170:y=1180:w=740:h=210:color=0x111827:t=fill",
            text_filter("ONE AGENT", "205", "1225", 25, "0x67e8f9"),
            text_filter("multiple tools / one workflow", "205", "1280", 34, "white"),
            text_filter(line2, "205", "1350", 24, "0x94a3b8"),
            "drawbox=x='120+760*min(t/4\\,1)':y=570:w=16:h=16:color=0x67e8f9:t=fill",
        ]
    elif kind == "browser":
        # Browser with search bar, result cards, scrolling highlight.
        f += [
            "drawbox=x=45:y=500:w=990:h=1080:color=0xf8fafc:t=fill",
            "drawbox=x=45:y=500:w=990:h=78:color=0x1e293b:t=fill",
            "drawbox=x=70:y=527:w=16:h=16:color=0xf87171:t=fill",
            "drawbox=x=98:y=527:w=16:h=16:color=0xfbbf24:t=fill",
            "drawbox=x=126:y=527:w=16:h=16:color=0x4ade80:t=fill",
            "drawbox=x=185:y=520:w=790:h=38:color=0x334155:t=fill",
            text_filter("search  AI agent computer use", "215", "528", 20, "0xe2e8f0"),
            "drawbox=x=100:y=650:w=880:h=95:color=0xe2e8f0:t=fill",
            text_filter("AI agents that can use a computer", "135", "680", 27, "0x0f172a"),
            "drawbox=x=100:y=790:w=410:h=250:color=0xffffff:t=fill",
            "drawbox=x=545:y=790:w=435:h=250:color=0xffffff:t=fill",
            text_filter("RESULT 01", "135", "835", 23, "0x2563eb"),
            text_filter("browser control", "135", "880", 31, "0x0f172a"),
            text_filter("RESULT 02", "580", "835", 23, "0x2563eb"),
            text_filter("computer use", "580", "880", 31, "0x0f172a"),
            "drawbox=x=100:y='1100+90*sin(1.2*t)':w=880:h=6:color=0x38bdf8:t=fill",
            text_filter("READ", "145", "1160", 24, "0x475569"),
            text_filter("DECIDE", "420", "1160", 24, "0x475569"),
            text_filter("NAVIGATE", "730", "1160", 24, "0x475569"),
            "drawtext=text='✓':fontcolor=0x16a34a:fontsize=46:x=165:y=1220",
            "drawtext=text='✓':fontcolor=0x16a34a:fontsize=46:x=440:y=1220",
            "drawtext=text='→':fontcolor=0x2563eb:fontsize=46:x='750+70*sin(2*t)':y=1220",
        ]
    elif kind == "code":
        # Realistic editor/terminal split.
        f += [
            "drawbox=x=45:y=500:w=990:h=1080:color=0x0b1120:t=fill",
            "drawbox=x=45:y=500:w=990:h=70:color=0x111827:t=fill",
            text_filter("agent.py", "100", "520", 23, "0xe2e8f0"),
            text_filter("RUNNING", "800", "520", 20, "0x86efac"),
            text_filter("01", "95", "625", 21, "0x64748b"),
            text_filter("task = browser.open(url)", "145", "625", 27, "0x93c5fd"),
            text_filter("02", "95", "700", 21, "0x64748b"),
            text_filter("result = agent.read()", "145", "700", 27, "0x86efac"),
            text_filter("03", "95", "775", 21, "0x64748b"),
            text_filter("assert result.ok", "145", "775", 27, "0xfde68a"),
            text_filter("04", "95", "850", 21, "0x64748b"),
            text_filter("fix_and_retry()", "145", "850", 27, "0xf9a8d4"),
            "drawbox=x=90:y=940:w=900:h=330:color=0x020617:t=fill",
            text_filter("$ python agent.py", "125", "1000", 27, "0x94a3b8"),
            text_filter("> opening browser...", "125", "1065", 25, "0x67e8f9"),
            text_filter("> tests passed", "125", "1130", 25, "0x86efac"),
            text_filter("> task complete", "125", "1195", 25, "white"),
            "drawbox=x=125:y='1260+15*sin(4*t)':w='760*min(t/3\\,1)':h=7:color=0x22c55e:t=fill",
        ]
    elif kind == "agent":
        # Large connected execution graph with moving pulse.
        f += [
            "drawbox=x=55:y=500:w=970:h=1080:color=0x0b1220:t=fill",
            text_filter("AUTONOMOUS TASK", "100", "565", 24, "0x94a3b8"),
            "drawbox=x=110:y=700:w=230:h=150:color=0x172554:t=fill",
            "drawbox=x=425:y=700:w=230:h=150:color=0x064e3b:t=fill",
            "drawbox=x=740:y=700:w=230:h=150:color=0x3b0764:t=fill",
            text_filter("PLAN", "180", "755", 30, "white"),
            text_filter("TOOL", "495", "755", 30, "white"),
            text_filter("VERIFY", "790", "755", 30, "white"),
            text_filter("→", "365", "750", 48, "0x67e8f9"),
            text_filter("→", "680", "750", 48, "0x67e8f9"),
            "drawbox=x='125+790*min(t/4\\,1)':y=690:w=20:h=170:color=0x67e8f9@0.22:t=fill",
            "drawbox=x=150:y=980:w=780:h=250:color=0x111827:t=fill",
            text_filter("VERIFYING RESULT", "190", "1030", 25, "0x67e8f9"),
            text_filter("✓ browser action", "190", "1090", 28, "0x86efac"),
            text_filter("✓ code check", "190", "1145", 28, "0x86efac"),
            text_filter("✓ final output", "190", "1200", 28, "0x86efac"),
            text_filter("DONE", "760", "1340", 44, "0x86efac"),
        ]
    else:
        # Clean branded ending, still animated rather than a static title card.
        f += [
            "drawbox=x=55:y=500:w=970:h=1080:color=0x07111f:t=fill",
            "drawbox=x=120:y=650:w=840:h=520:color=0x0f172a:t=fill",
            "drawbox=x=180:y=730:w=680:h=110:color=0x111c31:t=fill",
            text_filter("TECHMIND", "235", "755", 52, "0x67e8f9"),
            text_filter("COMPUTER + AI", "235", "885", 42, "white"),
            text_filter("Plan  •  Act  •  Verify", "235", "970", 30, "0xcbd5e1"),
            "drawbox=x=180:y='1090+20*sin(2*t)':w='680*min(t/2\\,1)':h=7:color=0x38bdf8:t=fill",
            text_filter(line1, "110", "1280", 30, "white"),
            text_filter(line2, "110", "1350", 24, "0x94a3b8"),
        ]

    f += [
        # Bottom progress + tiny subtitle; intentionally not a repeated giant card.
        "drawbox=x=70:y=1780:w=940:h=5:color=0x1e293b:t=fill",
        f"drawbox=x=70:y=1780:w='940*min(t/{max(dur,0.1):.3f},1)':h=5:color=0x38bdf8:t=fill",
        text_filter(line2, "70", "1830", 23, "0x94a3b8"),
    ]
    return ",".join(f)

def make_scene(i: int, scene: tuple[str, str, str, str, str], dur: float) -> Path:
    kicker, title, line1, line2, kind = scene
    out = OUT / f"scene_{i}.mp4"
    vf = scene_filter(kind, dur, title, kicker, line1, line2)
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x020617:s={W}x{H}:r={FPS}:d={dur:.3f}",
        "-vf", vf,
        "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-pix_fmt", "yuv420p",
        str(out),
    ])
    return out

def main() -> None:
    run(["python", "-m", "pip", "install", "--quiet", "edge-tts"])
    run([
        "edge-tts", "--voice", "hi-IN-MadhurNeural", "--rate", "+8%",
        "--text", NARRATION, "--write-media", str(OUT / "voice.mp3")
    ])
    audio_duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(OUT / "voice.mp3")
    ], text=True).strip())
    # Keep each visual beat exactly aligned to the narration length.
    scene_duration = audio_duration / len(SCENES)
    print(f"TTS duration={audio_duration:.2f}s; scene duration={scene_duration:.2f}s")

    clips = [make_scene(i, scene, scene_duration) for i, scene in enumerate(SCENES)]
    concat = OUT / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")

    silent = OUT / "silent.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-c", "copy", str(silent)
    ])

    final = OUT / "techmind-daily.mp4"
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(OUT / "voice.mp3"),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
        str(final)
    ])
    run([
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-show_entries", "format=duration,size",
        "-of", "default=noprint_wrappers=1",
        str(final)
    ])
    print(f"FINAL={final}")

if __name__ == "__main__":
    main()
