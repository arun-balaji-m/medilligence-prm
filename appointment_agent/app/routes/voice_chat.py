from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import asyncio
import json
import os
import websockets
from appointment_agent.app.database import get_db
from appointment_agent.app.utils.voice_handler import VoiceHandler
from appointment_agent.app.utils.ai_handler import process_chat_message, add_function_result
from appointment_agent.app import crud
from datetime import datetime

router = APIRouter(prefix="/api/voice", tags=["voice"])

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# Welcome message for voice
WELCOME_MESSAGE = "Hello! I'm your medical appointment assistant. I can help you book appointments, check available slots, or manage your existing appointments. How can I help you today?"


@router.get("/test-keys")
async def test_api_keys():
    """Test if API keys are configured"""
    return {
        "deepgram": "configured" if DEEPGRAM_API_KEY else "missing",
        "deepgram_length": len(DEEPGRAM_API_KEY) if DEEPGRAM_API_KEY else 0,
        "deepgram_prefix": DEEPGRAM_API_KEY[:10] if DEEPGRAM_API_KEY else "none",
        "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing"
    }


@router.get("/test-deepgram")
async def test_deepgram_connection():
    """Test Deepgram WebSocket connection"""
    try:
        deepgram_url = (
            "wss://api.deepgram.com/v1/listen?"
            "model=nova-2"
            "&encoding=linear16"
            "&sample_rate=16000"
            "&channels=1"
            "&interim_results=true"
            "&vad_events=true"
        )

        async with websockets.connect(
                deepgram_url,
                additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
                ping_interval=5,
                ping_timeout=10
        ) as ws:
            # Send a test message
            await ws.send(json.dumps({"type": "KeepAlive"}))

            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)

            return {
                "status": "success",
                "message": "Deepgram connection works!",
                "response": response
            }
    except asyncio.TimeoutError:
        return {
            "status": "error",
            "message": "Deepgram timeout - API key might be invalid or no credits"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def execute_function(function_name: str, function_args: dict, db: Session):
    """Execute the requested function and return result"""
    try:
        if function_name == "getPatientDetails":
            patient = crud.get_patient_by_mobile(db, function_args["mobile_number"])
            if patient:
                return json.dumps({
                    "success": True,
                    "data": {
                        "id": patient.id,
                        "patient_name": patient.patient_name,
                        "patient_mrn": patient.patient_mrn,
                        "dob": str(patient.dob) if patient.dob else None,
                        "gender": patient.gender,
                        "mobile_number": patient.mobile_number,
                        "email": patient.email
                    }
                })
            else:
                return json.dumps({"success": False, "message": "Patient not found"})

        elif function_name == "getDoctorDepartmentDetails":
            doctors = crud.get_doctors_by_name_or_department(
                db,
                function_args.get("doctor_name"),
                function_args.get("specialization")
            )
            if doctors:
                return json.dumps({
                    "success": True,
                    "data": [
                        {
                            "id": doc.id,
                            "doctor_name": doc.doctor_name,
                            "specialization": doc.specialization
                        }
                        for doc in doctors
                    ]
                })
            else:
                return json.dumps({"success": False, "message": "No doctors found"})

        elif function_name == "getAvailableSlots":
            date_str = function_args["appointment_date"]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")

            slots = crud.get_available_slots(
                db,
                function_args.get("doctor_id"),
                None,
                date_obj
            )

            if slots:
                return json.dumps({
                    "success": True,
                    "data": [
                        {
                            "id": slot.id,
                            "doctor_id": slot.doctor_id,
                            "doctor_name": slot.doctor.doctor_name if slot.doctor else None,
                            "specialization": slot.doctor.specialization if slot.doctor else None,
                            "start_time": slot.start_time.isoformat(),
                            "end_time": slot.end_time.isoformat(),
                            "status": slot.status
                        }
                        for slot in slots
                    ]
                })
            else:
                return json.dumps({"success": False, "message": "No available slots found"})

        elif function_name == "bookAnAppointment":
            appointment_date = datetime.fromisoformat(function_args["appointment_date"])
            appointment, error = crud.book_appointment(
                db,
                function_args["patient_id"],
                function_args["slot_id"],
                appointment_date
            )

            if error:
                return json.dumps({"success": False, "message": error})

            return json.dumps({
                "success": True,
                "data": {
                    "id": appointment.id,
                    "appointment_number": appointment.appointment_number,
                    "appointment_date": appointment.appointment_date.isoformat(),
                    "slot_id": appointment.slot_id,
                    "patient_id": appointment.patient_id
                }
            })

        elif function_name == "cancelAppointment":
            success, error = crud.cancel_appointment(db, function_args["appointment_id"])

            if error:
                return json.dumps({"success": False, "message": error})

            return json.dumps({"success": True, "message": "Appointment cancelled successfully"})

        else:
            return json.dumps({"success": False, "message": f"Unknown function: {function_name}"})

    except Exception as e:
        return json.dumps({"success": False, "message": f"Error: {str(e)}"})


async def process_transcript_with_ai(transcript: str, session_id: str, db: Session, websocket: WebSocket,
                                     voice_handler: VoiceHandler):
    """Process transcript with AI and handle function calls"""
    try:
        await websocket.send_json({
            "type": "status",
            "message": "Processing..."
        })

        # Process with AI
        result = process_chat_message(transcript, session_id)

        # Handle function calls in a loop
        while result["type"] == "function_call":
            function_name = result["function_name"]
            function_args = result["function_args"]

            print(f"Calling function: {function_name} with args: {function_args}")

            # Execute the function
            function_result = execute_function(function_name, function_args, db)

            # Send result back to AI and get next response
            result = add_function_result(session_id, function_name, function_result)

        # Get final text response
        ai_response = result["content"]

        await websocket.send_json({
            "type": "response",
            "text": ai_response
        })

        # Generate speech
        await websocket.send_json({
            "type": "status",
            "message": "Speaking..."
        })

        audio_bytes = await voice_handler.speak_with_elevenlabs(ai_response)

        if audio_bytes:
            await websocket.send_bytes(audio_bytes)
            await websocket.send_json({
                "type": "audio_complete",
                "message": "Audio sent"
            })

        await websocket.send_json({
            "type": "status",
            "message": "Listening..."
        })

    except Exception as e:
        print(f"Error processing transcript: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     session_id = f"voice_session_{id(websocket)}"
#
#     db = next(get_db())
#     voice_handler = VoiceHandler()
#     deepgram_ws = None
#
#     try:
#         # Welcome
#         await websocket.send_json({"type": "status", "message": "Connected"})
#         await websocket.send_json({"type": "response", "text": WELCOME_MESSAGE})
#
#         audio = await voice_handler.text_to_speech(WELCOME_MESSAGE)
#         if audio:
#             await websocket.send_bytes(audio)
#             await websocket.send_json({"type": "audio_complete"})
#
#         await websocket.send_json({"type": "status", "message": "Listening..."})
#
#         # Deepgram connection
#         deepgram_url = (
#             "wss://api.deepgram.com/v1/listen?"
#             "model=nova-2"
#             "&encoding=linear16"
#             "&sample_rate=16000"
#             "&channels=1"
#             "&interim_results=true"
#             "&vad_events=true"
#         )
#
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"}
#         )
#
#         async def receive_from_client():
#             while True:
#                 try:
#                     message = await websocket.receive()
#                     if "bytes" in message and message["bytes"]:
#                         await deepgram_ws.send(message["bytes"])
#                 except WebSocketDisconnect:
#                     break
#
#         async def receive_from_deepgram():
#             while True:
#                 try:
#                     data = json.loads(await deepgram_ws.recv())
#                     msg_type = data.get("type")
#
#                     if msg_type == "Results":
#                         alt = data["channel"]["alternatives"][0]
#                         transcript = alt.get("transcript", "").strip()
#                         is_final = data.get("is_final", False)
#                         speech_final = data.get("speech_final", False)
#
#                         if transcript and is_final:
#                             voice_handler.current_transcript += " " + transcript
#                             voice_handler.current_transcript = voice_handler.current_transcript.strip()
#
#                             await websocket.send_json({
#                                 "type": "interim_transcript",
#                                 "text": voice_handler.current_transcript
#                             })
#
#                         if speech_final and voice_handler.current_transcript and not voice_handler.is_processing:
#                             await process_voice_input(
#                                 websocket,
#                                 voice_handler,
#                                 session_id,
#                                 db
#                             )
#
#                     elif msg_type == "UtteranceEnd":
#                         if voice_handler.current_transcript and not voice_handler.is_processing:
#                             await process_voice_input(
#                                 websocket,
#                                 voice_handler,
#                                 session_id,
#                                 db
#                             )
#
#                 except Exception:
#                     break
#
#         await asyncio.gather(
#             receive_from_client(),
#             receive_from_deepgram()
#         )
#
#     finally:
#         if deepgram_ws:
#             await deepgram_ws.close()
#         db.close()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"voice_session_{id(websocket)}"

    db = next(get_db())
    voice_handler = VoiceHandler()
    deepgram_ws = None
    stop_event = asyncio.Event()

    try:
        # ---- Welcome ----
        await websocket.send_json({"type": "status", "message": "Connected"})
        await websocket.send_json({"type": "response", "text": WELCOME_MESSAGE})

        audio = await voice_handler.text_to_speech(WELCOME_MESSAGE)
        if audio:
            print("✅ Sending audio bytes:", len(audio))
            await websocket.send_bytes(audio)
            await websocket.send_json({"type": "audio_complete"})

        await websocket.send_json({"type": "status", "message": "Listening..."})

        # ---- Deepgram ----
        deepgram_url = (
            "wss://api.deepgram.com/v1/listen?"
            "model=nova-2&encoding=linear16&sample_rate=16000"
            "&channels=1&interim_results=true&vad_events=true"
        )

        deepgram_ws = await websockets.connect(
            deepgram_url,
            additional_headers={"Authorization": f"Token {DEEPGRAM_API_KEY}"},
            ping_interval=5,
            ping_timeout=10
        )

        async def receive_from_client():
            try:
                while not stop_event.is_set():
                    message = await websocket.receive()
                    if message.get("type") == "websocket.disconnect":
                        stop_event.set()
                        break

                    if message.get("bytes"):
                        await deepgram_ws.send(message["bytes"])
            except WebSocketDisconnect:
                stop_event.set()
            except Exception:
                stop_event.set()

        async def receive_from_deepgram():
            try:
                while not stop_event.is_set():
                    data = json.loads(await deepgram_ws.recv())
                    msg_type = data.get("type")

                    if msg_type == "Results":
                        alt = data["channel"]["alternatives"][0]
                        transcript = alt.get("transcript", "").strip()
                        is_final = data.get("is_final", False)
                        speech_final = data.get("speech_final", False)

                        if transcript and is_final:
                            voice_handler.current_transcript += " " + transcript
                            voice_handler.current_transcript = voice_handler.current_transcript.strip()

                            await websocket.send_json({
                                "type": "interim_transcript",
                                "text": voice_handler.current_transcript
                            })

                        if speech_final and voice_handler.current_transcript and not voice_handler.is_processing:
                            await process_voice_input(
                                websocket,
                                voice_handler,
                                session_id,
                                db
                            )

                    elif msg_type == "UtteranceEnd":
                        if voice_handler.current_transcript and not voice_handler.is_processing:
                            await process_voice_input(
                                websocket,
                                voice_handler,
                                session_id,
                                db
                            )
            except Exception:
                stop_event.set()

        await asyncio.gather(
            receive_from_client(),
            receive_from_deepgram()
        )

    finally:
        stop_event.set()
        if deepgram_ws:
            await deepgram_ws.close()
        db.close()


# async def process_voice_input(websocket, voice_handler, session_id, db):
#     voice_handler.is_processing = True
#     transcript = voice_handler.current_transcript
#     voice_handler.current_transcript = ""
#
#     await websocket.send_json({"type": "transcript", "text": transcript})
#     await websocket.send_json({"type": "status", "message": "Thinking..."})
#
#     # 🔒 EXISTING appointment AI logic — untouched
#     result = process_chat_message(transcript, session_id)
#     while result["type"] == "function_call":
#         function_result = execute_function(
#             result["function_name"],
#             result["function_args"],
#             db
#         )
#         result = add_function_result(
#             session_id,
#             result["function_name"],
#             function_result
#         )
#
#     response_text = result["content"]
#
#     await websocket.send_json({"type": "response", "text": response_text})
#     await websocket.send_json({"type": "status", "message": "Speaking..."})
#
#     audio = await voice_handler.text_to_speech(response_text)
#     if audio:
#         await websocket.send_bytes(audio)
#         await websocket.send_json({"type": "audio_complete"})
#
#     await websocket.send_json({"type": "status", "message": "Listening..."})
#     voice_handler.is_processing = False

async def process_voice_input(websocket, voice_handler, session_id, db):
    # Prevent parallel processing
    if voice_handler.is_processing:
        return

    voice_handler.is_processing = True

    try:
        transcript = voice_handler.current_transcript.strip()
        voice_handler.current_transcript = ""

        if not transcript:
            return

        # Send transcript to frontend
        await websocket.send_json({
            "type": "transcript",
            "text": transcript
        })

        await websocket.send_json({
            "type": "status",
            "message": "Thinking..."
        })

        # 🔒 EXISTING appointment AI logic — untouched
        result = process_chat_message(transcript, session_id)

        while result["type"] == "function_call":
            function_result = execute_function(
                result["function_name"],
                result["function_args"],
                db
            )
            result = add_function_result(
                session_id,
                result["function_name"],
                function_result
            )

        response_text = result.get("content", "").strip()

        if not response_text:
            return

        await websocket.send_json({
            "type": "response",
            "text": response_text
        })

        await websocket.send_json({
            "type": "status",
            "message": "Speaking..."
        })

        # 🎙️ Text-to-Speech
        audio = await voice_handler.text_to_speech(response_text)

        if audio:
            await websocket.send_bytes(audio)
            await websocket.send_json({
                "type": "audio_complete"
            })

        await websocket.send_json({
            "type": "status",
            "message": "Listening..."
        })

    except Exception as e:
        # Log but do NOT crash websocket loop
        print("❌ Error in process_voice_input:", str(e))

        try:
            await websocket.send_json({
                "type": "error",
                "message": "Voice processing failed"
            })
        except:
            pass  # WebSocket already closed

    finally:
        # ✅ ALWAYS reset this
        voice_handler.is_processing = False

