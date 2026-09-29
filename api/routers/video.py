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

"""
Video generation endpoints

Supports both synchronous and asynchronous video generation.
"""

import os
import asyncio
import subprocess
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.video import (
    VideoGenerateRequest,
    VideoGenerateResponse,
    VideoGenerateAsyncResponse,
)
from api.tasks import task_manager, TaskType
from api.openrouter_video import generate_video as generate_openrouter_video

router = APIRouter(prefix="/video", tags=["Video Generation"])


async def generate_free_motion_video(text: str, title: str | None = None, fps: int = 30) -> dict:
    """Create a genuinely free TechMind-style MP4 using Edge TTS + FFmpeg only.

    No paid video/image API, ComfyUI, RunningHub, or browser rendering is used.
    """
    import edge_tts

    task_id = uuid4().hex[:12]
    out_dir = Path("output") / f"free_{task_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "voice.mp3"
    text_path = out_dir / "body.txt"
    title_path = out_dir / "title.txt"
    video_path = out_dir / "techmind.mp4"

    script = text.strip()
    if not script:
        script = "AI agents do more than chat. They can control apps, browse the web, write code, and execute tasks."

    # Edge TTS is used as the free narration layer.
    communicate = edge_tts.Communicate(script, voice="en-US-AriaNeural", rate="+8%")
    await communicate.save(str(audio_path))

    body = (script.replace("\\r", "").replace("\\n", " \\n").strip())[:900]
    text_path.write_text(body, encoding="utf-8")
    title_text = (title or "TECHMIND").upper().replace(":", " - ")[:60]
    title_path.write_text(title_text, encoding="utf-8")
    text_file = str(text_path.resolve())
    title_file = str(title_path.resolve())

    filter_graph = (
        "drawgrid=w=120:h=120:t=1:c=0x2b3954@0.22,"
        f"drawtext=fontcolor=0x67e8f9:fontsize=34:x=(w-text_w)/2:y=80:"
        f"textfile='{title_file}':shadowcolor=0x000000@0.7:shadowx=3:shadowy=3,"
        f"drawtext=fontcolor=white:fontsize=18:line_spacing=8:x=25:y=220:"
        f"textfile='{text_file}':box=1:boxcolor=0x0b1220@0.82:boxborderw=16"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x050914:s=360x640:r={min(fps,15)}",
        "-i", str(audio_path),
        "-vf", filter_graph,
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", str(video_path),
    ]

    proc = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0 or not video_path.exists() or video_path.stat().st_size == 0:
        raise RuntimeError(f"Free FFmpeg video generation failed: {proc.stderr[-2000:]}")

    probe = await asyncio.to_thread(subprocess.run, [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)
    ], capture_output=True, text=True, timeout=30)
    try:
        duration = float(probe.stdout.strip())
    except Exception:
        duration = 0.0

    return {"video_path": str(video_path), "duration": duration, "file_size": video_path.stat().st_size}

@router.get("/openrouter/models")
async def openrouter_video_models():
    """Return the currently available OpenRouter video models without exposing the API key."""
    import httpx

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENROUTER_API_KEY is not configured")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/videos/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json()
        return {
            "data": [
                {
                    "id": item.get("id"),
                    "pricing": item.get("pricing"),
                    "supported_parameters": item.get("supported_parameters"),
                    "supported": item.get("supported"),
                }
                for item in data.get("data", [])
            ]
        }
    except Exception as e:
        logger.error(f"OpenRouter video model lookup error: {e}")
        raise HTTPException(status_code=502, detail=str(e))



def path_to_url(request: Request, file_path: str) -> str:
    """
    Convert file path to accessible URL
    
    Handles both absolute and relative paths, extracting the path relative
    to the output directory for URL construction.
    
    Args:
        request: FastAPI Request object (provides base_url from actual request)
        file_path: Absolute or relative file path
    
    Returns:
        Full URL to access the file
    
    Examples:
        Windows: G:\\...\\output\\20251205_233630_c939\\final.mp4
              -> http://localhost:8000/api/files/20251205_233630_c939/final.mp4
        
        Linux:   /home/user/.../output/20251205_233630_c939/final.mp4
              -> http://localhost:8000/api/files/20251205_233630_c939/final.mp4
        
        Domain:  With domain request -> https://your-domain.com/api/files/...
    """
    from pathlib import Path
    import os
    
    # Normalize path separators to forward slashes first (for cross-platform compatibility)
    file_path = file_path.replace("\\", "/")
    
    # Check if it's an absolute path (works for both Windows and Linux)
    is_absolute = os.path.isabs(file_path) or Path(file_path).is_absolute()
    
    if is_absolute:
        # Find "output" in the path and get everything after it
        # Split by / to work with normalized paths
        parts = file_path.split("/")
        try:
            output_idx = parts.index("output")
            # Get all parts after "output" and join them
            relative_parts = parts[output_idx + 1:]
            file_path = "/".join(relative_parts)
        except ValueError:
            # If "output" not in path, use the filename only
            file_path = Path(file_path).name
    else:
        # If relative path starting with "output/", remove it
        if file_path.startswith("output/"):
            file_path = file_path[7:]  # Remove "output/"
    
    # Build URL using request's base_url (automatically matches the request host)
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/api/files/{file_path}"


@router.post("/generate/sync", response_model=VideoGenerateResponse)
async def generate_video_sync(
    request_body: VideoGenerateRequest,
    pixelle_video: PixelleVideoDep,
    request: Request
):
    """
    Generate video synchronously
    
    This endpoint blocks until video generation is complete.
    Suitable for small videos (< 30 seconds).
    
    **Note**: May timeout for large videos. Use `/generate/async` instead.
    
    Request body includes all video generation parameters.
    See VideoGenerateRequest schema for details.
    
    Returns path to generated video, duration, and file size.
    """
    try:
        logger.info(f"Sync video generation: {request_body.text[:50]}...")
        
        # Auto-determine media_width and media_height from template meta tags (required)
        if not request_body.frame_template:
            raise ValueError("frame_template is required to determine media size")
        
        from pixelle_video.services.frame_html import HTMLFrameGenerator
        from pixelle_video.utils.template_util import resolve_template_path
        template_path = resolve_template_path(request_body.frame_template)
        generator = HTMLFrameGenerator(template_path)
        media_width, media_height = generator.get_media_size()
        logger.debug(f"Auto-determined media size from template: {media_width}x{media_height}")
        
        # Build video generation parameters
        video_params = {
            "text": request_body.text,
            "mode": request_body.mode,
            "title": request_body.title,
            "n_scenes": request_body.n_scenes,
            "min_narration_words": request_body.min_narration_words,
            "max_narration_words": request_body.max_narration_words,
            "min_image_prompt_words": request_body.min_image_prompt_words,
            "max_image_prompt_words": request_body.max_image_prompt_words,
            "media_width": media_width,
            "media_height": media_height,
            "media_workflow": request_body.media_workflow,
            "video_fps": request_body.video_fps,
            "frame_template": request_body.frame_template,
            "prompt_prefix": request_body.prompt_prefix,
            "bgm_path": request_body.bgm_path,
            "bgm_volume": request_body.bgm_volume,
        }
        
        # Add TTS workflow if specified
        if request_body.tts_workflow:
            video_params["tts_workflow"] = request_body.tts_workflow
        
        # Add ref_audio if specified
        if request_body.ref_audio:
            video_params["ref_audio"] = request_body.ref_audio
        
        # Legacy voice_id support (deprecated)
        if request_body.voice_id:
            logger.warning("voice_id parameter is deprecated, please use tts_workflow instead")
            video_params["voice_id"] = request_body.voice_id
        
        # Add custom template parameters if specified
        if request_body.template_params:
            video_params["template_params"] = request_body.template_params
        
        # Call video generator service
        result = await pixelle_video.generate_video(**video_params)
        
        # Get file size
        file_size = os.path.getsize(result.video_path) if os.path.exists(result.video_path) else 0
        
        # Convert path to URL
        video_url = path_to_url(request, result.video_path)
        
        return VideoGenerateResponse(
            video_url=video_url,
            duration=result.duration,
            file_size=file_size
        )
        
    except Exception as e:
        logger.error(f"Sync video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/async", response_model=VideoGenerateAsyncResponse)
async def generate_video_async(
    request_body: VideoGenerateRequest,
    pixelle_video: PixelleVideoDep,
    request: Request
):
    """
    Generate video asynchronously
    
    Creates a background task for video generation.
    Returns immediately with a task_id for tracking progress.
    
    **Workflow:**
    1. Submit video generation request
    2. Receive task_id in response
    3. Poll `/api/tasks/{task_id}` to check status
    4. When status is "completed", retrieve video from result
    
    Request body includes all video generation parameters.
    See VideoGenerateRequest schema for details.
    
    Returns task_id for tracking progress.
    """
    try:
        logger.info(f"Async video generation: {request_body.text[:50]}...")

        # Prefer OpenRouter only when an explicitly enabled paid video model is configured.
        # The OpenRouter free router is text/image-only, so free mode falls back to Pixelle's
        # native pipeline instead of sending an unsupported /videos request.
        openrouter_model = os.getenv("OPENROUTER_VIDEO_MODEL", "").strip()
        use_openrouter = bool(os.getenv("OPENROUTER_API_KEY") and openrouter_model and not openrouter_model.endswith(":free"))
        if use_openrouter:
            task = task_manager.create_task(
                task_type=TaskType.VIDEO_GENERATION,
                request_params=request_body.model_dump()
            )

            async def execute_openrouter_generation():
                aspect_ratio = "16:9"
                if request_body.frame_template and "1080x1920" in request_body.frame_template:
                    aspect_ratio = "9:16"
                elif request_body.frame_template and "1080x1080" in request_body.frame_template:
                    aspect_ratio = "1:1"

                result = await generate_openrouter_video(
                    request_body.text,
                    model=openrouter_model,
                    duration=5,
                    aspect_ratio=aspect_ratio,
                    resolution=os.getenv("OPENROUTER_VIDEO_RESOLUTION", "720p"),
                    generate_audio=False,
                )
                return {
                    "video_url": path_to_url(request, result["video_path"]),
                    "duration": result["duration"],
                    "file_size": result["file_size"],
                    "provider": result["provider"],
                    "model": result["model"],
                    "job_id": result["job_id"],
                    "usage": result.get("usage"),
                }

            await task_manager.execute_task(task_id=task.task_id, coro_func=execute_openrouter_generation)
            return VideoGenerateAsyncResponse(task_id=task.task_id)

        # Create task
        task = task_manager.create_task(
            task_type=TaskType.VIDEO_GENERATION,
            request_params=request_body.model_dump()
        )

        # In free mode, bypass the heavyweight browser/ComfyUI pipeline entirely.
        # This guarantees that no paid video/image provider is called.
        if not use_openrouter:
            async def execute_free_generation():
                result = await generate_free_motion_video(
                    request_body.text,
                    title=request_body.title or "TechMind",
                    fps=request_body.video_fps,
                )
                return {
                    "video_url": path_to_url(request, result["video_path"]),
                    "duration": result["duration"],
                    "file_size": result["file_size"],
                    "provider": "free-local-ffmpeg-edge-tts",
                    "model": "none",
                }

            await task_manager.execute_task(task_id=task.task_id, coro_func=execute_free_generation)
            return VideoGenerateAsyncResponse(task_id=task.task_id)

        # Define async execution function
        async def execute_video_generation():
            """Execute video generation in background"""
            # Auto-determine media_width and media_height from template meta tags (required)
            if not request_body.frame_template:
                raise ValueError("frame_template is required to determine media size")
            
            from pixelle_video.services.frame_html import HTMLFrameGenerator
            from pixelle_video.utils.template_util import resolve_template_path
            template_path = resolve_template_path(request_body.frame_template)
            generator = HTMLFrameGenerator(template_path)
            media_width, media_height = generator.get_media_size()
            logger.debug(f"Auto-determined media size from template: {media_width}x{media_height}")
            
            # Build video generation parameters
            video_params = {
                "text": request_body.text,
                "mode": request_body.mode,
                "title": request_body.title,
                "n_scenes": request_body.n_scenes,
                "min_narration_words": request_body.min_narration_words,
                "max_narration_words": request_body.max_narration_words,
                "min_image_prompt_words": request_body.min_image_prompt_words,
                "max_image_prompt_words": request_body.max_image_prompt_words,
                "media_width": media_width,
                "media_height": media_height,
                "media_workflow": request_body.media_workflow,
                "video_fps": request_body.video_fps,
                "frame_template": request_body.frame_template,
                "prompt_prefix": request_body.prompt_prefix,
                "bgm_path": request_body.bgm_path,
                "bgm_volume": request_body.bgm_volume,
                # Progress callback can be added here if needed
                # "progress_callback": lambda event: task_manager.update_progress(...)
            }
            
            # Add TTS workflow if specified
            if request_body.tts_workflow:
                video_params["tts_workflow"] = request_body.tts_workflow
            
            # Add ref_audio if specified
            if request_body.ref_audio:
                video_params["ref_audio"] = request_body.ref_audio
            
            # Legacy voice_id support (deprecated)
            if request_body.voice_id:
                logger.warning("voice_id parameter is deprecated, please use tts_workflow instead")
                video_params["voice_id"] = request_body.voice_id
            
            # Add custom template parameters if specified
            if request_body.template_params:
                video_params["template_params"] = request_body.template_params
            
            result = await pixelle_video.generate_video(**video_params)
            
            # Get file size
            file_size = os.path.getsize(result.video_path) if os.path.exists(result.video_path) else 0
            
            # Convert path to URL
            video_url = path_to_url(request, result.video_path)
            
            return {
                "video_url": video_url,
                "duration": result.duration,
                "file_size": file_size
            }
        
        # Start execution
        await task_manager.execute_task(
            task_id=task.task_id,
            coro_func=execute_video_generation
        )
        
        return VideoGenerateAsyncResponse(
            task_id=task.task_id
        )
        
    except Exception as e:
        logger.error(f"Async video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

