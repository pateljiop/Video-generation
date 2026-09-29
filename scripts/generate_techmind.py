#!/usr/bin/env python3
"""TechMind free Shorts renderer: kinetic tech visuals + Hindi Edge TTS + FFmpeg.
No paid video/image API is used. Visuals are original motion-graphics, not copied from any reference.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

OUT = Path("build")
OUT.mkdir(exist_ok=True)
W, H, FPS = 1080, 1920, 20
HERO: Path | None = None

NARRATION = (
    "AI agents ab sirf chat nahi karte. "
    "Ye computer par apps khol sakte hain, web browse kar sakte hain, code likh sakte hain, "
    "aur task complete hone tak khud verify bhi kar sakte hain. "
    "TechMind — AI jo aapke computer ke saath kaam karta hai."
)

# Short, kinetic beats. The visuals are deliberately original rather than copies of any reference.
SCENES = [
    ("AI AGENTS", "CHAT SE AAGE", "Give the task", "The computer starts moving", "hook"),
    ("OPEN", "APPS", "Mail  •  Code  •  Terminal", "One agent, multiple tools", "apps"),
    ("BROWSE", "THE WEB", "TYPE  →  SEARCH  →  READ", "The agent navigates for you", "browser"),
    ("WRITE", "CODE", "WRITE  →  RUN  →  FIX", "It tests and corrects the result", "code"),
    ("VERIFY", "BEFORE DONE", "PLAN  →  ACT  →  CHECK", "No result? It keeps working", "verify"),
    ("TECHMIND", "COMPUTER + AI", "PLAN  •  ACT  •  VERIFY", "Practical AI, not just chat", "end"),
]

def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def make_cinematic_source_image() -> Path:
    """Create a clean source frame for the free Wan I2V hero shot."""
    from PIL import Image, ImageDraw, ImageFilter

    p = OUT / "hero_source.png"
    img = Image.new("RGB", (832, 480), (5, 9, 18))
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            glow = max(0, 1 - (((x - 430) / 520) ** 2 + ((y - 235) / 360) ** 2))
            px[x, y] = (
                int(5 + 8 * glow),
                int(9 + 18 * glow),
                int(18 + 35 * glow),
            )

    d = ImageDraw.Draw(img, "RGBA")
    # Desk and ambient light.
    d.rectangle((0, 350, 832, 480), fill=(8, 12, 20, 255))
    d.rectangle((0, 342, 832, 358), fill=(25, 40, 55, 255))
    d.ellipse((560, 330, 820, 510), fill=(20, 110, 180, 45))

    # Laptop body/screen, deliberately simple so Wan supplies the realism and motion.
    d.rounded_rectangle((245, 95, 625, 335), 18, fill=(14, 20, 31, 255), outline=(80, 105, 130, 190), width=3)
    d.rounded_rectangle((265, 115, 605, 300), 10, fill=(4, 13, 25, 255))
    d.rectangle((285, 135, 585, 280), fill=(7, 22, 38, 255))
    for i, w in enumerate((220, 185, 250, 145, 205)):
        y = 155 + i * 22
        d.rounded_rectangle((300, y, 300 + w, y + 7), 3, fill=(70, 190, 235, 165))
    d.rounded_rectangle((220, 332, 650, 365), 8, fill=(24, 30, 40, 255))
    d.polygon([(220, 365), (650, 365), (710, 405), (160, 405)], fill=(18, 24, 33, 255))
    d.rounded_rectangle((385, 375, 475, 392), 5, fill=(65, 78, 92, 170))

    # Abstract hands/foreground silhouette.
    d.ellipse((115, 355, 255, 470), fill=(35, 43, 53, 220))
    d.ellipse((590, 360, 760, 485), fill=(35, 43, 53, 220))

    # Cinematic practical lights and subtle particles.
    for cx, cy, r in [(110, 95, 45), (740, 110, 55), (680, 300, 28)]:
        d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(50, 180, 255, 25))
    for x, y in [(92, 260), (720, 240), (770, 185), (180, 160), (650, 85)]:
        d.ellipse((x, y, x+3, y+3), fill=(120, 220, 255, 130))

    img = img.filter(ImageFilter.GaussianBlur(radius=0.25))
    img.save(p)
    return p


def generate_free_wan_hero() -> Path | None:
    """Try one free Hugging Face ZeroGPU Wan 2.2 I2V hero shot; return None on any quota/queue/API failure."""
    hero = OUT / "wan_hero.mp4"
    try:
        run(["python", "-m", "pip", "install", "--quiet", "gradio_client", "pillow"])
        source = make_cinematic_source_image()
        from gradio_client import Client, handle_file

        token = os.getenv("HF_TOKEN") or None
        client = Client(
            "zerogpu-aoti/wan2-2-fp8da-aoti-faster",
            token=token,
            verbose=True,
        )
        print("Attempting free Hugging Face ZeroGPU Wan 2.2 hero generation...")
        result = client.predict(
            input_image=handle_file(str(source)),
            prompt=(
                "Cinematic live-action close-up of a futuristic computer workstation at night, "
                "a powerful AI agent operating a laptop, screen glow reflecting across the desk, "
                "subtle hand movement, cursor activity, shallow depth of field, realistic glass "
                "and metal, blue and cyan practical lighting, smooth slow camera push-in, "
                "premium technology commercial, photorealistic, natural motion, no text, no logos."
            ),
            negative_prompt=(
                "static image, frozen frame, cartoon, illustration, anime, low quality, blurry, "
                "warped laptop, distorted hands, extra fingers, text, subtitles, watermark, logo"
            ),
            duration_seconds=3.0,
            guidance_scale=1.0,
            guidance_scale_2=1.0,
            steps=4,
            seed=42,
            randomize_seed=True,
            api_name="/generate_video",
        )
        video_path = result[0] if isinstance(result, (tuple, list)) else result
        if not video_path:
            raise RuntimeError(f"Space returned no video: {result!r}")
        shutil.copyfile(str(video_path), hero)
        duration = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "csv=p=0", str(hero)
        ], text=True).strip())
        if duration < 1.0:
            raise RuntimeError(f"Wan output too short: {duration:.2f}s")
        print(f"FREE_WAN_HERO={hero} duration={duration:.2f}s")
        return hero
    except Exception as exc:
        print(f"WAN_ZERO_GPU_FALLBACK={type(exc).__name__}: {exc}")
        return None


def make_hero_scene(dur: float) -> Path:
    out = OUT / "scene_0.mp4"
    # Crop the landscape hero into a vertical commercial frame and layer readable hook text.
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,eq=contrast=1.06:saturation=1.08,"
        "drawbox=x=0:y=0:w=1080:h=1920:color=0x020617@0.18:t=fill,"
        "drawbox=x=50:y=110:w=980:h=2:color=0x38bdf8@0.55:t=fill,"
        "drawtext=text='AI AGENTS':fontcolor=0x67e8f9:fontsize=30:x=60:y=180,"
        "drawtext=text='CHAT SE AAGE':fontcolor=white:fontsize=74:x=60:y=225,"
        "drawtext=text='Computer par kaam karte hain.':fontcolor=0xcbd5e1:fontsize=30:x=60:y=330,"
        "drawbox=x=60:y=1780:w=960:h=5:color=0x1e293b:t=fill,"
        f"drawbox=x=60:y=1780:w='960*min(t/{max(dur,0.1):.3f},1)':h=5:color=0x38bdf8:t=fill,"
        "drawtext=text='TECHMIND':fontcolor=0x67e8f9:fontsize=24:x=60:y=70"
    )
    run([
        "ffmpeg", "-y", "-i", str(HERO),
        "-vf", vf,
        "-t", f"{dur:.3f}",
        "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        str(out),
    ])
    return out


def esc(s: str) -> str:
    return (s.replace("\\", "\\\\")
             .replace(":", "\\:")
             .replace("'", "\\'")
             .replace("%", "\\%")
             .replace(",", "\\,"))

def dt(txt: str, x: str, y: str, size: int, color: str = "white",
       enable: str | None = None, alpha: str = "1") -> str:
    x = x.strip("'")
    y = y.strip("'")
    f = f"drawtext=text='{esc(txt)}':fontcolor={color}@{alpha}:fontsize={size}:x='{x}':y='{y}'"
    if enable:
        f += f":enable='{enable}'"
    return f

def box(x: str, y: str, w: str, h: str, color: str, enable: str | None = None) -> str:
    # Quote coordinates so FFmpeg expressions containing commas are parsed as one value.
    x = x.strip("'")
    y = y.strip("'")
    f = f"drawbox=x='{x}':y='{y}':w={w}:h={h}:color={color}:t=fill"
    if enable:
        f += f":enable='{enable}'"
    return f

def bg() -> list[str]:
    return [
        box("0", "0", "1080", "1920", "0x030712"),
        box("0", "0", "1080", "1920", "0x0b1220@0.22"),
        # Kinetic scanline + grid.
        box("0", "mod(90*t,1920)", "1080", "2", "0x38bdf8@0.10"),
        box("mod(180*t,1080)", "0", "2", "1920", "0x38bdf8@0.05"),
        dt("TECHMIND", "60", "74", 28, "0x67e8f9"),
        dt("AI / COMPUTER / AUTOMATION", "60", "112", 17, "0x64748b"),
    ]

def cursor(x: str, y: str, enable: str | None = None) -> list[str]:
    # Pointer + click ring. The ring appears only at action moments.
    out = [
        box(x, y, "13", "13", "white", enable),
        box(f"({x})+10", f"({y})+10", "2", "2", "0x67e8f9", enable),
    ]
    if enable:
        out.append(
            f"drawbox=x='({x})-18':y='({y})-18':w=48:h=48:color=0x67e8f9@0.35:t=4:enable='{enable}'"
        )
    return out

def common_title(f: list[str], kicker: str, title: str, line: str) -> None:
    f.extend([
        dt(kicker, "60", "250", 24, "0x67e8f9"),
        dt(title, "60", "292", 78, "white"),
        dt(line, "60", "388", 30, "0xcbd5e1"),
    ])

def scene_filter(kind: str, dur: float, kicker: str, title: str, line1: str, line2: str) -> str:
    f = bg()
    common_title(f, kicker, title, line1)

    if kind == "hook":
        # 0.0-1.0: task arrives; 1.0-2.0: cursor clicks; 2.0+: computer wakes up.
        f += [
            box("55", "510", "970", "1050", "0x0b1220"),
            box("80", "540", "910", "80", "0x111827"),
            dt("TASK RECEIVED", "115", "565", 24, "0x94a3b8"),
            dt("Open the latest report and verify it", "115", "680", 39, "white",
               "between(t,0.25,3.0)"),
            box("115", "760", "780", "2", "0x334155"),
            dt("AI AGENT", "115", "820", 22, "0x67e8f9"),
            dt("planning...", "115", "865", 28, "0xcbd5e1", "between(t,0.5,1.4)"),
            dt("opening apps...", "115", "865", 28, "0xcbd5e1", "between(t,1.4,2.3)"),
            dt("working...", "115", "865", 28, "0x86efac", "between(t,2.3,3.5)"),
            box("115", "960", "250", "150", "0x172554"),
            box("405", "960", "250", "150", "0x052e16"),
            box("695", "960", "250", "150", "0x1c1917"),
            dt("MAIL", "190", "1015", 31),
            dt("CODE", "475", "1015", 31),
            dt("TERM", "760", "1015", 31),
            box("115", "1200", "780", "10", "0x1e293b"),
            box("115", "1200", "780", "10", "0x38bdf8",
                "gte(t,1.0)"),
            *cursor(
                "120+620*min(max((t-0.8)/1.8,0),1)",
                "920",
                "between(t,0.75,3.2)"
            ),
            dt("COMPUTER ACTION STARTED", "115", "1300", 25, "0x67e8f9",
               "gte(t,1.7)"),
        ]

    elif kind == "apps":
        # Windows slide into a workspace; active window changes as cursor moves.
        f += [
            box("50", "500", "980", "1080", "0x0b1220"),
            dt("WORKSPACE", "90", "560", 20, "0x64748b"),
            box("95+min(max((t-0.2)*120,0),300)", "650", "270", "310", "0x172554",
                "between(t,0.2,2.8)"),
            box("405+min(max((t-1.0)*120,0),120)", "650", "270", "310", "0x052e16",
                "between(t,1.0,3.2)"),
            box("715+min(max((t-1.8)*120,0),0)", "650", "230", "310", "0x1c1917",
                "gte(t,1.8)"),
            dt("MAIL", "170", "750", 40, "white", "gte(t,0.35)"),
            dt("OPEN", "170", "815", 20, "0x67e8f9", "gte(t,0.5)"),
            dt("CODE", "475", "750", 40, "white", "gte(t,1.1)"),
            dt("RUN", "475", "815", 20, "0x86efac", "gte(t,1.3)"),
            dt("TERM", "770", "750", 34, "white", "gte(t,1.9)"),
            dt("EXEC", "770", "815", 20, "0xfbbf24", "gte(t,2.1)"),
            # Active underline jumps from app to app.
            box("135", "875", "190", "6", "0x38bdf8", "between(t,0.5,1.15)"),
            box("445", "875", "190", "6", "0x22c55e", "between(t,1.15,1.9)"),
            box("745", "875", "170", "6", "0xf59e0b", "gte(t,1.9)"),
            dt("OPEN  →  READ  →  ACT", "150", "1110", 33, "white"),
            box("150", "1180", "780", "9", "0x1e293b"),
            box("150", "1180", "780", "9", "0x38bdf8", "gte(t,0.7)"),
            dt(line2, "150", "1260", 25, "0x94a3b8"),
            *cursor("140+760*min(t/3.0,1)", "600", "between(t,0.35,3.1)"),
        ]

    elif kind == "browser":
        # Search bar types in, button gets clicked, results move upward.
        f += [
            box("45", "500", "990", "1080", "0xf8fafc"),
            box("45", "500", "990", "74", "0x1e293b"),
            box("180", "520", "760", "38", "0x334155"),
            dt("search", "205", "529", 19, "0x64748b"),
            dt("AI agent computer use", "285", "529", 19, "0xe2e8f0", "gte(t,0.45)"),
            box("860", "518", "55", "42", "0x2563eb"),
            dt("↵", "879", "524", 23, "white", "gte(t,1.1)"),
            box("95", "650", "890", "90", "0xe2e8f0", "gte(t,1.15)"),
            dt("AI agents that can use a computer", "130", "680", 25, "0x0f172a", "gte(t,1.15)"),
            box("95", "800-70*min(max(t-1.2,0),2)", "410", "250", "white", "gte(t,1.2)"),
            box("545", "800-70*min(max(t-1.2,0),2)", "440", "250", "white", "gte(t,1.2)"),
            dt("RESULT 01", "130", "845-70*min(max(t-1.2,0),2)", 21, "0x2563eb", "gte(t,1.2)"),
            dt("browser control", "130", "890-70*min(max(t-1.2,0),2)", 29, "0x0f172a", "gte(t,1.2)"),
            dt("RESULT 02", "580", "845-70*min(max(t-1.2,0),2)", 21, "0x2563eb", "gte(t,1.2)"),
            dt("computer use", "580", "890-70*min(max(t-1.2,0),2)", 29, "0x0f172a", "gte(t,1.2)"),
            dt("READ", "140", "1210", 23, "0x475569", "gte(t,1.8)"),
            dt("DECIDE", "420", "1210", 23, "0x475569", "gte(t,2.0)"),
            dt("NAVIGATE", "725", "1210", 23, "0x475569", "gte(t,2.2)"),
            dt("✓", "160", "1260", 40, "0x16a34a", "gte(t,1.9)"),
            dt("✓", "445", "1260", 40, "0x16a34a", "gte(t,2.1)"),
            dt("→", "770", "1260", 42, "0x2563eb", "gte(t,2.3)"),
            *cursor("250+520*min(t/2.7,1)", "585", "between(t,0.4,3.0)"),
        ]

    elif kind == "code":
        # Editor changes line-by-line, then terminal runs and reports success.
        f += [
            box("45", "500", "990", "1080", "0x0b1120"),
            box("45", "500", "990", "68", "0x111827"),
            dt("agent.py", "95", "518", 22, "0xe2e8f0"),
            dt("RUN", "835", "518", 20, "0x86efac", "gte(t,2.0)"),
            dt("01", "90", "620", 19, "0x64748b"),
            dt("task = browser.open(url)", "145", "620", 26, "0x93c5fd", "gte(t,0.25)"),
            dt("02", "90", "700", 19, "0x64748b"),
            dt("result = agent.read()", "145", "700", 26, "0x86efac", "gte(t,0.7)"),
            dt("03", "90", "780", 19, "0x64748b"),
            dt("assert result.ok", "145", "780", 26, "0xfde68a", "gte(t,1.15)"),
            dt("04", "90", "860", 19, "0x64748b"),
            dt("fix_and_retry()", "145", "860", 26, "0xf9a8d4", "gte(t,1.6)"),
            box("90", "950", "900", "340", "0x020617"),
            dt("$ python agent.py", "125", "1005", 25, "0x94a3b8", "gte(t,1.9)"),
            dt("> opening browser...", "125", "1065", 24, "0x67e8f9", "gte(t,2.15)"),
            dt("> tests passed", "125", "1125", 24, "0x86efac", "gte(t,2.45)"),
            dt("> task complete", "125", "1185", 24, "white", "gte(t,2.8)"),
            box("125", "1250", "760", "7", "0x1e293b"),
            box("125", "1250", "760", "7", "0x22c55e", "gte(t,2.4)"),
            *cursor("760", "840", "between(t,0.2,1.9)"),
        ]

    elif kind == "verify":
        # A connected graph lights up node-by-node; failure can trigger retry.
        f += [
            box("55", "500", "970", "1080", "0x0b1220"),
            dt("AUTONOMOUS TASK", "95", "560", 21, "0x64748b"),
            box("105", "690", "240", "155", "0x172554"),
            box("420", "690", "240", "155", "0x064e3b"),
            box("735", "690", "240", "155", "0x3b0764"),
            dt("PLAN", "180", "745", 31, "white"),
            dt("ACT", "500", "745", 31, "white"),
            dt("CHECK", "795", "745", 31, "white"),
            dt("→", "365", "738", 48, "0x475569", "gte(t,0.5)"),
            dt("→", "680", "738", 48, "0x475569", "gte(t,1.1)"),
            box("150", "900", "780", "250", "0x111827"),
            dt("VERIFYING RESULT", "190", "950", 24, "0x67e8f9"),
            dt("✓ browser action", "190", "1010", 27, "0x86efac", "gte(t,1.5)"),
            dt("✓ code check", "190", "1065", 27, "0x86efac", "gte(t,2.0)"),
            dt("✓ final output", "190", "1120", 27, "0x86efac", "gte(t,2.45)"),
            dt("DONE", "720", "1290", 52, "0x86efac", "gte(t,2.8)"),
            # Moving verification pulse.
            box("120+800*min(t/3.0,1)", "650", "18", "210", "0x67e8f9@0.35"),
            *cursor("165+720*min(t/2.8,1)", "1320", "between(t,1.4,3.2)"),
        ]

    else:
        # Ending is animated: mark builds, logo rises, CTA appears last.
        f += [
            box("55", "500", "970", "1080", "0x07111f"),
            dt("SYSTEM COMPLETE", "100", "620", 21, "0x86efac", "gte(t,0.2)"),
            dt("TECHMIND", "120", "760", 88, "0x67e8f9", "gte(t,0.55)"),
            dt("COMPUTER + AI", "120", "875", 43, "white", "gte(t,0.95)"),
            dt("PLAN  •  ACT  •  VERIFY", "120", "950", 28, "0xcbd5e1", "gte(t,1.25)"),
            box("120", "1035", "820", "8", "0x1e293b"),
            box("120", "1035", "820", "8", "0x38bdf8", "gte(t,1.3)"),
            dt(line1, "120", "1150", 29, "white", "gte(t,1.7)"),
            dt(line2, "120", "1220", 25, "0x94a3b8", "gte(t,2.1)"),
            dt("FOLLOW FOR PRACTICAL AI", "120", "1400", 22, "0x67e8f9", "gte(t,2.6)"),
            # Expanding glow rings.
            f"drawbox=x='430-80*sin(2*t)':y='700-80*sin(2*t)':w='220+160*sin(2*t)':h='220+160*sin(2*t)':color=0x38bdf8@0.10:t=6:enable='gte(t,0.6)'",
        ]

    # Fast lower progress rail, not a slide footer.
    f += [
        box("60", "1780", "960", "4", "0x1e293b"),
        f"drawbox=x=60:y=1780:w='960*min(t/{max(dur,0.1):.3f},1)':h=4:color=0x38bdf8:t=fill",
    ]
    return ",".join(f)

def make_scene(i: int, scene: tuple[str, str, str, str, str], dur: float) -> Path:
    global HERO
    kicker, title, line1, line2, kind = scene
    if i == 0 and HERO is not None and HERO.exists():
        return make_hero_scene(dur)
    out = OUT / f"scene_{i}.mp4"
    vf = scene_filter(kind, dur, kicker, title, line1, line2)
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x030712:s={W}x{H}:r={FPS}:d={dur:.3f}",
        "-vf", vf,
        "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p",
        str(out),
    ])
    return out

def main() -> None:
    global HERO
    # Install all optional free dependencies before creating the source frame.
    run(["python", "-m", "pip", "install", "--quiet", "edge-tts", "gradio_client", "pillow"])
    # One short free AI-video hero shot; all remaining scenes stay local/free.
    HERO = generate_free_wan_hero()
    run([
        "edge-tts", "--voice", "hi-IN-MadhurNeural", "--rate", "+8%",
        "--text", NARRATION, "--write-media", str(OUT / "voice.mp3")
    ])
    audio_duration = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", str(OUT / "voice.mp3")
    ], text=True).strip())
    scene_duration = audio_duration / len(SCENES)
    print(f"TTS duration={audio_duration:.2f}s; scene duration={scene_duration:.2f}s")

    clips = [make_scene(i, scene, scene_duration) for i, scene in enumerate(SCENES)]
    concat = OUT / "concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in clips), encoding="utf-8")

    silent = OUT / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
         "-c", "copy", str(silent)])

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
