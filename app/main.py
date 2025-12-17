import secrets
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import markdown
from pathlib import Path

from .database import SessionLocal, engine, Base
from .models import User
from .services import send_email

# Create database tables
Base.metadata.create_all(bind=engine)

# Move OpenAPI docs to /api-docs so we can use /docs for our documentation
app = FastAPI(title="Shardium", docs_url="/api-docs", redoc_url="/api-redoc")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Marketing landing page"""
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/app", response_class=HTMLResponse)
async def app_page(request: Request):
    """Main application - create vault"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/docs", response_class=HTMLResponse)
async def docs_index(request: Request):
    """Documentation index"""
    return await render_docs(request, "README")

@app.get("/docs/{doc_name}", response_class=HTMLResponse)
async def docs_page(request: Request, doc_name: str):
    """Documentation pages"""
    return await render_docs(request, doc_name)

async def render_docs(request: Request, doc_name: str):
    """Helper to render markdown documentation"""
    docs_path = Path("docs")
    
    # Map doc names to files
    doc_files = {
        "README": "README.md",
        "getting-started": "getting-started.md",
        "how-it-works": "how-it-works.md",
        "security": "security.md",
        "faq": "faq.md",
    }
    
    filename = doc_files.get(doc_name, f"{doc_name}.md")
    file_path = docs_path / filename
    
    if not file_path.exists():
        # Return 404 page or redirect
        return templates.TemplateResponse("docs.html", {
            "request": request,
            "content": "<h1>Page Not Found</h1><p>This documentation page doesn't exist.</p>",
            "current_doc": doc_name
        })
    
    # Read and convert markdown to HTML
    md_content = file_path.read_text(encoding="utf-8")
    html_content = markdown.markdown(
        md_content, 
        extensions=['tables', 'fenced_code', 'toc']
    )
    
    return templates.TemplateResponse("docs.html", {
        "request": request,
        "content": html_content,
        "current_doc": "index" if doc_name == "README" else doc_name
    })

@app.post("/vault/create", response_class=HTMLResponse)
async def create_vault(
    request: Request,
    email: str = Form(...),
    beneficiary_email: str = Form(...),
    shard_c: str = Form(...),
    db: Session = Depends(get_db)
):
    # Check if user exists
    user = db.query(User).filter(User.email == email).first()
    if user:
        return templates.TemplateResponse("index.html", {"request": request, "error": "User already exists with this email."})

    heartbeat_token = secrets.token_urlsafe(32)
    new_user = User(
        email=email,
        beneficiary_email=beneficiary_email,
        shard_c=shard_c,
        heartbeat_token=heartbeat_token,
        last_heartbeat=datetime.now()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send beautiful welcome email
    welcome_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0a0a0a; color: #e2e8f0; padding: 40px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #111; border-radius: 16px; padding: 40px; border: 1px solid #333; }}
            .logo {{ font-size: 28px; font-weight: bold; color: #14b8a6; margin-bottom: 20px; }}
            h1 {{ color: #fff; margin-bottom: 10px; }}
            .subtitle {{ color: #94a3b8; font-size: 16px; margin-bottom: 30px; }}
            .section {{ background: #1a1a1a; border-radius: 12px; padding: 20px; margin: 20px 0; border: 1px solid #333; }}
            .section h3 {{ color: #14b8a6; margin-top: 0; }}
            .btn {{ display: inline-block; background: linear-gradient(to right, #14b8a6, #0ea5e9); color: #000; font-weight: bold; padding: 14px 28px; border-radius: 8px; text-decoration: none; margin: 20px 0; }}
            .timeline {{ border-left: 3px solid #14b8a6; padding-left: 20px; margin: 20px 0; }}
            .timeline-item {{ margin-bottom: 15px; }}
            .timeline-day {{ color: #14b8a6; font-weight: bold; }}
            .warning {{ background: #422006; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; margin: 20px 0; }}
            .warning-title {{ color: #fbbf24; font-weight: bold; margin-bottom: 5px; }}
            .footer {{ text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #333; }}
            ul {{ color: #cbd5e1; }}
            li {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🔐 Shardium</div>
            <h1>Your Vault is Active!</h1>
            <p class="subtitle">Welcome to the trustless dead man's switch. Your crypto is now protected.</p>
            
            <div class="section">
                <h3>📋 What We've Set Up</h3>
                <ul>
                    <li><strong>Your Email:</strong> {email}</li>
                    <li><strong>Beneficiary:</strong> {beneficiary_email}</li>
                    <li><strong>Shard C:</strong> Securely stored (only released if you stop responding)</li>
                    <li><strong>Check-in Period:</strong> Every 30 days</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>🗓️ How the Dead Man's Switch Works</h3>
                <div class="timeline">
                    <div class="timeline-item">
                        <span class="timeline-day">Day 0 (Today)</span><br>
                        Vault activated. Timer starts.
                    </div>
                    <div class="timeline-item">
                        <span class="timeline-day">Day 30</span><br>
                        We'll email you: "Are you still with us?" Click to confirm.
                    </div>
                    <div class="timeline-item">
                        <span class="timeline-day">Day 60</span><br>
                        Final warning if you haven't responded.
                    </div>
                    <div class="timeline-item">
                        <span class="timeline-day">Day 90</span><br>
                        If no response, Shard C is sent to your beneficiary.
                    </div>
                </div>
            </div>
            
            <div class="warning">
                <div class="warning-title">⚠️ Important Reminders</div>
                <ul>
                    <li>Make sure your beneficiary has <strong>Shard B</strong> (the printed PDF)</li>
                    <li>Keep your <strong>Shard A</strong> in a safe place (password manager, safe, etc.)</li>
                    <li>Check your email regularly to avoid false alarms</li>
                    <li>You can reset the timer anytime by clicking the heartbeat link</li>
                </ul>
            </div>
            
            <div style="text-align: center;">
                <a href="https://shardium.maxcomperatore.com/heartbeat/{new_user.id}/{heartbeat_token}" class="btn">
                    ✅ Test Your Heartbeat Link
                </a>
                <p style="color: #64748b; font-size: 12px;">Click to verify everything is working (resets your 30-day timer)</p>
            </div>
            
            <div class="section">
                <h3>🔒 Security Reminders</h3>
                <ul>
                    <li>We <strong>never</strong> have access to your full seed phrase</li>
                    <li>We only store Shard C (useless on its own)</li>
                    <li>Your beneficiary needs Shard B + Shard C to recover</li>
                    <li>You can recover with Shard A + Shard B anytime</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>Shardium — Trustless Dead Man's Switch for Crypto</p>
                <p>Questions? Reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(email, "🔐 Welcome to Shardium - Your Vault is Active", welcome_html)
    
    return templates.TemplateResponse("success.html", {"request": request})

@app.get("/heartbeat/{user_id}/{token}", response_class=HTMLResponse)
async def heartbeat(request: Request, user_id: int, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.heartbeat_token == token).first()
    if not user:
        return HTMLResponse("Invalid link", status_code=404)
    
    user.last_heartbeat = datetime.now()
    user.is_dead = False # Resurrect if previously marked
    db.commit()
    
    return templates.TemplateResponse("check_in.html", {"request": request, "message": "Heartbeat confirmed. Timer reset for 30 days."})

@app.get("/recover", response_class=HTMLResponse)
async def recover_page(request: Request):
    return templates.TemplateResponse("recover.html", {"request": request})

# ========== CRON JOBS ==========
# Vercel Cron calls this daily at midnight

@app.get("/api/cron/check-heartbeats")
@app.post("/api/cron/check-heartbeats")
async def check_heartbeats(db: Session = Depends(get_db)):
    """
    Daily cron job that:
    1. Sends 30-day reminder emails
    2. Sends 60-day warning emails
    3. Triggers death at 90 days (sends Shard C to beneficiary)
    """
    now = datetime.now()
    results = {"reminders_30d": [], "warnings_60d": [], "deaths_90d": []}
    
    # Get all active (not dead) users
    active_users = db.query(User).filter(User.is_dead == False).all()
    
    for user in active_users:
        days_since_heartbeat = (now - user.last_heartbeat).days
        
        # 30-day reminder (between 29-31 days to catch it)
        if 29 <= days_since_heartbeat <= 31:
            send_email(
                user.email,
                "🔔 Shardium Check-In Required",
                f"""
                <h2>It's been 30 days!</h2>
                <p>Click the link below to confirm you're still with us:</p>
                <p><a href="https://shardium.maxcomperatore.com/heartbeat/{user.id}/{user.heartbeat_token}">✅ I'm Still Here</a></p>
                <p>If we don't hear from you in 60 more days, Shard C will be sent to your beneficiary.</p>
                """
            )
            results["reminders_30d"].append(user.email)
        
        # 60-day warning
        elif 59 <= days_since_heartbeat <= 61:
            send_email(
                user.email,
                "⚠️ URGENT: Shardium - 30 Days Left",
                f"""
                <h2>Final Warning!</h2>
                <p>We haven't heard from you in 60 days.</p>
                <p><strong>In 30 days, Shard C will be sent to your beneficiary.</strong></p>
                <p><a href="https://shardium.maxcomperatore.com/heartbeat/{user.id}/{user.heartbeat_token}">✅ Click Here to Confirm You're OK</a></p>
                """
            )
            results["warnings_60d"].append(user.email)
        
        # 90-day death trigger
        elif days_since_heartbeat >= 90:
            user.is_dead = True
            send_email(
                user.beneficiary_email,
                "🔐 Shardium Activation - Recovery Key Inside",
                f"""
                <h2>Important: Crypto Recovery Key</h2>
                <p>We have not heard from <strong>{user.email}</strong> for 90 days.</p>
                <p>As instructed, here is <strong>Shard C</strong>:</p>
                <div style="background:#f0f0f0; padding:15px; font-family:monospace; word-break:break-all;">
                    {user.shard_c}
                </div>
                <h3>Next Steps:</h3>
                <ol>
                    <li>Locate Shard B (the printed document you received)</li>
                    <li>Go to <a href="https://shardium.maxcomperatore.com/recover">shardium.maxcomperatore.com/recover</a></li>
                    <li>Enter both Shard B and Shard C</li>
                    <li>The original seed phrase will be recovered</li>
                </ol>
                <p>Our condolences. 💐</p>
                """
            )
            results["deaths_90d"].append(user.email)
    
    db.commit()
    return {"status": "ok", "processed": results}

# Keep old endpoint for manual testing
@app.post("/simulate/cron/check-deaths")
async def simulate_check_deaths(db: Session = Depends(get_db)):
    return await check_heartbeats(db)


