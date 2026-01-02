# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models.schema_models import ChatRequest, ChatResponse
# from ..services import AIService, PatientService, AdherenceService
# from typing import Dict
# import uuid
#
# router = APIRouter(prefix="/api/followup", tags=["followup"])
#
# # In-memory session storage (use Redis in production)
# conversation_sessions: Dict[str, dict] = {}
#
#
# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest, db: Session = Depends(get_db)):
#     session_id = request.session_id or str(uuid.uuid4())
#
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = {
#             "messages": [],
#             "patient_verified": False,
#             "patient_id": None,
#             "consultation_id": None,
#             "stage": "ask_mobile"
#         }
#
#     session = conversation_sessions[session_id]
#     ai_service = AIService()
#
#     # Add user message
#     session["messages"].append({"role": "user", "content": request.message})
#
#     # Handle mobile number verification
#     if session["stage"] == "ask_mobile" and not session["patient_verified"]:
#         mobile_number = request.message.strip().replace("-", "").replace(" ", "")
#         patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#         if patient:
#             consultation = PatientService.get_latest_consultation(db, patient.id)
#             if consultation:
#                 session["patient_verified"] = True
#                 session["patient_id"] = patient.id
#                 session["consultation_id"] = consultation["id"]
#                 session["patient_name"] = patient.patient_name
#                 session["medication_prescribed"] = consultation["medication_id"] is not None
#                 session["stage"] = "followup_questions"
#
#                 response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "
#                 if session["medication_prescribed"]:
#                     response += "Did you receive the prescribed medication?"
#                 else:
#                     response += "How are you feeling since your visit?"
#             else:
#                 response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
#         else:
#             response = "I couldn't find a patient with that mobile number. Please verify and try again."
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Handle follow-up conversation
#     if session["stage"] == "followup_questions":
#         ai_response = ai_service.get_response(session["messages"])
#         session["messages"].append({"role": "assistant", "content": ai_response})
#
#         # Check if conversation should end
#         if any(keyword in request.message.lower() for keyword in ["thank you", "goodbye", "done", "that's all"]):
#             adherence_data = ai_service.extract_adherence_data(session["messages"])
#             AdherenceService.save_adherence_data(
#                 db,
#                 session["consultation_id"],
#                 adherence_data
#             )
#             session["stage"] = "completed"
#
#             final_response = ai_response + "\n\nYour responses have been recorded. Take care!"
#             return ChatResponse(response=final_response, session_id=session_id)
#
#         return ChatResponse(response=ai_response, session_id=session_id)
#
#     # Default response
#     response = ai_service.get_response(session["messages"])
#     session["messages"].append({"role": "assistant", "content": response})
#
#     return ChatResponse(response=response, session_id=session_id)

# #seond version
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models.schema_models import ChatRequest, ChatResponse
# from ..services import AIService, PatientService, AdherenceService, AppointmentService
# from typing import Dict
# import uuid
#
# router = APIRouter(prefix="/api/followup", tags=["followup"])
#
# # In-memory session storage (use Redis in production)
# conversation_sessions: Dict[str, dict] = {}
#
#
# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest, db: Session = Depends(get_db)):
#     session_id = request.session_id or str(uuid.uuid4())
#
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = {
#             "messages": [],
#             "patient_verified": False,
#             "patient_id": None,
#             "consultation_id": None,
#             "appointment_id": None,
#             "doctor_id": None,
#             "stage": "ask_mobile"
#         }
#
#     session = conversation_sessions[session_id]
#     ai_service = AIService()
#
#     # Add user message
#     session["messages"].append({"role": "user", "content": request.message})
#
#     # Handle mobile number verification
#     if session["stage"] == "ask_mobile" and not session["patient_verified"]:
#         mobile_number = request.message.strip().replace("-", "").replace(" ", "")
#         patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#         if patient:
#             consultation = PatientService.get_latest_consultation(db, patient.id)
#             if consultation:
#                 session["patient_verified"] = True
#                 session["patient_id"] = patient.id
#                 session["consultation_id"] = consultation["id"]
#                 session["appointment_id"] = consultation["appointment_id"]
#                 session["patient_name"] = patient.patient_name
#                 session["medication_prescribed"] = consultation["medication_id"] is not None
#                 session["medication_document"] = consultation["medication_document"]
#                 session["stage"] = "followup_questions"
#
#                 response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "
#
#                 if session["medication_prescribed"] and session["medication_document"]:
#                     # Format and display medications
#                     medication_list = PatientService.format_medication_list(session["medication_document"])
#                     response += f"\n\nYou were prescribed the following medications:\n{medication_list}\n\nDid you receive all of these medications from the pharmacy?"
#                 else:
#                     response += "How are you feeling since your visit?"
#             else:
#                 response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
#         else:
#             response = "I couldn't find a patient with that mobile number. Please verify and try again."
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Handle follow-up conversation
#     if session["stage"] == "followup_questions":
#         # Prepare context for AI
#         context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
#         if session.get("medication_document"):
#             med_list = PatientService.format_medication_list(session["medication_document"])
#             context += f"Prescribed Medications:\n{med_list}"
#
#         ai_response = ai_service.get_response(session["messages"], context)
#         session["messages"].append({"role": "assistant", "content": ai_response})
#
#         # Check if conversation should end
#         if any(keyword in request.message.lower() for keyword in
#                ["thank you", "goodbye", "done", "that's all", "no more questions"]):
#             # Extract adherence data in medical language
#             adherence_data = ai_service.extract_adherence_data(session["messages"])
#
#             # Check if early follow-up is needed
#             early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])
#
#             # If early follow-up needed, suggest appointment
#             if early_followup_analysis.get("needs_early_followup"):
#                 # Get doctor_id from appointment
#                 doctor_id = AppointmentService.get_doctor_from_appointment(
#                     db,
#                     session["appointment_id"]
#                 )
#
#                 if doctor_id:
#                     suggested_date = AppointmentService.suggest_early_appointment_date()
#
#                     followup_message = (
#                         f"\n\n⚠️ IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
#                         f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
#                         f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
#                         f"\n\nWould you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
#                     )
#
#                     ai_response += followup_message
#                     session["early_followup_offered"] = True
#                     session["suggested_appointment_date"] = suggested_date.isoformat()
#                     session["doctor_id"] = doctor_id
#
#             # Save adherence data
#             AdherenceService.save_adherence_data(
#                 db,
#                 session["consultation_id"],
#                 adherence_data,
#                 early_followup_analysis
#             )
#
#             session["stage"] = "completed"
#
#             if not early_followup_analysis.get("needs_early_followup"):
#                 final_response = ai_response + "\n\nYour responses have been recorded. Take care and feel better soon!"
#                 return ChatResponse(response=final_response, session_id=session_id)
#
#         return ChatResponse(response=ai_response, session_id=session_id)
#
#     # Handle appointment booking confirmation
#     if session["stage"] == "completed" and session.get("early_followup_offered"):
#         if any(keyword in request.message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
#             # Create early follow-up appointment
#             appointment_response = AppointmentService.create_early_followup_appointment(
#                 db,
#                 patient_id=session["patient_id"],
#                 doctor_id=session["doctor_id"],
#                 appointment_date=session["suggested_appointment_date"]
#             )
#
#             if appointment_response:
#                 response = (
#                     f"✅ Your early follow-up appointment has been scheduled for "
#                     f"{appointment_response['appointment_date']}. "
#                     f"Appointment number: {appointment_response['appointment_number']}. "
#                     f"\n\nPlease arrive 15 minutes early. Take care!"
#                 )
#             else:
#                 response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
#         else:
#             response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Default response
#     response = ai_service.get_response(session["messages"])
#     session["messages"].append({"role": "assistant", "content": response})
#
#     return ChatResponse(response=response, session_id=session_id)

# #third version
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models.schema_models import ChatRequest, ChatResponse
# from ..services import AIService, PatientService, AdherenceService, AppointmentService
# from typing import Dict
# import uuid
#
# router = APIRouter(prefix="/api/followup", tags=["followup"])
#
# # In-memory session storage (use Redis in production)
# conversation_sessions: Dict[str, dict] = {}
#
#
# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest, db: Session = Depends(get_db)):
#     session_id = request.session_id or str(uuid.uuid4())
#
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = {
#             "messages": [],
#             "patient_verified": False,
#             "patient_id": None,
#             "consultation_id": None,
#             "appointment_id": None,
#             "doctor_id": None,
#             "stage": "ask_mobile"
#         }
#
#     session = conversation_sessions[session_id]
#     ai_service = AIService()
#
#     # Add user message
#     session["messages"].append({"role": "user", "content": request.message})
#
#     # Handle mobile number verification
#     if session["stage"] == "ask_mobile" and not session["patient_verified"]:
#         mobile_number = request.message.strip().replace("-", "").replace(" ", "")
#         patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#         if patient:
#             consultation = PatientService.get_latest_consultation(db, patient.id)
#             if consultation:
#                 session["patient_verified"] = True
#                 session["patient_id"] = patient.id
#                 session["consultation_id"] = consultation["id"]
#                 session["appointment_id"] = consultation["appointment_id"]
#                 session["patient_name"] = patient.patient_name
#                 session["medication_prescribed"] = consultation["medication_id"] is not None
#                 session["medication_document"] = consultation["medication_document"]
#                 session["stage"] = "followup_questions"
#
#                 response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "
#
#                 if session["medication_prescribed"] and session["medication_document"]:
#                     # Format and display medications
#                     medication_list = PatientService.format_medication_list(session["medication_document"])
#
#                     if medication_list:
#                         response += f"\n\nYou were prescribed the following medications:\n{medication_list}\n\nDid you receive all of these medications from the pharmacy?"
#                     else:
#                         # Medication exists but couldn't parse, ask generically
#                         response += "I see you were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
#                         session["medication_parse_failed"] = True
#                 else:
#                     response += "How are you feeling since your visit?"
#             else:
#                 response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
#         else:
#             response = "I couldn't find a patient with that mobile number. Please verify and try again."
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Handle follow-up conversation
#     if session["stage"] == "followup_questions":
#         # Prepare context for AI
#         context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
#         if session.get("medication_document") and not session.get("medication_parse_failed"):
#             med_list = PatientService.format_medication_list(session["medication_document"])
#             if med_list:
#                 context += f"Prescribed Medications:\n{med_list}"
#
#         ai_response = ai_service.get_response(session["messages"], context)
#         session["messages"].append({"role": "assistant", "content": ai_response})
#
#         # Check if conversation should end
#         if any(keyword in request.message.lower() for keyword in
#                ["thank you", "goodbye", "done", "that's all", "no more questions"]):
#             # Extract adherence data in medical language
#             adherence_data = ai_service.extract_adherence_data(session["messages"])
#
#             # Check if early follow-up is needed
#             early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])
#
#             # If early follow-up needed, suggest appointment
#             if early_followup_analysis.get("needs_early_followup"):
#                 # Get doctor_id from appointment
#                 doctor_id = AppointmentService.get_doctor_from_appointment(
#                     db,
#                     session["appointment_id"]
#                 )
#
#                 if doctor_id:
#                     suggested_date = AppointmentService.suggest_early_appointment_date()
#
#                     followup_message = (
#                         f"\n\n⚠️ IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
#                         f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
#                         f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
#                         f"\n\nWould you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
#                     )
#
#                     ai_response += followup_message
#                     session["early_followup_offered"] = True
#                     session["suggested_appointment_date"] = suggested_date.isoformat()
#                     session["doctor_id"] = doctor_id
#
#             # Save adherence data
#             AdherenceService.save_adherence_data(
#                 db,
#                 session["consultation_id"],
#                 adherence_data,
#                 early_followup_analysis
#             )
#
#             session["stage"] = "completed"
#
#             if not early_followup_analysis.get("needs_early_followup"):
#                 final_response = ai_response + "\n\nYour responses have been recorded. Take care and feel better soon!"
#                 return ChatResponse(response=final_response, session_id=session_id)
#
#         return ChatResponse(response=ai_response, session_id=session_id)
#
#     # Handle appointment booking confirmation
#     if session["stage"] == "completed" and session.get("early_followup_offered"):
#         if any(keyword in request.message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
#             # Create early follow-up appointment
#             appointment_response = AppointmentService.create_early_followup_appointment(
#                 db,
#                 patient_id=session["patient_id"],
#                 doctor_id=session["doctor_id"],
#                 appointment_date=session["suggested_appointment_date"]
#             )
#
#             if appointment_response:
#                 response = (
#                     f"✅ Your early follow-up appointment has been scheduled for "
#                     f"{appointment_response['appointment_date']}. "
#                     f"Appointment number: {appointment_response['appointment_number']}. "
#                     f"\n\nPlease arrive 15 minutes early. Take care!"
#                 )
#             else:
#                 response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
#         else:
#             response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Default response
#     response = ai_service.get_response(session["messages"])
#     session["messages"].append({"role": "assistant", "content": response})
#
#     return ChatResponse(response=response, session_id=session_id)
#
#
# @router.get("/debug/patient/{mobile_number}")
# async def debug_patient_data(mobile_number: str, db: Session = Depends(get_db)):
#     """Debug endpoint to check patient data structure"""
#     patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")
#
#     consultation = PatientService.get_latest_consultation(db, patient.id)
#
#     return {
#         "patient": {
#             "id": patient.id,
#             "name": patient.patient_name,
#             "mobile": patient.mobile_number
#         },
#         "consultation": consultation,
#         "medication_document_structure": consultation["medication_document"] if consultation else None
#     }


# # ##working fourth version
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models.schema_models import ChatRequest, ChatResponse
# from ..services import AIService, PatientService, AdherenceService, AppointmentService
# from typing import Dict
# import uuid
#
# router = APIRouter(prefix="/api/followup", tags=["followup"])
#
# # In-memory session storage (use Redis in production)
# conversation_sessions: Dict[str, dict] = {}
#
#
# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest, db: Session = Depends(get_db)):
#     session_id = request.session_id or str(uuid.uuid4())
#
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = {
#             "messages": [],
#             "patient_verified": False,
#             "patient_id": None,
#             "consultation_id": None,
#             "appointment_id": None,
#             "doctor_id": None,
#             "stage": "ask_mobile"
#         }
#
#     session = conversation_sessions[session_id]
#     ai_service = AIService()
#
#     # Add user message
#     session["messages"].append({"role": "user", "content": request.message})
#
#     # Handle mobile number verification
#     if session["stage"] == "ask_mobile" and not session["patient_verified"]:
#         mobile_number = request.message.strip().replace("-", "").replace(" ", "")
#         patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#         if patient:
#             consultation = PatientService.get_latest_consultation(db, patient.id)
#             if consultation:
#                 session["patient_verified"] = True
#                 session["patient_id"] = patient.id
#                 session["consultation_id"] = consultation["id"]
#                 session["appointment_id"] = consultation["appointment_id"]
#                 session["patient_name"] = patient.patient_name
#                 session["medication_prescribed"] = consultation["medication_id"] is not None
#                 session["medication_document"] = consultation["medication_document"]
#                 session["stage"] = "followup_questions"
#
#                 response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "
#
#                 if session["medication_prescribed"]:
#                     if session["medication_document"]:
#                         # Format and display medications
#                         medication_list = PatientService.format_medication_list(session["medication_document"])
#
#                         if medication_list:
#                             response += f"\n\nYou were prescribed the following medications:\n{medication_list}\n\nDid you receive all of these medications from the pharmacy?"
#                         else:
#                             # Medication exists but couldn't parse - show raw structure and ask
#                             response += f"You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
#                     else:
#                         response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
#                 else:
#                     response += "How are you feeling since your visit?"
#             else:
#                 response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
#         else:
#             response = "I couldn't find a patient with that mobile number. Please verify and try again."
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Handle follow-up conversation
#     if session["stage"] == "followup_questions":
#         # Prepare context for AI
#         context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
#         if session.get("medication_document") and not session.get("medication_parse_failed"):
#             med_list = PatientService.format_medication_list(session["medication_document"])
#             if med_list:
#                 context += f"Prescribed Medications:\n{med_list}"
#
#         ai_response = ai_service.get_response(session["messages"], context)
#         session["messages"].append({"role": "assistant", "content": ai_response})
#
#         # Check if conversation should end
#         if any(keyword in request.message.lower() for keyword in
#                ["thank you", "goodbye", "done", "that's all", "no more questions"]):
#             # Extract adherence data in medical language
#             adherence_data = ai_service.extract_adherence_data(session["messages"])
#
#             # Check if early follow-up is needed
#             early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])
#
#             # If early follow-up needed, suggest appointment
#             if early_followup_analysis.get("needs_early_followup"):
#                 # Get doctor_id from appointment
#                 doctor_id = AppointmentService.get_doctor_from_appointment(
#                     db,
#                     session["appointment_id"]
#                 )
#
#                 if doctor_id:
#                     suggested_date = AppointmentService.suggest_early_appointment_date()
#
#                     followup_message = (
#                         f"\n\n⚠️ IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
#                         f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
#                         f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
#                         f"\n\nWould you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
#                     )
#
#                     ai_response += followup_message
#                     session["early_followup_offered"] = True
#                     session["suggested_appointment_date"] = suggested_date.isoformat()
#                     session["doctor_id"] = doctor_id
#
#             # Save adherence data
#             AdherenceService.save_adherence_data(
#                 db,
#                 session["consultation_id"],
#                 adherence_data,
#                 early_followup_analysis
#             )
#
#             session["stage"] = "completed"
#
#             if not early_followup_analysis.get("needs_early_followup"):
#                 final_response = ai_response + "\n\nYour responses have been recorded. Take care and feel better soon!"
#                 return ChatResponse(response=final_response, session_id=session_id)
#
#         return ChatResponse(response=ai_response, session_id=session_id)
#
#     # Handle appointment booking confirmation
#     if session["stage"] == "completed" and session.get("early_followup_offered"):
#         if any(keyword in request.message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
#             # Create early follow-up appointment
#             appointment_response = AppointmentService.create_early_followup_appointment(
#                 db,
#                 patient_id=session["patient_id"],
#                 doctor_id=session["doctor_id"],
#                 appointment_date=session["suggested_appointment_date"]
#             )
#
#             if appointment_response:
#                 response = (
#                     f"✅ Your early follow-up appointment has been scheduled for "
#                     f"{appointment_response['appointment_date']}. "
#                     f"Appointment number: {appointment_response['appointment_number']}. "
#                     f"\n\nPlease arrive 15 minutes early. Take care!"
#                 )
#             else:
#                 response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
#         else:
#             response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Default response
#     response = ai_service.get_response(session["messages"])
#     session["messages"].append({"role": "assistant", "content": response})
#
#     return ChatResponse(response=response, session_id=session_id)
#
#
# @router.get("/debug/patient/{mobile_number}")
# async def debug_patient_data(mobile_number: str, db: Session = Depends(get_db)):
#     """Debug endpoint to check patient data structure"""
#     patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")
#
#     consultation = PatientService.get_latest_consultation(db, patient.id)
#
#     return {
#         "patient": {
#             "id": patient.id,
#             "name": patient.patient_name,
#             "mobile": patient.mobile_number
#         },
#         "consultation": consultation,
#         "medication_document_structure": consultation["medication_document"] if consultation else None
#     }
#
#
# # #fifth version - printing conversion history
# #
# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from ..database import get_db
# # from ..models.schema_models import ChatRequest, ChatResponse
# # from ..services import AIService, PatientService, AdherenceService, AppointmentService
# # from typing import Dict
# # import uuid
# # import json
# #
# # router = APIRouter(prefix="/api/followup", tags=["followup"])
# #
# # # In-memory session storage (use Redis in production)
# # conversation_sessions: Dict[str, dict] = {}
# #
# #
# # @router.post("/chat", response_model=ChatResponse)
# # async def chat(request: ChatRequest, db: Session = Depends(get_db)):
# #     session_id = request.session_id or str(uuid.uuid4())
# #
# #     if session_id not in conversation_sessions:
# #         conversation_sessions[session_id] = {
# #             "messages": [],
# #             "patient_verified": False,
# #             "patient_id": None,
# #             "consultation_id": None,
# #             "appointment_id": None,
# #             "doctor_id": None,
# #             "stage": "ask_mobile"
# #         }
# #
# #     session = conversation_sessions[session_id]
# #     ai_service = AIService()
# #
# #     # Add user message
# #     session["messages"].append({"role": "user", "content": request.message})
# #
# #     # Handle mobile number verification
# #     if session["stage"] == "ask_mobile" and not session["patient_verified"]:
# #         mobile_number = request.message.strip().replace("-", "").replace(" ", "")
# #         patient = PatientService.get_patient_by_mobile(db, mobile_number)
# #
# #         if patient:
# #             consultation = PatientService.get_latest_consultation(db, patient.id)
# #             if consultation:
# #                 session["patient_verified"] = True
# #                 session["patient_id"] = patient.id
# #                 session["consultation_id"] = consultation["id"]
# #                 session["appointment_id"] = consultation["appointment_id"]
# #                 session["patient_name"] = patient.patient_name
# #                 session["medication_prescribed"] = consultation["medication_id"] is not None
# #                 session["medication_document"] = consultation["medication_document"]
# #                 session["stage"] = "followup_questions"
# #
# #                 response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "
# #
# #                 if session["medication_prescribed"]:
# #                     if session["medication_document"]:
# #                         # Format and display medications
# #                         medication_list = PatientService.format_medication_list(session["medication_document"])
# #
# #                         if medication_list:
# #                             response += f"\n\nYou were prescribed the following medications:\n{medication_list}\n\nDid you receive all of these medications from the pharmacy?"
# #                         else:
# #                             # Medication exists but couldn't parse - show raw structure and ask
# #                             response += f"You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
# #                     else:
# #                         response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
# #                 else:
# #                     response += "How are you feeling since your visit?"
# #             else:
# #                 response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
# #         else:
# #             response = "I couldn't find a patient with that mobile number. Please verify and try again."
# #
# #         session["messages"].append({"role": "assistant", "content": response})
# #         return ChatResponse(response=response, session_id=session_id)
# #
# #     # Handle follow-up conversation
# #     if session["stage"] == "followup_questions":
# #         # Prepare context for AI
# #         context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
# #         if session.get("medication_document") and not session.get("medication_parse_failed"):
# #             med_list = PatientService.format_medication_list(session["medication_document"])
# #             if med_list:
# #                 context += f"Prescribed Medications:\n{med_list}"
# #
# #         ai_response = ai_service.get_response(session["messages"], context)
# #         session["messages"].append({"role": "assistant", "content": ai_response})
# #
# #         # Check if conversation should end
# #         if any(keyword in request.message.lower() for keyword in
# #                ["thank you", "goodbye", "done", "that's all", "no more questions"]):
# #             # Print conversation history
# #             print("\n" + "=" * 80)
# #             print("CONVERSATION COMPLETED - FULL HISTORY")
# #             print("=" * 80)
# #             for idx, msg in enumerate(session["messages"], 1):
# #                 role = msg['role'].upper()
# #                 content = msg['content']
# #                 print(f"\n[{idx}] {role}:")
# #                 print(f"{content}")
# #             print("\n" + "=" * 80)
# #
# #             # Extract adherence data in medical language
# #             adherence_data = ai_service.extract_adherence_data(session["messages"])
# #
# #             print("\nEXTRACTED ADHERENCE DATA:")
# #             print(json.dumps(adherence_data, indent=2))
# #             print("=" * 80 + "\n")
# #
# #             # Check if early follow-up is needed
# #             early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])
# #
# #             # If early follow-up needed, suggest appointment
# #             if early_followup_analysis.get("needs_early_followup"):
# #                 # Get doctor_id from appointment
# #                 doctor_id = AppointmentService.get_doctor_from_appointment(
# #                     db,
# #                     session["appointment_id"]
# #                 )
# #
# #                 if doctor_id:
# #                     suggested_date = AppointmentService.suggest_early_appointment_date()
# #
# #                     followup_message = (
# #                         f"\n\n⚠️ IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
# #                         f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
# #                         f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
# #                         f"\n\nWould you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
# #                     )
# #
# #                     ai_response += followup_message
# #                     session["early_followup_offered"] = True
# #                     session["suggested_appointment_date"] = suggested_date.isoformat()
# #                     session["doctor_id"] = doctor_id
# #
# #             # Save adherence data
# #             AdherenceService.save_adherence_data(
# #                 db,
# #                 session["consultation_id"],
# #                 adherence_data,
# #                 early_followup_analysis
# #             )
# #
# #             session["stage"] = "completed"
# #
# #             if not early_followup_analysis.get("needs_early_followup"):
# #                 final_response = ai_response + "\n\nYour responses have been recorded. Take care and feel better soon!"
# #                 return ChatResponse(response=final_response, session_id=session_id)
# #
# #         return ChatResponse(response=ai_response, session_id=session_id)
# #
# #     # Handle appointment booking confirmation
# #     if session["stage"] == "completed" and session.get("early_followup_offered"):
# #         if any(keyword in request.message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
# #             # Create early follow-up appointment
# #             appointment_response = AppointmentService.create_early_followup_appointment(
# #                 db,
# #                 patient_id=session["patient_id"],
# #                 doctor_id=session["doctor_id"],
# #                 appointment_date=session["suggested_appointment_date"]
# #             )
# #
# #             if appointment_response:
# #                 response = (
# #                     f"✅ Your early follow-up appointment has been scheduled for "
# #                     f"{appointment_response['appointment_date']}. "
# #                     f"Appointment number: {appointment_response['appointment_number']}. "
# #                     f"\n\nPlease arrive 15 minutes early. Take care!"
# #                 )
# #             else:
# #                 response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
# #         else:
# #             response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"
# #
# #         session["messages"].append({"role": "assistant", "content": response})
# #         return ChatResponse(response=response, session_id=session_id)
# #
# #     # Default response
# #     response = ai_service.get_response(session["messages"])
# #     session["messages"].append({"role": "assistant", "content": response})
# #
# #     return ChatResponse(response=response, session_id=session_id)
# #
# #
# # @router.get("/debug/patient/{mobile_number}")
# # async def debug_patient_data(mobile_number: str, db: Session = Depends(get_db)):
# #     """Debug endpoint to check patient data structure"""
# #     patient = PatientService.get_patient_by_mobile(db, mobile_number)
# #
# #     if not patient:
# #         raise HTTPException(status_code=404, detail="Patient not found")
# #
# #     consultation = PatientService.get_latest_consultation(db, patient.id)
# #
# #     return {
# #         "patient": {
# #             "id": patient.id,
# #             "name": patient.patient_name,
# #             "mobile": patient.mobile_number
# #         },
# #         "consultation": consultation,
# #         "medication_document_structure": consultation["medication_document"] if consultation else None
# #     }


##voice integration changes
#
# from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models.schema_models import ChatRequest, ChatResponse
# from ..services import AIService, PatientService, AdherenceService, AppointmentService, VoiceService
# from typing import Dict
# import uuid
# import json
# import websockets
# import asyncio
# from ..config import settings
#
# router = APIRouter(prefix="/api/followup", tags=["followup"])
#
# # In-memory session storage (use Redis in production)
# conversation_sessions: Dict[str, dict] = {}
#
#
# @router.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest, db: Session = Depends(get_db)):
#     session_id = request.session_id or str(uuid.uuid4())
#
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = {
#             "messages": [],
#             "patient_verified": False,
#             "patient_id": None,
#             "consultation_id": None,
#             "appointment_id": None,
#             "doctor_id": None,
#             "stage": "ask_mobile"
#         }
#
#     session = conversation_sessions[session_id]
#     ai_service = AIService()
#
#     # Add user message
#     session["messages"].append({"role": "user", "content": request.message})
#
#     # Handle mobile number verification
#     if session["stage"] == "ask_mobile" and not session["patient_verified"]:
#         mobile_number = request.message.strip().replace("-", "").replace(" ", "")
#         patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#         if patient:
#             consultation = PatientService.get_latest_consultation(db, patient.id)
#             if consultation:
#                 session["patient_verified"] = True
#                 session["patient_id"] = patient.id
#                 session["consultation_id"] = consultation["id"]
#                 session["appointment_id"] = consultation["appointment_id"]
#                 session["patient_name"] = patient.patient_name
#                 session["medication_prescribed"] = consultation["medication_id"] is not None
#                 session["medication_document"] = consultation["medication_document"]
#                 session["stage"] = "followup_questions"
#
#                 response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "
#
#                 if session["medication_prescribed"]:
#                     if session["medication_document"]:
#                         # Format and display medications
#                         medication_list = PatientService.format_medication_list(session["medication_document"])
#
#                         if medication_list:
#                             response += f"\n\nYou were prescribed the following medications:\n{medication_list}\n\nDid you receive all of these medications from the pharmacy?"
#                         else:
#                             # Medication exists but couldn't parse - show raw structure and ask
#                             response += f"You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
#                     else:
#                         response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
#                 else:
#                     response += "How are you feeling since your visit?"
#             else:
#                 response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
#         else:
#             response = "I couldn't find a patient with that mobile number. Please verify and try again."
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Handle follow-up conversation
#     if session["stage"] == "followup_questions":
#         # Prepare context for AI
#         context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
#         if session.get("medication_document") and not session.get("medication_parse_failed"):
#             med_list = PatientService.format_medication_list(session["medication_document"])
#             if med_list:
#                 context += f"Prescribed Medications:\n{med_list}"
#
#         ai_response = ai_service.get_response(session["messages"], context)
#         session["messages"].append({"role": "assistant", "content": ai_response})
#
#         # Check if conversation should end
#         if any(keyword in request.message.lower() for keyword in
#                ["thank you", "goodbye", "done", "that's all", "no more questions"]):
#             # Print conversation history
#             print("\n" + "=" * 80)
#             print("CONVERSATION COMPLETED - FULL HISTORY")
#             print("=" * 80)
#             for idx, msg in enumerate(session["messages"], 1):
#                 role = msg['role'].upper()
#                 content = msg['content']
#                 print(f"\n[{idx}] {role}:")
#                 print(f"{content}")
#             print("\n" + "=" * 80)
#
#             # Extract adherence data in medical language
#             adherence_data = ai_service.extract_adherence_data(session["messages"])
#
#             print("\nEXTRACTED ADHERENCE DATA:")
#             print(json.dumps(adherence_data, indent=2))
#             print("=" * 80 + "\n")
#
#             # Check if early follow-up is needed
#             early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])
#
#             # If early follow-up needed, suggest appointment
#             if early_followup_analysis.get("needs_early_followup"):
#                 # Get doctor_id from appointment
#                 doctor_id = AppointmentService.get_doctor_from_appointment(
#                     db,
#                     session["appointment_id"]
#                 )
#
#                 if doctor_id:
#                     suggested_date = AppointmentService.suggest_early_appointment_date()
#
#                     followup_message = (
#                         f"\n\n⚠️ IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
#                         f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
#                         f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
#                         f"\n\nWould you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
#                     )
#
#                     ai_response += followup_message
#                     session["early_followup_offered"] = True
#                     session["suggested_appointment_date"] = suggested_date.isoformat()
#                     session["doctor_id"] = doctor_id
#
#             # Save adherence data
#             AdherenceService.save_adherence_data(
#                 db,
#                 session["consultation_id"],
#                 adherence_data,
#                 early_followup_analysis
#             )
#
#             session["stage"] = "completed"
#
#             if not early_followup_analysis.get("needs_early_followup"):
#                 final_response = ai_response + "\n\nYour responses have been recorded. Take care and feel better soon!"
#                 return ChatResponse(response=final_response, session_id=session_id)
#
#         return ChatResponse(response=ai_response, session_id=session_id)
#
#     # Handle appointment booking confirmation
#     if session["stage"] == "completed" and session.get("early_followup_offered"):
#         if any(keyword in request.message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
#             # Create early follow-up appointment
#             appointment_response = AppointmentService.create_early_followup_appointment(
#                 db,
#                 patient_id=session["patient_id"],
#                 doctor_id=session["doctor_id"],
#                 appointment_date=session["suggested_appointment_date"]
#             )
#
#             if appointment_response:
#                 response = (
#                     f"✅ Your early follow-up appointment has been scheduled for "
#                     f"{appointment_response['appointment_date']}. "
#                     f"Appointment number: {appointment_response['appointment_number']}. "
#                     f"\n\nPlease arrive 15 minutes early. Take care!"
#                 )
#             else:
#                 response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
#         else:
#             response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return ChatResponse(response=response, session_id=session_id)
#
#     # Default response
#     response = ai_service.get_response(session["messages"])
#     session["messages"].append({"role": "assistant", "content": response})
#
#     return ChatResponse(response=response, session_id=session_id)
#
#
# @router.get("/debug/patient/{mobile_number}")
# async def debug_patient_data(mobile_number: str, db: Session = Depends(get_db)):
#     """Debug endpoint to check patient data structure"""
#     patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#     if not patient:
#         raise HTTPException(status_code=404, detail="Patient not found")
#
#     consultation = PatientService.get_latest_consultation(db, patient.id)
#
#     return {
#         "patient": {
#             "id": patient.id,
#             "name": patient.patient_name,
#             "mobile": patient.mobile_number
#         },
#         "consultation": consultation,
#         "medication_document_structure": consultation["medication_document"] if consultation else None
#     }
#
#
# @router.websocket("/ws/voice")
# async def voice_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
#     """WebSocket endpoint for voice interaction"""
#     await websocket.accept()
#     session_id = f"voice_{uuid.uuid4()}"
#
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = {
#             "messages": [],
#             "patient_verified": False,
#             "patient_id": None,
#             "consultation_id": None,
#             "appointment_id": None,
#             "doctor_id": None,
#             "stage": "ask_mobile",
#             "current_transcript": "",
#             "is_processing": False
#         }
#
#     session = conversation_sessions[session_id]
#     ai_service = AIService()
#     deepgram_ws = None
#
#     try:
#         # Send initial greeting
#         initial_greeting = "Hello! I'm your follow-up care assistant. Please tell me your registered mobile number."
#         await websocket.send_json({"type": "response", "text": initial_greeting})
#
#         # Generate and send initial audio
#         audio_bytes = await VoiceService.speak_with_elevenlabs(initial_greeting)
#         if audio_bytes:
#             await websocket.send_bytes(audio_bytes)
#             await websocket.send_json({"type": "audio_complete"})
#
#         # Connect to Deepgram
#         deepgram_url = "wss://api.deepgram.com/v1/listen?model=nova-2&interim_results=true&punctuate=true&vad_events=true"
#         deepgram_ws = await websockets.connect(
#             deepgram_url,
#             additional_headers={"Authorization": f"Token {settings.DEEPGRAM_API_KEY}"}
#         )
#
#         print(f"Voice session {session_id} connected")
#         await websocket.send_json({"type": "status", "message": "Listening..."})
#
#         async def receive_from_client():
#             while True:
#                 try:
#                     message = await websocket.receive()
#
#                     if "bytes" in message:
#                         audio_size = len(message['bytes'])
#                         if audio_size > 0:
#                             await deepgram_ws.send(message["bytes"])
#                     elif "text" in message:
#                         data = json.loads(message["text"])
#                         if data.get("type") == "stop":
#                             break
#                 except WebSocketDisconnect:
#                     break
#                 except Exception as e:
#                     print(f"Error receiving from client: {e}")
#                     break
#
#         async def receive_from_deepgram():
#             while True:
#                 try:
#                     response = await deepgram_ws.recv()
#                     data = json.loads(response)
#                     msg_type = data.get("type", "")
#
#                     if msg_type == "Results":
#                         channel = data.get("channel", {})
#                         alternatives = channel.get("alternatives", [])
#
#                         if alternatives:
#                             transcript = alternatives[0].get("transcript", "").strip()
#                             is_final = data.get("is_final", False)
#                             speech_final = data.get("speech_final", False)
#
#                             if transcript and is_final:
#                                 session["current_transcript"] += " " + transcript
#                                 session["current_transcript"] = session["current_transcript"].strip()
#
#                                 await websocket.send_json({
#                                     "type": "interim_transcript",
#                                     "text": session["current_transcript"]
#                                 })
#
#                             if speech_final and session["current_transcript"] and not session["is_processing"]:
#                                 session["is_processing"] = True
#                                 user_message = session["current_transcript"]
#                                 session["current_transcript"] = ""
#
#                                 await websocket.send_json({
#                                     "type": "transcript",
#                                     "text": user_message
#                                 })
#
#                                 # Process using existing chat logic
#                                 response_text = await process_voice_message(
#                                     user_message, session, ai_service, db
#                                 )
#
#                                 await websocket.send_json({
#                                     "type": "response",
#                                     "text": response_text
#                                 })
#
#                                 # Generate audio response
#                                 audio_bytes = await VoiceService.speak_with_elevenlabs(response_text)
#                                 if audio_bytes:
#                                     await websocket.send_bytes(audio_bytes)
#                                     await websocket.send_json({"type": "audio_complete"})
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Listening..."
#                                 })
#
#                                 session["is_processing"] = False
#
#                     elif msg_type == "UtteranceEnd":
#                         if session["current_transcript"] and not session["is_processing"]:
#                             await asyncio.sleep(0.5)
#                             if session["current_transcript"] and not session["is_processing"]:
#                                 session["is_processing"] = True
#                                 user_message = session["current_transcript"]
#                                 session["current_transcript"] = ""
#
#                                 await websocket.send_json({
#                                     "type": "transcript",
#                                     "text": user_message
#                                 })
#
#                                 response_text = await process_voice_message(
#                                     user_message, session, ai_service, db
#                                 )
#
#                                 await websocket.send_json({
#                                     "type": "response",
#                                     "text": response_text
#                                 })
#
#                                 audio_bytes = await VoiceService.speak_with_elevenlabs(response_text)
#                                 if audio_bytes:
#                                     await websocket.send_bytes(audio_bytes)
#                                     await websocket.send_json({"type": "audio_complete"})
#
#                                 await websocket.send_json({
#                                     "type": "status",
#                                     "message": "Listening..."
#                                 })
#
#                                 session["is_processing"] = False
#
#                 except websockets.exceptions.ConnectionClosed:
#                     break
#                 except Exception as e:
#                     print(f"Error in Deepgram: {e}")
#                     break
#
#         await asyncio.gather(
#             receive_from_client(),
#             receive_from_deepgram()
#         )
#
#     except Exception as e:
#         print(f"Voice WebSocket error: {e}")
#         await websocket.send_json({"type": "error", "message": str(e)})
#     finally:
#         if deepgram_ws:
#             await deepgram_ws.close()
#
#
# async def process_voice_message(message: str, session: dict, ai_service: AIService, db: Session) -> str:
#     """Process voice message using same logic as chat"""
#     session["messages"].append({"role": "user", "content": message})
#
#     # Mobile verification stage
#     if session["stage"] == "ask_mobile" and not session["patient_verified"]:
#         mobile_number = message.strip().replace("-", "").replace(" ", "")
#         patient = PatientService.get_patient_by_mobile(db, mobile_number)
#
#         if patient:
#             consultation = PatientService.get_latest_consultation(db, patient.id)
#             if consultation:
#                 session["patient_verified"] = True
#                 session["patient_id"] = patient.id
#                 session["consultation_id"] = consultation["id"]
#                 session["appointment_id"] = consultation["appointment_id"]
#                 session["patient_name"] = patient.patient_name
#                 session["medication_prescribed"] = consultation["medication_id"] is not None
#                 session["medication_document"] = consultation["medication_document"]
#                 session["stage"] = "followup_questions"
#
#                 response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "
#
#                 if session["medication_prescribed"]:
#                     if session["medication_document"]:
#                         medication_list = PatientService.format_medication_list(session["medication_document"])
#                         if medication_list:
#                             response += f"You were prescribed the following medications: {medication_list}. Did you receive all of these medications from the pharmacy?"
#                         else:
#                             response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
#                     else:
#                         response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
#                 else:
#                     response += "How are you feeling since your visit?"
#             else:
#                 response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
#         else:
#             response = "I couldn't find a patient with that mobile number. Please verify and try again."
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return response
#
#     # Follow-up conversation stage
#     if session["stage"] == "followup_questions":
#         context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
#         if session.get("medication_document") and not session.get("medication_parse_failed"):
#             med_list = PatientService.format_medication_list(session["medication_document"])
#             if med_list:
#                 context += f"Prescribed Medications:\n{med_list}"
#
#         ai_response = ai_service.get_response(session["messages"], context)
#         session["messages"].append({"role": "assistant", "content": ai_response})
#
#         # Check if conversation should end
#         if any(keyword in message.lower() for keyword in
#                ["thank you", "goodbye", "done", "that's all", "no more questions"]):
#             print("\n" + "=" * 80)
#             print("CONVERSATION COMPLETED - FULL HISTORY")
#             print("=" * 80)
#             for idx, msg in enumerate(session["messages"], 1):
#                 role = msg['role'].upper()
#                 content = msg['content']
#                 print(f"\n[{idx}] {role}:")
#                 print(f"{content}")
#             print("\n" + "=" * 80)
#
#             adherence_data = ai_service.extract_adherence_data(session["messages"])
#             print("\nEXTRACTED ADHERENCE DATA:")
#             print(json.dumps(adherence_data, indent=2))
#             print("=" * 80 + "\n")
#
#             early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])
#
#             if early_followup_analysis.get("needs_early_followup"):
#                 doctor_id = AppointmentService.get_doctor_from_appointment(db, session["appointment_id"])
#
#                 if doctor_id:
#                     suggested_date = AppointmentService.suggest_early_appointment_date()
#                     followup_message = (
#                         f" IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
#                         f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
#                         f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
#                         f"Would you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
#                     )
#                     ai_response += followup_message
#                     session["early_followup_offered"] = True
#                     session["suggested_appointment_date"] = suggested_date.isoformat()
#                     session["doctor_id"] = doctor_id
#
#             AdherenceService.save_adherence_data(db, session["consultation_id"], adherence_data,
#                                                  early_followup_analysis)
#             session["stage"] = "completed"
#
#             if not early_followup_analysis.get("needs_early_followup"):
#                 return ai_response + " Your responses have been recorded. Take care and feel better soon!"
#
#         return ai_response
#
#     # Appointment booking stage
#     if session["stage"] == "completed" and session.get("early_followup_offered"):
#         if any(keyword in message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
#             appointment_response = AppointmentService.create_early_followup_appointment(
#                 db,
#                 patient_id=session["patient_id"],
#                 doctor_id=session["doctor_id"],
#                 appointment_date=session["suggested_appointment_date"]
#             )
#
#             if appointment_response:
#                 response = (
#                     f"Your early follow-up appointment has been scheduled for "
#                     f"{appointment_response['appointment_date']}. "
#                     f"Appointment number: {appointment_response['appointment_number']}. "
#                     f"Please arrive 15 minutes early. Take care!"
#                 )
#             else:
#                 response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
#         else:
#             response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"
#
#         session["messages"].append({"role": "assistant", "content": response})
#         return response
#
#     # Default
#     response = ai_service.get_response(session["messages"])
#     session["messages"].append({"role": "assistant", "content": response})
#     return response


from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.schema_models import ChatRequest, ChatResponse
from ..services import AIService, PatientService, AdherenceService, AppointmentService, VoiceService
from typing import Dict
import uuid
import json
import websockets
import asyncio
from ..config import settings

router = APIRouter(prefix="/api/followup", tags=["followup"])

# In-memory session storage (use Redis in production)
conversation_sessions: Dict[str, dict] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    session_id = request.session_id or str(uuid.uuid4())

    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "messages": [],
            "patient_verified": False,
            "patient_id": None,
            "consultation_id": None,
            "appointment_id": None,
            "doctor_id": None,
            "stage": "ask_mobile"
        }

    session = conversation_sessions[session_id]
    ai_service = AIService()

    # Add user message
    session["messages"].append({"role": "user", "content": request.message})

    # Handle mobile number verification
    if session["stage"] == "ask_mobile" and not session["patient_verified"]:
        mobile_number = request.message.strip().replace("-", "").replace(" ", "")
        patient = PatientService.get_patient_by_mobile(db, mobile_number)

        if patient:
            consultation = PatientService.get_latest_consultation(db, patient.id)
            if consultation:
                session["patient_verified"] = True
                session["patient_id"] = patient.id
                session["consultation_id"] = consultation["id"]
                session["appointment_id"] = consultation["appointment_id"]
                session["patient_name"] = patient.patient_name
                session["medication_prescribed"] = consultation["medication_id"] is not None
                session["medication_document"] = consultation["medication_document"]
                session["stage"] = "followup_questions"

                response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "

                if session["medication_prescribed"]:
                    if session["medication_document"]:
                        # Format and display medications
                        medication_list = PatientService.format_medication_list(session["medication_document"])

                        if medication_list:
                            response += f"\n\nYou were prescribed the following medications:\n{medication_list}\n\nDid you receive all of these medications from the pharmacy?"
                        else:
                            # Medication exists but couldn't parse - show raw structure and ask
                            response += f"You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
                    else:
                        response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
                else:
                    response += "How are you feeling since your visit?"
            else:
                response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
        else:
            response = "I couldn't find a patient with that mobile number. Please verify and try again."

        session["messages"].append({"role": "assistant", "content": response})
        return ChatResponse(response=response, session_id=session_id)

    # Handle follow-up conversation
    if session["stage"] == "followup_questions":
        # Prepare context for AI
        context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
        if session.get("medication_document") and not session.get("medication_parse_failed"):
            med_list = PatientService.format_medication_list(session["medication_document"])
            if med_list:
                context += f"Prescribed Medications:\n{med_list}"

        ai_response = ai_service.get_response(session["messages"], context)
        session["messages"].append({"role": "assistant", "content": ai_response})

        # Check if conversation should end
        if any(keyword in request.message.lower() for keyword in
               ["thank you", "goodbye", "done", "that's all", "no more questions"]):
            # Print conversation history
            print("\n" + "=" * 80)
            print("CONVERSATION COMPLETED - FULL HISTORY")
            print("=" * 80)
            for idx, msg in enumerate(session["messages"], 1):
                role = msg['role'].upper()
                content = msg['content']
                print(f"\n[{idx}] {role}:")
                print(f"{content}")
            print("\n" + "=" * 80)

            # Extract adherence data in medical language
            adherence_data = ai_service.extract_adherence_data(session["messages"])

            print("\nEXTRACTED ADHERENCE DATA:")
            print(json.dumps(adherence_data, indent=2))
            print("=" * 80 + "\n")

            # Check if early follow-up is needed
            early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])

            # If early follow-up needed, suggest appointment
            if early_followup_analysis.get("needs_early_followup"):
                # Get doctor_id from appointment
                doctor_id = AppointmentService.get_doctor_from_appointment(
                    db,
                    session["appointment_id"]
                )

                if doctor_id:
                    suggested_date = AppointmentService.suggest_early_appointment_date()

                    followup_message = (
                        f"\n\n⚠️ IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
                        f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
                        f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
                        f"\n\nWould you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
                    )

                    ai_response += followup_message
                    session["early_followup_offered"] = True
                    session["suggested_appointment_date"] = suggested_date.isoformat()
                    session["doctor_id"] = doctor_id

            # Save adherence data
            AdherenceService.save_adherence_data(
                db,
                session["consultation_id"],
                adherence_data,
                early_followup_analysis
            )

            session["stage"] = "completed"

            if not early_followup_analysis.get("needs_early_followup"):
                final_response = ai_response + "\n\nYour responses have been recorded. Take care and feel better soon!"
                return ChatResponse(response=final_response, session_id=session_id)

        return ChatResponse(response=ai_response, session_id=session_id)

    # Handle appointment booking confirmation
    if session["stage"] == "completed" and session.get("early_followup_offered"):
        if any(keyword in request.message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
            # Create early follow-up appointment
            appointment_response = AppointmentService.create_early_followup_appointment(
                db,
                patient_id=session["patient_id"],
                doctor_id=session["doctor_id"],
                appointment_date=session["suggested_appointment_date"]
            )

            if appointment_response:
                response = (
                    f"✅ Your early follow-up appointment has been scheduled for "
                    f"{appointment_response['appointment_date']}. "
                    f"Appointment number: {appointment_response['appointment_number']}. "
                    f"\n\nPlease arrive 15 minutes early. Take care!"
                )
            else:
                response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
        else:
            response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"

        session["messages"].append({"role": "assistant", "content": response})
        return ChatResponse(response=response, session_id=session_id)

    # Default response
    response = ai_service.get_response(session["messages"])
    session["messages"].append({"role": "assistant", "content": response})

    return ChatResponse(response=response, session_id=session_id)


@router.get("/debug/patient/{mobile_number}")
async def debug_patient_data(mobile_number: str, db: Session = Depends(get_db)):
    """Debug endpoint to check patient data structure"""
    patient = PatientService.get_patient_by_mobile(db, mobile_number)

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    consultation = PatientService.get_latest_consultation(db, patient.id)

    return {
        "patient": {
            "id": patient.id,
            "name": patient.patient_name,
            "mobile": patient.mobile_number
        },
        "consultation": consultation,
        "medication_document_structure": consultation["medication_document"] if consultation else None
    }


@router.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """WebSocket endpoint for voice interaction"""
    await websocket.accept()
    session_id = f"voice_{uuid.uuid4()}"

    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "messages": [],
            "patient_verified": False,
            "patient_id": None,
            "consultation_id": None,
            "appointment_id": None,
            "doctor_id": None,
            "stage": "ask_mobile",
            "current_transcript": "",
            "is_processing": False
        }

    session = conversation_sessions[session_id]
    ai_service = AIService()
    deepgram_ws = None

    try:
        # Send initial greeting
        initial_greeting = "Hello! I'm your follow-up care assistant. Please tell me your registered mobile number."
        await websocket.send_json({"type": "response", "text": initial_greeting})

        # Generate and send initial audio
        audio_bytes = await VoiceService.speak_with_elevenlabs(initial_greeting)
        if audio_bytes:
            await websocket.send_bytes(audio_bytes)
            await websocket.send_json({"type": "audio_complete"})

        # Connect to Deepgram
        deepgram_url = (
            "wss://api.deepgram.com/v1/listen?"
            "model=nova-2"
            "&encoding=linear16"
            "&sample_rate=16000"
            "&channels=1"
            "&interim_results=true"
            "&vad_events=true"
        )

        deepgram_ws = await websockets.connect(
            deepgram_url,
            additional_headers={"Authorization": f"Token {settings.DEEPGRAM_API_KEY}"}
        )

        print(f"Voice session {session_id} connected")
        await websocket.send_json({"type": "status", "message": "Listening..."})

        async def receive_from_client():
            while True:
                try:
                    message = await websocket.receive()

                    if "bytes" in message:
                        audio_size = len(message['bytes'])
                        if audio_size > 0:
                            await deepgram_ws.send(message["bytes"])
                    elif "text" in message:
                        data = json.loads(message["text"])
                        if data.get("type") == "stop":
                            break
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    print(f"Error receiving from client: {e}")
                    break

        async def receive_from_deepgram():
            while True:
                try:
                    response = await deepgram_ws.recv()
                    data = json.loads(response)
                    msg_type = data.get("type", "")

                    if msg_type == "Results":
                        channel = data.get("channel", {})
                        alternatives = channel.get("alternatives", [])

                        if alternatives:
                            transcript = alternatives[0].get("transcript", "").strip()
                            is_final = data.get("is_final", False)
                            speech_final = data.get("speech_final", False)

                            if transcript and is_final:
                                session["current_transcript"] += " " + transcript
                                session["current_transcript"] = session["current_transcript"].strip()

                                await websocket.send_json({
                                    "type": "interim_transcript",
                                    "text": session["current_transcript"]
                                })

                            # Only process when speech is truly final AND there's a longer pause
                            if speech_final and session["current_transcript"] and not session["is_processing"]:
                                # Wait 1.5 seconds to ensure user is done speaking
                                await asyncio.sleep(1.5)

                                # Check if more speech came in during the wait
                                if session["current_transcript"] and not session["is_processing"]:
                                    session["is_processing"] = True
                                user_message = session["current_transcript"]
                                session["current_transcript"] = ""

                                await websocket.send_json({
                                    "type": "transcript",
                                    "text": user_message
                                })

                                # Process using existing chat logic
                                response_text = await process_voice_message(
                                    user_message, session, ai_service, db
                                )

                                await websocket.send_json({
                                    "type": "response",
                                    "text": response_text
                                })

                                # Generate audio response
                                audio_bytes = await VoiceService.speak_with_elevenlabs(response_text)
                                if audio_bytes:
                                    await websocket.send_bytes(audio_bytes)
                                    await websocket.send_json({"type": "audio_complete"})

                                await websocket.send_json({
                                    "type": "status",
                                    "message": "Listening..."
                                })

                                session["is_processing"] = False

                    elif msg_type == "UtteranceEnd":
                        if session["current_transcript"] and not session["is_processing"]:
                            await asyncio.sleep(0.5)
                            if session["current_transcript"] and not session["is_processing"]:
                                session["is_processing"] = True
                                user_message = session["current_transcript"]
                                session["current_transcript"] = ""

                                await websocket.send_json({
                                    "type": "transcript",
                                    "text": user_message
                                })

                                response_text = await process_voice_message(
                                    user_message, session, ai_service, db
                                )

                                await websocket.send_json({
                                    "type": "response",
                                    "text": response_text
                                })

                                audio_bytes = await VoiceService.speak_with_elevenlabs(response_text)
                                if audio_bytes:
                                    await websocket.send_bytes(audio_bytes)
                                    await websocket.send_json({"type": "audio_complete"})

                                await websocket.send_json({
                                    "type": "status",
                                    "message": "Listening..."
                                })

                                session["is_processing"] = False

                except websockets.exceptions.ConnectionClosed:
                    break
                except Exception as e:
                    print(f"Error in Deepgram: {e}")
                    break

        await asyncio.gather(
            receive_from_client(),
            receive_from_deepgram()
        )

    except Exception as e:
        print(f"Voice WebSocket error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if deepgram_ws:
            await deepgram_ws.close()


def convert_spoken_to_digits(text: str) -> str:
    """Convert spoken numbers to digits (e.g., 'nine six two' -> '962')"""
    word_to_digit = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "o": "0", "oh": "0"
    }

    words = text.lower().split()
    result = []

    for word in words:
        # Remove punctuation
        word = word.strip(".,!?")
        if word in word_to_digit:
            result.append(word_to_digit[word])
        elif word.isdigit():
            result.append(word)

    # If we found digits, return them joined
    if result:
        return "".join(result)

    # Otherwise return original text (might be already in digit form)
    return text


async def process_voice_message(message: str, session: dict, ai_service: AIService, db: Session) -> str:
    """Process voice message using same logic as chat"""
    session["messages"].append({"role": "user", "content": message})

    # Mobile verification stage
    if session["stage"] == "ask_mobile" and not session["patient_verified"]:
        # Convert spoken numbers to digits
        mobile_number = convert_spoken_to_digits(message)
        mobile_number = mobile_number.strip().replace("-", "").replace(" ", "")

        print(f"Original message: '{message}'")
        print(f"Converted mobile: '{mobile_number}'")

        patient = PatientService.get_patient_by_mobile(db, mobile_number)

        if patient:
            consultation = PatientService.get_latest_consultation(db, patient.id)
            if consultation:
                session["patient_verified"] = True
                session["patient_id"] = patient.id
                session["consultation_id"] = consultation["id"]
                session["appointment_id"] = consultation["appointment_id"]
                session["patient_name"] = patient.patient_name
                session["medication_prescribed"] = consultation["medication_id"] is not None
                session["medication_document"] = consultation["medication_document"]
                session["stage"] = "followup_questions"

                response = f"Hello {patient.patient_name}! I'm calling to check on your progress after your recent consultation. "

                if session["medication_prescribed"]:
                    if session["medication_document"]:
                        medication_list = PatientService.format_medication_list(session["medication_document"])
                        if medication_list:
                            response += f"You were prescribed the following medications: {medication_list}. Did you receive all of these medications from the pharmacy?"
                        else:
                            response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
                    else:
                        response += "You were prescribed medication. Did you receive your prescribed medication from the pharmacy?"
                else:
                    response += "How are you feeling since your visit?"
            else:
                response = "I couldn't find any recent consultation records. Please contact your healthcare provider."
        else:
            response = "I couldn't find a patient with that mobile number. Please verify and try again."

        session["messages"].append({"role": "assistant", "content": response})
        return response

    # Follow-up conversation stage
    if session["stage"] == "followup_questions":
        context = f"Patient: {session.get('patient_name', 'Unknown')}\n"
        if session.get("medication_document") and not session.get("medication_parse_failed"):
            med_list = PatientService.format_medication_list(session["medication_document"])
            if med_list:
                context += f"Prescribed Medications:\n{med_list}"

        ai_response = ai_service.get_response(session["messages"], context)
        session["messages"].append({"role": "assistant", "content": ai_response})

        # Check if conversation should end
        if any(keyword in message.lower() for keyword in
               ["thank you", "goodbye", "done", "that's all", "no more questions"]):
            print("\n" + "=" * 80)
            print("CONVERSATION COMPLETED - FULL HISTORY")
            print("=" * 80)
            for idx, msg in enumerate(session["messages"], 1):
                role = msg['role'].upper()
                content = msg['content']
                print(f"\n[{idx}] {role}:")
                print(f"{content}")
            print("\n" + "=" * 80)

            adherence_data = ai_service.extract_adherence_data(session["messages"])
            print("\nEXTRACTED ADHERENCE DATA:")
            print(json.dumps(adherence_data, indent=2))
            print("=" * 80 + "\n")

            early_followup_analysis = ai_service.check_early_followup_needed(session["messages"])

            if early_followup_analysis.get("needs_early_followup"):
                doctor_id = AppointmentService.get_doctor_from_appointment(db, session["appointment_id"])

                if doctor_id:
                    suggested_date = AppointmentService.suggest_early_appointment_date()
                    followup_message = (
                        f" IMPORTANT: Based on your responses, I strongly recommend scheduling an early follow-up appointment. "
                        f"Reason: {early_followup_analysis.get('reason', 'Medical evaluation needed')}. "
                        f"Urgency: {early_followup_analysis.get('urgency', 'Medium').upper()}. "
                        f"Would you like me to help you book an appointment with your doctor for {suggested_date.strftime('%B %d, %Y')}?"
                    )
                    ai_response += followup_message
                    session["early_followup_offered"] = True
                    session["suggested_appointment_date"] = suggested_date.isoformat()
                    session["doctor_id"] = doctor_id

            AdherenceService.save_adherence_data(db, session["consultation_id"], adherence_data,
                                                 early_followup_analysis)
            session["stage"] = "completed"

            if not early_followup_analysis.get("needs_early_followup"):
                return ai_response + " Your responses have been recorded. Take care and feel better soon!"

        return ai_response

    # Appointment booking stage
    if session["stage"] == "completed" and session.get("early_followup_offered"):
        if any(keyword in message.lower() for keyword in ["yes", "sure", "ok", "please", "book"]):
            appointment_response = AppointmentService.create_early_followup_appointment(
                db,
                patient_id=session["patient_id"],
                doctor_id=session["doctor_id"],
                appointment_date=session["suggested_appointment_date"]
            )

            if appointment_response:
                response = (
                    f"Your early follow-up appointment has been scheduled for "
                    f"{appointment_response['appointment_date']}. "
                    f"Appointment number: {appointment_response['appointment_number']}. "
                    f"Please arrive 15 minutes early. Take care!"
                )
            else:
                response = "I apologize, but I couldn't schedule the appointment. Please contact the clinic directly."
        else:
            response = "I understand. Please contact your healthcare provider if your symptoms worsen. Take care!"

        session["messages"].append({"role": "assistant", "content": response})
        return response

    # Default
    response = ai_service.get_response(session["messages"])
    session["messages"].append({"role": "assistant", "content": response})
    return response
