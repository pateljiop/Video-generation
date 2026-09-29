#!/usr/bin/env python3
"""Daily TechMind generator for Render Cron.

Uses the existing free Render video service. No paid video API is required.
"""
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

RENDER_URL = os.getenv("RENDER_URL", "https://pixelle-video-31d7.onrender.com").rstrip("/")
POLL_SECONDS = 10
MAX_POLLS = 120
START_RETRIES = 3

TOPICS = [
    "AI Agents ab sirf chat nahi karte. Ye agents computer par apps khol sakte hain, web browse kar sakte hain, code likh sakte hain aur tasks execute kar sakte hain. TechMind: AI jo aapke computer ke saath kaam karta hai.",
    "AI coding agents code likhne ke saath bugs bhi detect aur fix kar sakte hain. TechMind: developer workflow ka next step.",
    "AI browsers web pages ko samajhkar multi-step tasks automate kar rahe hain. TechMind: browser automation ka naya era.",
    "Local AI agents privacy ke liye useful ho sakte hain kyunki kuch tasks device par hi run kiye ja sakte hain. TechMind: local AI ka practical use.",
    "AI agents ko tools dene par wo sirf answer nahi, real actions bhi perform kar sakte hain. TechMind: tool-using AI explained.",
    "Computer-use AI screen ko dekhkar clicks, typing aur navigation jaise actions automate kar sakta hai. TechMind: computer control with AI.",
    "AI agent workflow me planning, tool use aur verification teen important steps hain. TechMind: agent loop simple language me.",
]

def post_json(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "techmind-daily-cron/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "techmind-daily-cron/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    day_index = datetime.now(timezone.utc).timetuple().tm_yday - 1
    prompt = TOPICS[day_index % len(TOPICS)]
    payload = {
        "text": prompt,
        "mode": "fixed",
        "n_scenes": 1,
        "title": "TechMind Daily",
        "frame_template": "1080x1920/static_default.html",
        "tts_workflow": "selfhost/tts_edge.json",
    }

    task_id = None
    for attempt in range(1, START_RETRIES + 1):
        try:
            result = post_json(f"{RENDER_URL}/api/video/generate/async", payload)
            task_id = result.get("task_id")
            if task_id:
                print(f"Generation started: {task_id}")
                break
            print(f"Attempt {attempt}: response had no task_id: {result}")
        except Exception as exc:
            print(f"Attempt {attempt}: start failed: {exc}")
        if attempt < START_RETRIES:
            time.sleep(15)

    if not task_id:
        raise RuntimeError("Could not start daily TechMind generation after 3 attempts")

    for poll in range(1, MAX_POLLS + 1):
        try:
            status = get_json(f"{RENDER_URL}/api/tasks/{task_id}")
            state = status.get("status")
            print(f"Poll {poll}/{MAX_POLLS}: {state}")
            if state == "completed":
                video_url = (status.get("result") or {}).get("video_url")
                if not video_url:
                    raise RuntimeError(f"Task completed without video URL: {status}")
                print(f"VIDEO_URL={video_url}")
                return
            if state in {"failed", "cancelled"}:
                raise RuntimeError(f"Daily TechMind task {state}: {status}")
        except urllib.error.URLError as exc:
            print(f"Poll {poll}: temporary network error: {exc}")
        time.sleep(POLL_SECONDS)

    raise TimeoutError(f"Daily TechMind generation timed out: {task_id}")

if __name__ == "__main__":
    main()
