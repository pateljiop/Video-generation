# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""OpenRouter hosted video generation bridge for Pixelle-Video."""

import asyncio
import os
from pathlib import Path
import httpx
from loguru import logger


BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "bytedance/seedance-2.0:free"


def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


async def generate_video(
    prompt: str,
    *,
    model: str | None = None,
    duration: int = 5,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    generate_audio: bool = False,
    output_dir: str = "output/openrouter",
) -> dict:
    """Submit an OpenRouter video job, poll it, and save the MP4 locally."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    selected_model = model or os.getenv("OPENROUTER_VIDEO_MODEL") or DEFAULT_MODEL
    duration = max(3, min(int(duration), 15))
    if aspect_ratio not in {"16:9", "9:16", "1:1"}:
        aspect_ratio = "16:9"

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": generate_audio,
    }

    timeout = httpx.Timeout(60.0, connect=20.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{BASE_URL}/videos",
            headers=_headers(api_key),
            json=payload,
        )
        if response.is_error:
            logger.error(
                "OpenRouter video submit failed: status=%s body=%s",
                response.status_code,
                response.text[:2000],
            )
            response.raise_for_status()
        job = response.json()

        job_id = job["id"]
        polling_url = job.get("polling_url") or f"{BASE_URL}/videos/{job_id}"
        logger.info(f"OpenRouter video job submitted: {job_id}")

        for _ in range(60):
            await asyncio.sleep(10)
            poll = await client.get(polling_url, headers=_headers(api_key))
            poll.raise_for_status()
            status = poll.json()

            state = status.get("status")
            logger.info(f"OpenRouter video job {job_id}: {state}")

            if state == "completed":
                urls = status.get("unsigned_urls") or []
                if not urls:
                    content_url = f"{BASE_URL}/videos/{job_id}/content?index=0"
                else:
                    content_url = urls[0]

                video_response = await client.get(
                    content_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    follow_redirects=True,
                )
                video_response.raise_for_status()

                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                target = output_path / f"{job_id}.mp4"
                target.write_bytes(video_response.content)

                return {
                    "provider": "openrouter",
                    "model": selected_model,
                    "job_id": job_id,
                    "video_path": str(target),
                    "file_size": target.stat().st_size,
                    "duration": duration,
                    "usage": status.get("usage"),
                }

            if state in {"failed", "cancelled", "expired"}:
                detail = status.get("error") or f"OpenRouter job {state}"
                raise RuntimeError(str(detail))

        raise TimeoutError(f"OpenRouter video job timed out: {job_id}")
