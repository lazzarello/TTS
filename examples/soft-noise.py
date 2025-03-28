import torch
from TTS.api import TTS
import subprocess
import io

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize TTS with a pre-trained model
tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)

def play_audio_with_pipewire(wav_data, sample_rate=22050):
    """Play audio using pw-cat without saving to a file"""
    try:
        # Create a subprocess with pw-cat
        process = subprocess.Popen(
            ["pw-cat", "--rate", str(sample_rate), "--playback", "--channels", "1", "-"],
            stdin=subprocess.PIPE
        )
        # Write the wav data to the process's stdin
        process.stdin.write(wav_data)
        process.stdin.close()
        # Wait for the process to complete
        process.wait()
        return True
    except Exception as e:
        print(f"Error playing audio with pw-cat: {e}")
        return False

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
    wav = tts.tts(text=text)
    
    # Convert numpy array to WAV bytes
    import scipy.io.wavfile
    import numpy as np
    
    # Convert list to numpy array if needed
    if isinstance(wav, list):
        wav = np.array(wav)
    
    wav_io = io.BytesIO()
    scipy.io.wavfile.write(wav_io, 22050, wav)
    wav_data = wav_io.getvalue()
    
    # Play the audio using Pipewire
    if not play_audio_with_pipewire(wav_data):
        # Fallback to platform-specific methods if pw-cat fails
        try:
            import platform
            import os
            
            # Save to file for fallback
            with open("output.wav", "wb") as f:
                f.write(wav_data)
            
            system = platform.system()
            if system == 'Darwin':  # macOS
                os.system("afplay output.wav")
            elif system == 'Linux':
                os.system("pw-play output.wav")
            elif system == 'Windows':
                os.system("start output.wav")
            else:
                print("Audio saved to output.wav (couldn't auto-play on this platform)")
        except Exception as e:
            print(f"Error playing audio: {e}")
            print("Audio saved to output.wav")
