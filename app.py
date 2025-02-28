import modal

app = modal.App(name="tooncrafter-sketchguidance")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements(
        "requirements.txt"
    )
    .add_local_python_source("scripts", "utils", "cldm", "lvdm", "ldm")
    .add_local_dir("configs", "/root/configs")
)

with image.imports():
    from scripts.gradio.i2v_test_application import Image2Video

CHECKPOINTS = "/checkpoints"
CONTROL_MODELS = "/control_models"
DATA = "/data"

checkpoints_volume = modal.Volume.from_name("tc-checkpoints", create_if_missing=True)
control_models_volume = modal.Volume.from_name("tc-control", create_if_missing=True)
data_volume = modal.Volume.from_name("tc-data", create_if_missing=True)

# @app.cls(
#     image=image,
#     gpu="A100-80GB",
#     volumes={CHECKPOINTS: checkpoints_volume, CONTROL_MODELS: control_models_volume, DATA: data_volume},
#     timeout=1000 # in seconds
# )
# class Model:
#     @modal.enter()
#     def enter(self):
#         import os
#         from huggingface_hub import hf_hub_download 

#         # Download checkpoint if not exists
#         ckpt_path = CHECKPOINTS + "/tooncrafter_512_interp_v1/model.ckpt"

#         if not os.path.exists(ckpt_path):
#             print("Downloading checkpoint files.")

#             hf_hub_download(
#                 repo_id="Doubiiu/ToonCrafter",
#                 filename="model.ckpt",
#                 local_dir= CHECKPOINTS + "/tooncrafter_512_interp_v1",
#             )

#         # Download pretrained SketchEncoder if not exists
#         sketch_encoder_path = CONTROL_MODELS + "/sketch_encoder.ckpt"

#         if not os.path.exists(sketch_encoder_path):
#             print("Downloading SketchEncoder files.")

#             hf_hub_download(
#                 repo_id="Doubiiu/ToonCrafter",
#                 filename="sketch_encoder.ckpt",
#                 local_dir= CONTROL_MODELS,
#             )
    
# @modal.method()
# def inference(self, image1_bytes, image2_bytes, frame_guides_path):
#     from PIL import Image
#     from io import BytesIO
#     from pathlib import Path
#     import cv2

#     image1 = Image.open(BytesIO(image1_bytes))
#     image2 = Image.open(BytesIO(image2_bytes))

#     # Read the video file
#     fgp = Path(frame_guides_path)
#     cap = cv2.VideoCapture(fgp)

#     if not fgp.exists():
#         raise FileNotFoundError(f"Frame guides file not found: {frame_guides_path}")

#     if not cap.isOpened():
#         raise ValueError(f"Error opening video file: {frame_guides_path}")

#     frame_guides = []
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frame_guides.append(frame)

#     cap.release()

#     image2video = Image2Video(DATA, resolution='320_512')

#     image2video.get_image(
#         image=image1,
#         prompt="A girl turns around",
#         steps=50,
#         cfg_scale=7.5,
#         eta=1.0,
#         fs=3,
#         seed=123,
#         image2=image2,
#         frame_guides=frame_guides, # sketch video
#         control_scale=0.6
#     )

@app.function(
    image=image,
    gpu="A100-80GB",
    volumes={CHECKPOINTS: checkpoints_volume, CONTROL_MODELS: control_models_volume, DATA: data_volume},
    timeout=1000 # in seconds
)
def inference(image1_bytes, image2_bytes, frame_guides):
    from PIL import Image
    from io import BytesIO
    from pathlib import Path
    import cv2
    import numpy as np

    image1 = Image.open(BytesIO(image1_bytes))
    image1 = np.array(image1)
    image2 = Image.open(BytesIO(image2_bytes))
    image2 = np.array(image2) # wrong!

    # Read the video file
    video_path = "video.mp4"

    with open(video_path, "wb") as f:
        f.write(frame_guides)

    image2video = Image2Video(DATA, resolution='320_512')

    image2video.get_image(
        image=image1,
        prompt="A girl turns around",
        steps=50,
        cfg_scale=7.5,
        eta=1.0,
        fs=3,
        seed=123,
        image2=image2,
        frame_guides=video_path, # sketch video
        control_scale=0.6
    )

@app.local_entrypoint()
def main():
    from pathlib import Path

    image1_bytes = Path("assets/sketch_sample/frame_1.png").read_bytes()
    image2_bytes = Path("assets/sketch_sample/frame_2.png").read_bytes()
    frame_guides_bytes = Path("assets/sketch_sample/sample.mov").read_bytes()

    # check if on volume?
    # with data_volume.batch_upload() as batch:
    #     batch.put_file("assets/sketch_sample/sample.mov", frame_guides_path)

    inference.remote(
        image1_bytes=image1_bytes,
        image2_bytes=image2_bytes,
        frame_guides=frame_guides_bytes,
    )