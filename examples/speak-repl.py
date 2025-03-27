import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize TTS with a pre-trained model
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)

print("Text-to-Speech REPL (type 'exit' to quit)")
print("------------------------------------------")

while True:
    # Get user input
    text = input("Enter text to speak: ")
    
    # Exit condition
    if text.lower() == 'exit':
        print("Exiting...")
        break
    
    # Skip empty input
    if not text.strip():
        continue
    
    print(f"Speaking: {text}")
    
    # Generate speech
    tts.tts_to_file(text=text, file_path="output.wav")
    
    # Play the audio (this is platform-dependent)
    try:
        import platform
        import os
        
        system = platform.system()
        if system == 'Darwin':  # macOS
            os.system("afplay output.wav")
        elif system == 'Linux':
            # Use Pipewire's pw-play instead of aplay
            os.system("pw-play output.wav")
        elif system == 'Windows':
            os.system("start output.wav")
        else:
            print("Audio saved to output.wav (couldn't auto-play on this platform)")
    except Exception as e:
        print(f"Error playing audio: {e}")
        print("Audio saved to output.wav")
