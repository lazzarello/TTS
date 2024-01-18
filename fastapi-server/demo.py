import gradio as gr
import requests
import base64
import tempfile
import json
import os
import urllib.parse as urlparse


SERVER_URL = os.environ.get("TTS_API_ENDPOINT", 'http://localhost:8000')
OUTPUT = "./demo_outputs"
cloned_speakers = {}

print("Preparing file structure...")
if not os.path.exists(OUTPUT):
    os.mkdir(OUTPUT)
    os.mkdir(os.path.join(OUTPUT, "cloned_speakers"))
    os.mkdir(os.path.join(OUTPUT, "generated_audios"))
elif os.path.exists(os.path.join(OUTPUT, "cloned_speakers")):
    print("Loading existing cloned speakers...")
    for file in os.listdir(os.path.join(OUTPUT, "cloned_speakers")):
        if file.endswith(".json"):
            with open(os.path.join(OUTPUT, "cloned_speakers", file), "r") as fp:
                cloned_speakers[file[:-5]] = json.load(fp)
    print("Available cloned speakers:", ", ".join(cloned_speakers.keys()))

try:
    LANGUAGES = [
        "en",
        "es",
        "fr",
        "de",
        "it",
        "pt",
        "pl",
        "tr",
        "ru",
        "nl",
        "cs",
        "ar",
        "zh-cn",
        "hu",
        "ko",
        "ja",
        "hi"
    ]
    print("Available languages:", ", ".join(LANGUAGES))
    print("Getting metadata from server ...")
    VOICES = requests.get(SERVER_URL + "/v1/voices").json()
    print("Available voices:", ", ".join(VOICES["voices"]))
except:
    raise Exception("Please make sure the server is running first.")


def clone_speaker(upload_file, clone_speaker_name):
    files = {"files": ("reference.wav", open(upload_file, "rb"))}
    requests.post(SERVER_URL + "/v1/voices/add", files=files, name=clone_speaker_name).json()
    return clone_speaker_name, gr.Dropdown(choices=clone_speaker_name)

def tts(text, speaker_type, speaker_name_studio, speaker_name_custom, lang):
    idx = VOICES["voices"].index(speaker_name_studio)
    voice = urlparse.quote(VOICES["voices"][idx])
    generated_audio = requests.post(
        SERVER_URL + f"/v1/text-to-speech/{voice}",
        json={
            "text": text,
            "language": lang,
        }
    ).content
    generated_audio_path = os.path.join("demo_outputs", "generated_audios", next(tempfile._get_candidate_names()) + ".wav")
    with open(generated_audio_path, "wb") as fp:
        fp.write(base64.b64decode(generated_audio))
        return fp.name

with gr.Blocks() as demo:
    cloned_speaker_names = gr.State(list(cloned_speakers.keys()))
    with gr.Tab("TTS"):
        with gr.Column() as row4:
            with gr.Row() as col4:
                speaker_name_studio = gr.Dropdown(
                    label="Studio speaker",
                    choices=VOICES["voices"],
                    value="Asya Anara" if "Asya Anara" in VOICES["voices"] else None,
                )
                speaker_name_custom = gr.Dropdown(
                    label="Cloned speaker",
                    choices=cloned_speaker_names.value,
                    value=cloned_speaker_names.value[0] if len(cloned_speaker_names.value) != 0 else None,
                )
            speaker_type = gr.Dropdown(label="Speaker type", choices=["Studio", "Cloned"], value="Studio")
        with gr.Column() as col2:
            lang = gr.Dropdown(label="Language", choices=LANGUAGES, value="en")
            text = gr.Textbox(label="text", value="A quick brown fox jumps over the lazy dog.")
            tts_button = gr.Button(value="TTS")
        with gr.Column() as col3:
            generated_audio = gr.Audio(label="Generated audio", autoplay=True)
    with gr.Tab("Clone a new speaker"):
        with gr.Column() as col1:
            upload_file = gr.Audio(label="Upload reference audio", type="filepath")
            clone_speaker_name = gr.Textbox(label="Speaker name", value="default_speaker")
            clone_button = gr.Button(value="Clone speaker")

    clone_button.click(
        fn=clone_speaker,
        inputs=[upload_file, clone_speaker_name],
        outputs=[clone_speaker_name, speaker_name_custom],
    )

    tts_button.click(
        fn=tts,
        # this input is expecting the "speaker_name_custom" value to include the latent vector data
        # but I'm storing that on the server side now. Update the server to handle this data.
        # the value of speaker_name_custom will work the same as the presets, just be a string
        # that matches the speaker name
        inputs=[text, speaker_type, speaker_name_studio, speaker_name_custom, lang],
        outputs=[generated_audio],
    )

if __name__ == "__main__":
    print("Warming up server...this might be superstitious.")
    resp = requests.post(
        SERVER_URL + "/v1/text-to-speech/Asya%20Anara",
        json={
            "text": "This is a warmup request.",
            "language": "en",
        }
    )
    resp.raise_for_status()
    print("Starting the demo...")
    demo.launch(
        share=False,
        debug=True,
        server_port=3009,
        server_name="0.0.0.0",
    )
