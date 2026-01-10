from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Initialize main gateway app
app = FastAPI(
    title="MediLligence AI Agents Gateway",
    description="Unified gateway for all medical AI agents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from appointment_agent.app.routes import appointment, ai_chat as appt_ai_chat, voice_chat as appt_voice
from follow_up_agent.app.routes import router as followup_router
from patient_fao_agent.app.routes import education_routes, voice_routes as faq_voice
from patient_referral_agent.app.routes.referral_routes import router as referral_router
from pre_assessment_agent.app.routes import assessment_routes


app.include_router(appointment.router, prefix="/appointment", tags=["appointment"])
app.include_router(appt_ai_chat.router, prefix="/appointment", tags=["appointment-chat"])
app.include_router(appt_voice.router, prefix="/appointment", tags=["appointment-voice"])


app.include_router(followup_router, prefix="/followup", tags=["followup"])


app.include_router(education_routes.router, prefix="/faq/api/v1", tags=["faq"])
app.include_router(faq_voice.router, prefix="/faq/api/v1", tags=["faq-voice"])


app.include_router(referral_router, prefix="/referral", tags=["referral"])


app.include_router(assessment_routes.router, prefix="/assessment", tags=["assessment"])


appointment_static = os.path.join(os.path.dirname(__file__), "appointment_agent", "app", "static")
if os.path.exists(appointment_static):
    app.mount("/appointment/static", StaticFiles(directory=appointment_static), name="appointment-static")

followup_static = os.path.join(os.path.dirname(__file__), "follow_up_agent", "app", "static")
if os.path.exists(followup_static):
    app.mount("/followup/static", StaticFiles(directory=followup_static), name="followup-static")

faq_static = os.path.join(os.path.dirname(__file__), "patient_fao_agent", "app", "static")
if os.path.exists(faq_static):
    app.mount("/faq/static", StaticFiles(directory=faq_static), name="faq-static")

referral_static = os.path.join(os.path.dirname(__file__), "patient_referral_agent", "app", "static")
if os.path.exists(referral_static):
    app.mount("/referral/static", StaticFiles(directory=referral_static), name="referral-static")

assessment_static = os.path.join(os.path.dirname(__file__), "pre_assessment_agent", "app", "static")
if os.path.exists(assessment_static):
    app.mount("/assessment/static", StaticFiles(directory=assessment_static), name="assessment-static")


from fastapi.responses import FileResponse


@app.get("/appointment/")
async def appointment_chat():
    return FileResponse(os.path.join(appointment_static, "chat.html"))


@app.get("/appointment/voice")
async def appointment_voice_page():
    return FileResponse(os.path.join(appointment_static, "voice.html"))


@app.get("/followup/")
async def followup_chat():
    return FileResponse(os.path.join(followup_static, "chat.html"))


@app.get("/followup/voice")
async def followup_voice_page():
    return FileResponse(os.path.join(followup_static, "voice.html"))


@app.get("/faq/")
async def faq_chat():
    return FileResponse(os.path.join(faq_static, "chat.html"))


@app.get("/referral/")
async def referral_chat():
    return FileResponse(os.path.join(referral_static, "chat.html"))


@app.get("/assessment/")
async def assessment_root():
    return {"message": "Pre-Assessment Agent", "chat_url": "/assessment/chat"}


@app.get("/assessment/chat")
async def assessment_chat():
    return FileResponse(os.path.join(assessment_static, "chat.html"))


@app.get("/")
async def root():
    """Gateway landing page with all available agents"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MediLligence AI Agents Gateway</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 900px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 2.5em;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 40px;
                font-size: 1.1em;
            }
            .agents-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .agent-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 25px;
                color: white;
                text-decoration: none;
                transition: transform 0.3s, box-shadow 0.3s;
                display: block;
            }
            .agent-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            .agent-card h3 {
                margin-bottom: 10px;
                font-size: 1.3em;
            }
            .agent-card p {
                opacity: 0.9;
                font-size: 0.9em;
                line-height: 1.5;
            }
            .icon {
                font-size: 2em;
                margin-bottom: 10px;
            }
            .health-status {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                text-align: center;
            }
            .status-badge {
                display: inline-block;
                padding: 5px 15px;
                background: #28a745;
                color: white;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MediLligence AI Agents</h1>
            <p class="subtitle">Unified Healthcare AI Agent Platform</p>

            <div class="agents-grid">
                <a href="/appointment/" class="agent-card">
                    <div class="icon">📅</div>
                    <h3>Appointment Agent</h3>
                    <p>AI-powered appointment booking system with voice capabilities</p>
                </a>

                <a href="/followup/" class="agent-card">
                    <div class="icon">📋</div>
                    <h3>Follow-up Agent</h3>
                    <p>Patient follow-up and adherence monitoring system</p>
                </a>

                <a href="/faq/" class="agent-card">
                    <div class="icon">❓</div>
                    <h3>FAQ Agent</h3>
                    <p>Patient education and medical query assistance</p>
                </a>

                <a href="/referral/" class="agent-card">
                    <div class="icon">🔄</div>
                    <h3>Referral Agent</h3>
                    <p>AI referral and care coordination system</p>
                </a>

                <a href="/assessment/chat" class="agent-card">
                    <div class="icon">📝</div>
                    <h3>Pre-assessment Agent</h3>
                    <p>Collect patient medical information before appointments</p>
                </a>
            </div>

            <div class="health-status">
                <span class="status-badge">● All Systems Operational</span>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """Health check for all agents"""
    return {
        "status": "healthy",
        "gateway": "operational",
        "agents": {
            "appointment": "mounted at /appointment",
            "followup": "mounted at /followup",
            "faq": "mounted at /faq",
            "referral": "mounted at /referral",
            "assessment": "mounted at /assessment"
        }
    }


@app.get("/agents")
async def list_agents():
    """List all available agents and their endpoints"""
    return {
        "agents": [
            {
                "name": "Appointment Agent",
                "path": "/appointment",
                "description": "AI-powered appointment booking system",
                "endpoints": ["/appointment/", "/appointment/voice", "/appointment/health"]
            },
            {
                "name": "Follow-up Agent",
                "path": "/followup",
                "description": "Patient follow-up and adherence monitoring",
                "endpoints": ["/followup/", "/followup/voice"]
            },
            {
                "name": "FAQ Agent",
                "path": "/faq",
                "description": "Patient education and medical queries",
                "endpoints": ["/faq/", "/faq/health"]
            },
            {
                "name": "Referral Agent",
                "path": "/referral",
                "description": "AI referral and coordination",
                "endpoints": ["/referral/", "/referral/health"]
            },
            {
                "name": "Pre-assessment Agent",
                "path": "/assessment",
                "description": "Pre-appointment patient information collection",
                "endpoints": ["/assessment/", "/assessment/health"]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("Starting MediLligence AI Agents Gateway")
    print("=" * 70)
    print("\nGateway URL: http://localhost:8000")
    print("\nAgent Routes:")
    print("  • Appointment Agent: http://localhost:8000/appointment")
    print("  • Follow-up Agent:   http://localhost:8000/followup")
    print("  • FAQ Agent:         http://localhost:8000/faq")
    print("  • Referral Agent:    http://localhost:8000/referral")
    print("  • Assessment Agent:  http://localhost:8000/assessment")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")