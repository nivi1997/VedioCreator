from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
import openai
from moviepy.editor import ImageSequenceClip, AudioFileClip
import os
import tempfile

openai.api_key = "YOUR_OPENAI_API_KEY"

app = FastAPI()

@app.post("/generate-video/")
async def generate_video(
    audio_file: UploadFile = File(...),
    scene_description: str = Form(...)
):
    # Save uploaded audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(await audio_file.read())
        audio_path = temp_audio.name

    # Split scene description into lines (1 scene per line)
    scenes = [line.strip() for line in scene_description.split("\n") if line.strip()]

    image_paths = []
    for idx, scene in enumerate(scenes):
        print(f"Generating image {idx+1}/{len(scenes)}: {scene}")
        image = openai.images.generate(
            model="gpt-image-1",
            prompt=f"Cartoon style kids animation, colorful, {scene}",
            size="1024x576"
        )
        img_url = image.data[0].url

        # Save image locally
        img_path = f"output/scene_{idx}.png"
        os.system(f"curl -s {img_url} -o {img_path}")
        image_paths.append(img_path)

    # Combine images into a video
    audio_clip = AudioFileClip(audio_path)
    num_scenes = len(image_paths)
    duration_per_scene = audio_clip.duration / num_scenes

    clip = ImageSequenceClip(image_paths, durations=[duration_per_scene]*num_scenes)
    clip = clip.set_audio(audio_clip)

    output_path = f"output/final_video.mp4"
    clip.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

    return FileResponse(output_path, media_type="video/mp4", filename="final_video.mp4")
