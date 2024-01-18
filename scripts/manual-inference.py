from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import torch, torchaudio
import os

config = XttsConfig()
config.load_json(f"{os.getenv('HOME', '/home/lee')}/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2/config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir=f"{os.getenv('HOME', '/home/lee')}/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2/", use_deepspeed=True)
model.cuda()

print(repr(model.speaker_manager.speakers.keys()))
print(type(model.speaker_manager.speakers['Claribel Dervla']['speaker_embedding']))
'''
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["/home/lee/Downloads/lee-reading-into-phone.wav"])

out = model.inference(
    "It was the best of times. It was the worst of times. It was the combination best of times and worst of times.",
    "en",
    gpt_cond_latent,
    speaker_embedding,
    temperature=0.4,
    length_penalty=1.0,
    repetition_penalty=2.5,
    top_k=40,
    top_p=0.8,
    speed=1.0,
    enable_text_splitting=False
)
torchaudio.save("out.wav", torch.tensor(out["wav"]).unsqueeze(0), 24000)
'''