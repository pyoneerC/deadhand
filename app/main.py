import secrets
import hashlib
import re
import os
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import markdown
from pathlib import Path

from .database import SessionLocal, engine, Base
from .models import User
from .services import send_email
from .crypto import encrypt_shard, decrypt_shard

# Create database tables
Base.metadata.create_all(bind=engine)

# Move OpenAPI docs to /api-docs so we can use /docs for our documentation
app = FastAPI(title="Shardium", docs_url="/api-docs", redoc_url="/api-redoc")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Favicon route
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.png", media_type="image/png")

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

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Terms of Service"""
    return templates.TemplateResponse("terms.html", {"request": request})

# ========== BLOG ==========

def parse_blog_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown file"""
    if not content.startswith('---'):
        return {}, content
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content
    
    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"\'')
    
    return frontmatter, parts[2]

def get_all_blog_posts() -> list:
    """Get all blog posts from the blog directory"""
    blog_dir = Path("blog")
    if not blog_dir.exists():
        return []
    
    posts = []
    for file in blog_dir.glob("*.md"):
        content = file.read_text(encoding="utf-8")
        meta, _ = parse_blog_frontmatter(content)
        if meta.get('title'):
            # Parse tags
            tags = meta.get('tags', '')
            tags_list = [t.strip() for t in tags.split(',')] if tags else []
            
            # Format date
            date_str = meta.get('date', '')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_formatted = date_obj.strftime('%B %d, %Y')
            except:
                date_formatted = date_str
            
            posts.append({
                'title': meta.get('title', ''),
                'slug': meta.get('slug', file.stem),
                'description': meta.get('description', ''),
                'author': meta.get('author', 'Shardium Team'),
                'date': date_str,
                'date_formatted': date_formatted,
                'tags': tags,
                'tags_list': tags_list,
                'image': meta.get('image', '/static/favicon.png')
            })
    
    # Sort by date descending
    posts.sort(key=lambda x: x['date'], reverse=True)
    return posts

@app.get("/blog", response_class=HTMLResponse)
async def blog_index(request: Request):
    """Blog listing page"""
    posts = get_all_blog_posts()
    return templates.TemplateResponse("blog_index.html", {
        "request": request,
        "posts": posts
    })

@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str):
    """Individual blog post"""
    blog_dir = Path("blog")
    
    # Find the post file
    post_file = blog_dir / f"{slug}.md"
    if not post_file.exists():
        # Try to find by slug in frontmatter
        for file in blog_dir.glob("*.md"):
            content = file.read_text(encoding="utf-8")
            meta, _ = parse_blog_frontmatter(content)
            if meta.get('slug') == slug:
                post_file = file
                break
        else:
            raise HTTPException(status_code=404, detail="Post not found")
    
    content = post_file.read_text(encoding="utf-8")
    meta, body = parse_blog_frontmatter(content)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(body, extensions=['tables', 'fenced_code', 'toc'])
    
    # Parse tags
    tags = meta.get('tags', '')
    tags_list = [t.strip() for t in tags.split(',')] if tags else []
    
    # Format date
    date_str = meta.get('date', '')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_formatted = date_obj.strftime('%B %d, %Y')
    except:
        date_formatted = date_str
    
    # Estimate reading time (200 words per minute)
    word_count = len(body.split())
    reading_time = max(1, round(word_count / 200))
    
    # Get related posts (exclude current)
    all_posts = get_all_blog_posts()
    related_posts = [p for p in all_posts if p['slug'] != slug][:2]
    
    return templates.TemplateResponse("blog_post.html", {
        "request": request,
        "title": meta.get('title', 'Blog Post'),
        "description": meta.get('description', ''),
        "author": meta.get('author', 'Shardium Team'),
        "date": date_str,
        "date_formatted": date_formatted,
        "tags": tags,
        "tags_list": tags_list,
        "image": meta.get('image', '/static/favicon.png'),
        "slug": slug,
        "content": html_content,
        "reading_time": reading_time,
        "related_posts": related_posts
    })

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
        "icp": "icp.md",
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
    created_timestamp = datetime.now()
    
    # IMMUTABILITY PROTECTION: Create hash of critical config
    # If attacker modifies beneficiary_email or shard_c, hash won't match
    config_string = f"{beneficiary_email}|{shard_c}|{created_timestamp.isoformat()}"
    config_hash = hashlib.sha256(config_string.encode()).hexdigest()
    
    # Encrypt shard_c before storing (key derived from heartbeat_token)
    encrypted_shard = encrypt_shard(shard_c, heartbeat_token)
    
    new_user = User(
        email=email,
        beneficiary_email=beneficiary_email,
        shard_c=encrypted_shard,  # Now actually encrypted!
        config_hash=config_hash,  # Immutable commitment
        heartbeat_token=heartbeat_token,
        last_heartbeat=created_timestamp
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
            .timeline-item {{ margin-bottom: 15px; color: #cbd5e1; }}
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
    try:
        now = datetime.now()
        results = {"reminders_30d": [], "warnings_60d": [], "deaths_90d": [], "errors": []}
        
        # Get all active (not dead) users
        active_users = db.query(User).filter(User.is_dead == False).all()
        
        for user in active_users:
            try:
                # Handle timezone-aware vs naive datetime
                last_hb = user.last_heartbeat
                if last_hb is None:
                    continue
                if hasattr(last_hb, 'replace') and last_hb.tzinfo is not None:
                    last_hb = last_hb.replace(tzinfo=None)
                days_since_heartbeat = (now - last_hb).days
                
                # 30-day reminder
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
                    # INTEGRITY CHECK
                    if user.config_hash and user.created_at:
                        created_str = user.created_at.isoformat() if hasattr(user.created_at, 'isoformat') else str(user.created_at)
                        if user.created_at.tzinfo is not None:
                            created_str = user.created_at.replace(tzinfo=None).isoformat()
                        expected_config = f"{user.beneficiary_email}|{user.shard_c}|{created_str}"
                        expected_hash = hashlib.sha256(expected_config.encode()).hexdigest()
                        
                        if expected_hash != user.config_hash:
                            results["errors"].append(f"{user.email}: tampering detected")
                            continue
                    
                    user.is_dead = True
                    send_email(
                        user.beneficiary_email,
                        "🔐 Shardium Activation - Recovery Key Inside",
                        f"""
                        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0a0a0a; color: #e2e8f0; padding: 40px; border-radius: 16px;">
                            <div style="text-align: center; margin-bottom: 30px;">
                                <div style="font-size: 28px; font-weight: bold; color: #14b8a6;">🔐 Shardium</div>
                            </div>
                            
                            <h2 style="color: #fff; margin-bottom: 10px;">Important: Crypto Recovery Key</h2>
                            <p style="color: #94a3b8;">We have not heard from <strong style="color: #fff;">{user.email}</strong> for 90 days.</p>
                            <p style="color: #94a3b8;">As instructed, here is <strong style="color: #14b8a6;">Shard C</strong>:</p>
                            
                            <div style="background: #18181b; border: 2px dashed #3f3f46; padding: 20px; font-family: monospace; word-break: break-all; border-radius: 8px; color: #10b981; margin: 20px 0;">
                                {decrypt_shard(user.shard_c, user.heartbeat_token)}
                            </div>
                            
                            <div style="background: #1a1a1a; border-radius: 12px; padding: 20px; margin: 20px 0; border: 1px solid #333;">
                                <h3 style="color: #14b8a6; margin-top: 0;">📋 Recovery Steps</h3>
                                <ol style="color: #cbd5e1; padding-left: 20px;">
                                    <li style="margin-bottom: 8px;">Locate <strong>Shard B</strong> (the printed document you received)</li>
                                    <li style="margin-bottom: 8px;">Go to <a href="https://shardium.maxcomperatore.com/recover" style="color: #14b8a6;">shardium.maxcomperatore.com/recover</a></li>
                                    <li style="margin-bottom: 8px;">Enter both Shard B and Shard C</li>
                                    <li style="margin-bottom: 8px;">The original seed phrase will be recovered</li>
                                </ol>
                            </div>
                            
                            <p style="color: #64748b; text-align: center;">Our condolences. 💐</p>
                            
                            <hr style="border: none; border-top: 1px solid #333; margin: 30px 0;">
                            
                            <!-- VIRAL LOOP: Convert beneficiary to user -->
                            <div style="background: linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%); border-radius: 12px; padding: 25px; text-align: center; margin-top: 20px;">
                                <h3 style="color: #000; margin: 0 0 10px 0; font-size: 18px;">Now Protect YOUR Crypto</h3>
                                <p style="color: #000; opacity: 0.8; margin: 0 0 15px 0; font-size: 14px;">
                                    You just experienced how Shardium works. Don't let your crypto die with you.
                                </p>
                                <a href="https://shardium.maxcomperatore.com/app?ref=beneficiary&discount=50" 
                                   style="display: inline-block; background: #000; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                                    Create Your Vault — 50% Off First Year
                                </a>
                                <p style="color: #000; opacity: 0.6; margin: 10px 0 0 0; font-size: 12px;">
                                    Set up in 5 minutes. Protect your loved ones.
                                </p>
                            </div>
                            
                            <div style="text-align: center; margin-top: 30px; color: #64748b; font-size: 12px;">
                                <p>Shardium — Trustless Dead Man's Switch for Crypto</p>
                            </div>
                        </div>
                        """
                    )
                    results["deaths_90d"].append(user.email)
                    
            except Exception as e:
                results["errors"].append(f"{user.email}: {str(e)}")
                continue
        
        db.commit()
        return {"status": "ok", "processed": results}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Keep old endpoint for manual testing
@app.post("/simulate/cron/check-deaths")
async def simulate_check_deaths(db: Session = Depends(get_db)):
    return await check_heartbeats(db)
