from flask import Flask, request, jsonify
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

app = Flask(__name__)

OUTPUT_DIR = "/app/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/")
def home():
    return "Video Agent Python Worker is running!"


@app.route("/health")
def health():
    return {"status": "ok"}


def create_scene_image(text, filename):
    width = 1280
    height = 720

    image = Image.new("RGB", (width, height), (20, 20, 30))
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "/usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf",
            42
        )
    except:
        font = ImageFont.load_default()

    wrapped_text = textwrap.fill(text, width=42)

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped_text,
        font=font,
        spacing=12
    )

    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.multiline_text(
        (x, y),
        wrapped_text,
        font=font,
        fill="white",
        spacing=12,
        align="center"
    )

    image.save(filename)


@app.route("/generate-video", methods=["POST"])
def generate_video():
    data = request.get_json()
    scenes = data.get("scenes", [])

    if not scenes:
        return jsonify({"error": "No scenes received"}), 400

    clips = []

    for index, scene in enumerate(scenes):
        text = scene.get("scene_text", "")
        duration = scene.get("duration", 5)

        image_file = os.path.join(
            OUTPUT_DIR,
            f"scene_{index + 1}.png"
        )

        create_scene_image(text, image_file)

        clip = ImageClip(image_file).set_duration(duration)
        clips.append(clip)

    final_video = concatenate_videoclips(
        clips,
        method="compose"
    )

    output_file = os.path.join(
        OUTPUT_DIR,
        "ai_social_media_video.mp4"
    )

    final_video.write_videofile(
        output_file,
        fps=24,
        codec="libx264",
        audio=False
    )

    final_video.close()

    return jsonify({
        "status": "success",
        "video": output_file
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000
    )