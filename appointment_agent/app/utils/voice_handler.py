# import os
# import httpx
# import time
# from typing import Optional
#
# DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
#
#
# class VoiceHandler:
#     def __init__(self, session_id: str):
#         self.session_id = session_id
#         self.current_transcript = ""
#         self.last_speech_time = time.time()
#         self.is_processing = False
#
#     async def transcribe_with_deepgram(self, audio_data: bytes) -> Optional[str]:
#         """Send audio to Deepgram and get transcription"""
#         try:
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     "https://api.deepgram.com/v1/listen",
#                     headers={
#                         "Authorization": f"Token {DEEPGRAM_API_KEY}",
#                         "Content-Type": "audio/wav"
#                     },
#                     content=audio_data,
#                     timeout=30.0
#                 )
#
#                 if response.status_code == 200:
#                     result = response.json()
#                     transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
#                     return transcript.strip()
#                 return None
#         except Exception as e:
#             print(f"Deepgram error: {e}")
#             return None
#
#     async def speak_with_elevenlabs(self, text: str) -> Optional[bytes]:
#         """Convert text to speech with ElevenLabs"""
#         try:
#             print(f"ElevenLabs request - Text: '{text}'")
#
#             async with httpx.AsyncClient() as client:
#                 response = await client.post(
#                     f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
#                     headers={
#                         "xi-api-key": ELEVENLABS_API_KEY,
#                         "Content-Type": "application/json"
#                     },
#                     json={
#                         "text": text,
#                         "model_id": "eleven_turbo_v2_5",
#                         "voice_settings": {
#                             "stability": 0.5,
#                             "similarity_boost": 0.75
#                         }
#                     },
#                     timeout=30.0
#                 )
#
#                 print(f"ElevenLabs status code: {response.status_code}")
#
#                 if response.status_code == 200:
#                     audio_bytes = response.content
#                     print(f"Successfully got {len(audio_bytes)} bytes from ElevenLabs")
#                     return audio_bytes
#                 else:
#                     print(f"ElevenLabs error: {response.status_code}")
#                     print(f"Response: {response.text}")
#                     return None
#
#         except Exception as e:
#             print(f"ElevenLabs exception: {e}")
#             import traceback
#             traceback.print_exc()
#             return None


# appointment_agent/app/utils/voice_handler.py

import os
import httpx
from typing import Optional

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")


class VoiceHandler:
    def __init__(self):
        self.current_transcript = ""
        self.is_processing = False

    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using ElevenLabs"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
                    headers={
                        "xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_turbo_v2_5",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                            "use_speaker_boost": True
                        }
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    return response.content
                return None

        except Exception as e:
            print(f"[VoiceHandler] ElevenLabs error: {e}")
            return None
