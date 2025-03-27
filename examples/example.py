import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize TTS with a pre-trained model
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)

# Generate speech and save to file
tts.tts_to_file(text="Hello world!", file_path="output.wav")