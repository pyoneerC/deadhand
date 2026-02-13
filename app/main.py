# SPDX-License-Identifier: BUSL-1.1
# Copyright (c) 2026 pyoneerC. All rights reserved.

import secrets
import hmac
import hashlib
import re
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Depends, Form, HTTPException, Response, BackgroundTasks
import resend
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, ORJSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import markdown
from pathlib import Path
import stripe
from urllib.parse import quote_plus
import csv
import io
import random
from posthog import Posthog

from email.utils import formatdate

# Load environment variables from .env file
load_dotenv()

# Load programmatic SEO topics from CSV
PSEO_TOPICS = {}
TOPICS_FILE = Path("app/data/pseo_topics.csv")
if TOPICS_FILE.exists():
    try:
        with open(TOPICS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                PSEO_TOPICS[row['slug']] = row
    except Exception as e:
        print(f"Error loading PSEO topics: {e}")

# Load Competitor Comparison Data
COMPETITORS = {}
COMPETITORS_FILE = Path("app/data/competitors.csv")
if COMPETITORS_FILE.exists():
    try:
        with open(COMPETITORS_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                COMPETITORS[row['slug']] = row
    except Exception as e:
        print(f"Error loading competitors: {e}")

# Dynamic price caching
async def get_btc_price():
    """Static BTC price placeholder to remove external dependencies"""
    return 95000  # Conservative estimate for visual purposes


from .database import SessionLocal, engine, Base
from .models import User
from .services import send_email
from .crypto import encrypt_shard, decrypt_shard, encrypt_token, decrypt_token

# Create database tables
Base.metadata.create_all(bind=engine)

# Stripe Configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
BASE_URL = os.getenv("BASE_URL", "https://deadhandprotocol.com")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # For purchase notifications

# Stripe Price IDs - Create these in Stripe Dashboard
STRIPE_PRICES = {
    "annual": os.getenv("STRIPE_PRICE_ANNUAL"),      # $49/year subscription
    "lifetime": os.getenv("STRIPE_PRICE_LIFETIME"),  # $129 one-time
}

# PostHog Configuration
posthog = Posthog(
    project_api_key='phc_sFQxcTaCFEjtTSgt2qjDYDMFIgY6XlDYn80JxSickHQ',
    host='https://us.i.posthog.com',
    enable_exception_autocapture=True
)

# Disable OpenAPI docs and schemas for minimal footprint
app = FastAPI(
    openapi_url=None, 
    docs_url=None, 
    redoc_url=None,
    default_response_class=ORJSONResponse
)

# Performance: Enable GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Global Exception Handler for PostHog
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Capture exception in PostHog
    posthog.capture_exception(exc)
    
    # Return a generic error response
    return HTMLResponse(
        content="""
        <div style="background: #09090b; color: #fff; height: 100vh; display: flex; align-items: center; justify-content: center; font-family: sans-serif;">
            <div style="text-align: center;">
                <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">500</h1>
                <p style="color: #a1a1aa;">something went wrong on our end. we've been notified.</p>
                <a href="/" style="color: #10b981; text-decoration: none; margin-top: 1rem; display: inline-block;">go back home</a>
            </div>
        </div>
        """,
        status_code=500
    )

# Canonical Domain Redirection Middleware
@app.middleware("http")
async def enforce_canonical_domain(request: Request, call_next):
    # Get host from header
    host = request.headers.get("host", "")
    canonical_host = BASE_URL.replace("https://", "").replace("http://", "").rstrip("/")
    
    # 302 Redirect (Temporary) if host is not canonical
    # Using 302 instead of 301 to prevent browser caching localhost redirects
    is_local = any(h in host for h in ["localhost", "127.0.0.1", ":8000", ":5000"])
    
    if host and host != canonical_host and not is_local:
        target_url = str(request.url).replace(host, canonical_host)
        if BASE_URL.startswith("https://"):
            target_url = target_url.replace("http://", "https://")
        return RedirectResponse(url=target_url, status_code=301)
        
    return await call_next(request)

# Static Asset Caching Middleware
@app.middleware("http")
async def add_cache_control_header(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if (path.startswith("/static") or 
        path == "/favicon.ico" or 
        path.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".mp4", ".css", ".js", ".vtt"))):
        # Cache for 1 year (31536000 seconds)
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"

    # Security Headers (Institutional Grade)
    response.headers["X-Frame-Options"] = "DENY" 
    response.headers["X-Content-Type-Options"] = "nosniff" 
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    
    return response

# CSRF Protection Middleware
class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.method == "GET":
            # If no csrf cookie, set one
            if "csrf_token" not in request.cookies:
                token = secrets.token_urlsafe(32)
                response.set_cookie(
                    "csrf_token", 
                    token, 
                    httponly=True,  # Prevent JS access (XSS protection)
                    samesite="lax",
                    secure=True
                )
                request.state.csrf_token = token
            else:
                request.state.csrf_token = request.cookies["csrf_token"]
        return response

app.add_middleware(CSRFMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Dependency to validate CSRF
async def validate_csrf(request: Request):
    csrf_cookie = request.cookies.get("csrf_token")
    if not csrf_cookie:
        raise HTTPException(status_code=403, detail="CSRF cookie missing")
    
    # Check header (for AJAX/JSON)
    csrf_header = request.headers.get("X-CSRF-Token")
    if csrf_header and secrets.compare_digest(csrf_header, csrf_cookie):
        return
        
    # Check form (for Form POST) - This requires reading body which consumes stream
    # FastAPI dependency runs before body parsing. 
    # For Form data, we inject it into the route handler arguments instead of middleware/dep
    # because reading body here would break the route handler.
    # So for JSON endpoints we use this dependency. For Form endpoints we check manually.
    if csrf_header: 
         raise HTTPException(status_code=403, detail="CSRF token mismatch")
         
    # If no header, and not a method that requires it, pass (handled in route)
    pass


# Favicon route
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/favicon.png", media_type="image/png")

# Robots.txt
@app.get("/robots.txt", include_in_schema=False)
async def robots():
    return FileResponse("robots.txt", media_type="text/plain")

# Sitemap.xml
@app.get("/sitemap.xml", include_in_schema=False)
async def sitemap():
    from fastapi.responses import Response
    
    # Get all blog posts
    blog_dir = Path("blog")
    blog_posts = []
    if blog_dir.exists():
        for file in blog_dir.glob("*.md"):
            slug = file.stem
            blog_posts.append(f"{BASE_URL.rstrip('/')}/blog/{slug}")
    
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{BASE_URL.rstrip('/')}/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{BASE_URL.rstrip('/')}/tools/dead-switch</loc>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>{BASE_URL.rstrip('/')}/docs</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <!-- Programmatic SEO URLs -->
    {"".join([f'''
    <url>
        <loc>{BASE_URL.rstrip('/')}/p/{slug}</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>''' for slug in PSEO_TOPICS.keys()])}
    <!-- Competitor Alternatives -->
    {"".join([f'''
    <url>
        <loc>{BASE_URL.rstrip('/')}/alternatives/{slug}-alternative</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>''' for slug in COMPETITORS.keys()])}
    {"".join([f'''
    <url>
        <loc>{post}</loc>
        <changefreq>monthly</changefreq>
        <priority>0.6</priority>
    </url>''' for post in blog_posts])}
</urlset>"""
    
    return Response(content=sitemap_xml, media_type="application/xml")

# RSS Feed (Automated Distribution)
@app.get("/feed.xml", include_in_schema=False)
async def rss_feed():
    """Generate RSS 2.0 feed for blog posts and announcements"""
    
    # 1. Get Blog Posts
    blog_dir = Path("blog")
    items = []
    
    if blog_dir.exists():
        # Read posts, sort by date (filename or metadata), limit to recent 10
        # Sort by modification time, newest first
        files = sorted(list(blog_dir.glob("*.md")), key=lambda f: f.stat().st_mtime, reverse=True)
        
        for file in files[:10]:
            slug = file.stem
            url = f"{BASE_URL.rstrip('/')}/blog/{slug}"
            
            # Robust Frontmatter Parsing
            try:
                content = file.read_text(encoding="utf-8")
                md = markdown.Markdown(extensions=['meta'])
                md.convert(content)
                meta = getattr(md, 'Meta', {})
            except:
                meta = {}

            # Extract title with fallback
            title = meta.get('title', [slug.replace("-", " ").title()])[0]
            
            # Extract date with fallback to file mtime
            date_str = meta.get('date', [''])[0]
            try:
                if date_str:
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                    pub_date = formatdate(dt.timestamp())
                else:
                    pub_date = formatdate(file.stat().st_mtime)
            except:
                pub_date = formatdate(file.stat().st_mtime)
            
            # Extract description
            desc = meta.get('description', [f'Official update regarding {title}.'])[0]
            
            items.append(f"""
            <item>
                <title>{title}</title>
                <link>{url}</link>
                <guid>{url}</guid>
                <pubDate>{pub_date}</pubDate>
                <description>{desc}</description>
            </item>""")
            
    rss_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
    <title>Deadhand Protocol Updates</title>
    <link>{BASE_URL}</link>
    <description>The sovereign protocol for cryptographic inheritance and digital dead man's switches.</description>
    <language>en-us</language>
    <lastBuildDate>{formatdate(datetime.now().timestamp())}</lastBuildDate>
    <atom:link href="{BASE_URL.rstrip('/')}/feed.xml" rel="self" type="application/rss+xml" />
    {"".join(items)}
</channel>
</rss>"""

    return Response(content=rss_content, media_type="application/xml")

# PSEO Directory
@app.get("/p", response_class=HTMLResponse)
@app.get("/p/", response_class=HTMLResponse)
async def pseo_directory(request: Request, page: int = 1):
    """Paginated directory for all pSEO topics to help crawler discovery"""
    per_page = 100
    all_slugs = sorted(list(PSEO_TOPICS.keys()))
    total = len(all_slugs)
    
    start = (page - 1) * per_page
    end = start + per_page
    
    paged_slugs = all_slugs[start:end]
    topics = [(slug, PSEO_TOPICS[slug]['title']) for slug in paged_slugs]
    
    return templates.TemplateResponse("pseo_directory.html", {
        "request": request,
        "topics": topics,
        "page": page,
        "total_pages": (total // per_page) + 1,
        "total_count": total
    })

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Stripe Webhook Handler
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail="Webhook secret not configured")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle checkout.session.completed
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Extract data
        customer_email = session.get("customer_details", {}).get("email")
        amount = session.get("amount_total", 0) / 100  # Convert cents to dollars
        plan = session.get("metadata", {}).get("plan", "annual")
        customer_id = session.get("customer")
        subscription_id = session.get("subscription")
        
        print(f"✅ Payment received: {customer_email} - plan: {plan}")
        
        # Track in PostHog
        posthog.capture(
            distinct_id=customer_email or "anonymous",
            event="payment_received",
            properties={
                "plan": plan,
                "amount": amount
            }
        )
        
        # Update or Create user in database
        if customer_email:
            user = db.query(User).filter(User.email == customer_email).first()
            if not user:
                # Create a placeholder user so they can access the tool immediately
                user = User(
                    email=customer_email,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    plan_type=plan,
                    is_active=True
                )
                db.add(user)
                print(f"👤 Created new user shell for {customer_email}")
            else:
                user.stripe_customer_id = customer_id
                user.stripe_subscription_id = subscription_id
                user.plan_type = plan
                user.is_active = True
                print(f"🔄 Updated existing user {customer_email} to active")
            db.commit()
    
    # Handle subscription cancelled (user stopped paying!)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        subscription_id = subscription.get('id')
        
        print(f"❌ Subscription cancelled: {subscription_id}")
        
        # Find and deactivate the user
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        if user:
            print(f"🗑️ Deactivating vault for: {user.email}")
            user.is_active = False
            db.commit()
            
            # Send human-centered cancellation email
            cancellation_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Georgia, serif; line-height: 1.6; color: #222; max-width: 600px; margin: 0 auto; padding: 40px 20px; background: #fff; }}
                    .footer {{ font-size: 11px; color: #999; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; }}
                </style>
            </head>
            <body>
                <p>hey,</p>
                <p>i just got word that your subscription was cancelled. your vault is now deactivated.</p>
                <p>i'm not going to send you a "please come back" survey or a discount code to win you over. i just want to say thanks for trusting deadhand for a while.</p>
                <p>if you ever want to protect your family again, you know where to find me.</p>
                
                <p>take care,</p>
                <p><strong>deadhand protocol</strong></p>

                <div class="footer">
                    <p>sent by deadhand - built with care in argentina.</p>
                </div>
            </body>
            </html>
            """
            send_email(user.email, "your deadhand vault has been deactivated", cancellation_html)
    
    return {"status": "success"}

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Marketing landing page"""
    return templates.TemplateResponse("landing.html", {
        "request": request,
        "csrf_token": getattr(request.state, "csrf_token", "")
    })

@app.get("/buy")
async def buy_chooser(request: Request):
    """Render the pricing selection page"""
    return templates.TemplateResponse("pricing_select.html", {"request": request})

@app.get("/buy/annual")
async def buy_annual(request: Request):
    """Legacy Stripe Checkout for Annual Plan"""
    try:
        price_id = os.getenv("STRIPE_PRICE_ANNUAL")
        if not price_id:
             # Fallback if config is missing dev mode
             return RedirectResponse(url="/buy")
             
        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=f"{BASE_URL.rstrip('/')}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL.rstrip('/')}/buy",
            metadata={"plan": "annual"}
        )
        return RedirectResponse(url=checkout_session.url, status_code=303)
    except Exception as e:
        posthog.capture_exception(e)
        print(f"Stripe Error: {e}")
        return RedirectResponse(url="/buy")

@app.get("/buy/lifetime")
async def buy_lifetime(request: Request):
    """Stripe Checkout for Lifetime Plan ($400 one-time)"""
    try:
        # Use simple ad-hoc price if env var not set, or create dynamic price
        price_id = os.getenv("STRIPE_PRICE_LIFETIME") 
        
        # If no price ID configured in env, we can't process
        if not price_id:
             # Fallback to annual if config missing or show error
             return RedirectResponse(url="/buy")

        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='payment', # One-time payment, not subscription
            success_url=f"{BASE_URL.rstrip('/')}/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{BASE_URL.rstrip('/')}/buy",
            metadata={"plan": "lifetime"}
        )
        return RedirectResponse(url=checkout_session.url, status_code=303)
    except Exception as e:
        posthog.capture_exception(e)
        print(f"Stripe Error: {e}")
        return RedirectResponse(url="/buy")



def send_founder_welcome(email: str):
    """Send personal founder welcome email via Resend"""
    try:
        api_key = os.getenv("RESEND_API_KEY")
        if not api_key:
            return

        resend.api_key = api_key
        
        # Determine sender from ENV or fallback
        sender = os.getenv("FROM_EMAIL", "Max from Deadhand <max@deadhandprotocol.com>")
        
        # HTML Email Body - Personal, No Corporate BS
        html_body = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333; line-height: 1.6;">
            <p>Hey,</p>
            <p>I just wanted to personally say thank you.</p>
            <p>I understand that your first order is more than just clicking "buy." It's a leap of trust, especially when it comes to securing your legacy. And I don't take that lightly.</p>
            <p>When I started Deadhand, it wasn't some big corporate mission. It was me, obsessed with finding a way to ensure my Bitcoin wouldn't die with me, with no middlemen, no lawyers, and no BS.</p>
            <p>That's still what drives us today. And now you're a part of that story.</p>
            <p>If you've got questions, just hit reply. You'll get a real response, fast.</p>
            <p>Grateful to have you here.</p>
            <br>
            <p>Stay Sovereign,</p>
            <p><strong>Max Comperatore</strong> | Founder</p>
            <p><a href="{BASE_URL}" style="color: #666; text-decoration: none;">Deadhand Protocol</a></p>
            <br>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 14px; color: #666;">P.S. While you set up your vault, <a href="https://discord.gg/eDyCkgvBjf" style="color: #0066cc;">join our private Discord</a>. It's where the smart money hangs out.</p>
        </div>
        """

        resend.Emails.send({
            "from": sender,
            "to": email,
            "subject": "Thank you so much for your order",
            "html": html_body
        })
    except Exception as e:
        print(f"Failed to send welcome email: {e}")

@app.get("/payment-success")
async def payment_success(session_id: str, background_tasks: BackgroundTasks):
    """Set the access cookie and redirect to the tool"""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        email = session.customer_details.email
        
        # Trigger welcome email in background (zero latency for user)
        if email:
            background_tasks.add_task(send_founder_welcome, email)
        
        # Simple signed token: email:hmac(email, secret)
        secret_key = os.getenv('SECRET_KEY', 'changeme_in_prod')
        signature = hmac.new(secret_key.encode(), email.encode(), hashlib.sha256).hexdigest()
        token = f"{email}:{signature}"
        
        response = RedirectResponse(url="/tools/dead-switch", status_code=303)
        # Set cookie for 1 year with Strict hardening
        response.set_cookie(
            key="dead_auth", 
            value=token, 
            max_age=31536000, 
            httponly=True, 
            secure=True, 
            samesite="lax"
        )
        return response
    except Exception as e:
        print(f"Payment Success Error: {e}")
        return RedirectResponse(url="/")

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    """Terms of Service"""
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/docs", response_class=HTMLResponse)
async def docs_page(request: Request):
    """Documentation - Semantic SEO optimized for AI scraping"""
    return templates.TemplateResponse("docs.html", {"request": request})

# ========== FREE TOOLS ==========

@app.get("/tools/bus-factor", response_class=HTMLResponse)
async def bus_factor_tool(request: Request):
    """Bus Factor Calculator"""
    return templates.TemplateResponse("tools_bus_factor.html", {"request": request})

@app.get("/tools/optical-splitting", response_class=HTMLResponse)
async def optical_splitting_page(request: Request):
    """Optical Splitting Tool - split images into noise shares"""
    return templates.TemplateResponse("tools_visual_steg.html", {"request": request})

@app.get("/tools/acoustic-masking", response_class=HTMLResponse)
async def acoustic_masking_page(request: Request):
    """Acoustic Masking Tool - hide text in WAV files"""
    return templates.TemplateResponse("tools_audio_steg.html", {"request": request})

@app.get("/tools/dead-switch", response_class=HTMLResponse)
async def dead_switch_page(request: Request, db: Session = Depends(get_db)):
    """Dead Mans Switch - tool is public, activation is gated"""
    dead_auth = request.cookies.get("dead_auth")
    email = None
    
    if dead_auth:
        try:
            email_part, signature = dead_auth.split(":")
            secret_key = os.getenv('SECRET_KEY', 'changeme_in_prod')
            expected_signature = hmac.new(secret_key.encode(), email_part.encode(), hashlib.sha256).hexdigest()
            
            # Constant time comparison (prevent timing attacks)
            if hmac.compare_digest(signature, expected_signature):
                email = email_part
                # Check if user exists and is active
                user = db.query(User).filter(User.email == email).first()
                if user and not user.is_active:
                     email = None # Subscription expired/cancelled
            else:
                email = None
        except:
            email = None
            
    return templates.TemplateResponse("tools_dead_switch.html", {
        "request": request, 
        "email": email,
        "csrf_token": getattr(request.state, "csrf_token", "")
    })

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
            
            # Calculate reading time
            words = len(content.split())
            reading_time = max(1, round(words / 200))

            posts.append({
                'title': meta.get('title', ''),
                'slug': meta.get('slug', file.stem),
                'description': meta.get('description', ''),
                'author': meta.get('author', 'Deadhand Team'),
                'date': date_str,
                'date_formatted': date_formatted,
                'tags': tags,
                'tags_list': tags_list,
                'image': meta.get('image', '/static/favicon.png'),
                'reading_time': reading_time
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
        "author": meta.get('author', 'Deadhand Team'),
        "date": date_str,
        "date_formatted": date_formatted,
        "tags": tags,
        "tags_list": tags_list,
        "image": meta.get('image', '/static/og_card.png'),
        "slug": slug,
        "content": html_content,
        "reading_time": reading_time,
        "related_posts": related_posts
    })

@app.get("/docs")
async def docs_index():
    """Redirect documentation to GitHub Source"""
    return RedirectResponse("https://github.com/pyoneerC/deadhand#how-it-works")

@app.get("/docs/{doc_name}", response_class=HTMLResponse)
async def docs_page(request: Request, doc_name: str):
    """Documentation now lives on GitHub to reduce dependency surface area"""
    return RedirectResponse(f"https://github.com/pyoneerC/deadhand/blob/main/docs/{doc_name}.md")

# Deprecated helper function removed to save bytes

# SEO: Competitor Alternatives
@app.get("/alternatives/{competitor}-alternative", response_class=HTMLResponse)
async def competitor_alternative(request: Request, competitor: str):
    """Dynamic competitor comparison pages for high-intent SEO"""
    if competitor not in COMPETITORS:
        raise HTTPException(status_code=404)
        
    data = COMPETITORS[competitor]
    
    return templates.TemplateResponse("competitor_vs.html", {
        "request": request,
        "c": data,
        "competitor_name": data['name'],
        "btc_price": await get_btc_price()
    })

@app.get("/p/{slug}", response_class=HTMLResponse)
async def programmatic_seo_landing(request: Request, slug: str):
    """Dynamic landing pages for programmatic SEO with God Level injections"""
    if slug not in PSEO_TOPICS:
        raise HTTPException(status_code=404)
        
    topic = PSEO_TOPICS[slug]
    btc_price = await get_btc_price()
    
    # 1. Transform Body: Dynamic Variables
    body = topic.get('body', '')
    body = body.replace("{{ BTC_PRICE }}", f"${btc_price:,}")
    
    # 2. Transform Body: Inline Internal Linking (Optimized for 50k+ pages)
    # Instead of checking all 50k topics (O(N)), we pick a random sample to check for linking
    # This keeps response times fast while still building a dense internal graph
    sample_size = min(200, len(PSEO_TOPICS))
    sampled_slugs = random.sample(list(PSEO_TOPICS.keys()), sample_size)
    
    for other_slug in sampled_slugs:
        if other_slug == slug: continue
        other_topic = PSEO_TOPICS[other_slug]
        # Find parts of the title in the text (e.g., "MetaMask" or "Bitcoin")
        anchor_text = other_topic['title'].split(' ')[0]
        if len(anchor_text) > 3: # Avoid linking short words
             # Use a safer regex that ignores words inside HTML tags or existing links
             pattern = re.compile(rf'(<a[^>]*>.*?</a>|<[^>]+>)|(\b{re.escape(anchor_text)}\b)', re.IGNORECASE | re.DOTALL)
             
             found = False
             def link_fixer(m):
                 nonlocal found
                 if m.group(1): # If it's an existing tag or <a> link, leave it alone
                     return m.group(1)
                 if not found: # If it's the anchor and we haven't linked it in this post yet
                     found = True
                     return f'<a href="/p/{other_slug}" class="underline">{m.group(2)}</a>'
                 return m.group(2)
             
             body = pattern.sub(link_fixer, body)

    # 3. Get Related Topics
    all_slugs = list(PSEO_TOPICS.keys())
    other_slugs = [s for s in all_slugs if s != slug]
    related_slugs = random.sample(other_slugs, min(4, len(other_slugs)))
    related_topics = [(s, PSEO_TOPICS[s]['title']) for s in related_slugs]
    
    return templates.TemplateResponse("pseo.html", {
        "request": request,
        "title": topic.get('title'),
        "description": topic.get('description'),
        "h1": topic.get('h1'),
        "intro": topic.get('intro'),
        "body": body,
        "slug": slug,
        "related_topics": related_topics,
        "btc_price": btc_price,
        "date_now": datetime.now().strftime('%Y-%m-%d'),
        "config_hash": hashlib.sha256(slug.encode()).hexdigest()[:12]
    })



@app.post("/vault/create", response_class=HTMLResponse)
async def create_vault(
    request: Request,
    email: str = Form(...),
    beneficiary_email: str = Form(...),
    shard_c: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db)
):
    # Verify CSRF
    cookie_token = request.cookies.get("csrf_token")
    if not cookie_token or not secrets.compare_digest(csrf_token, cookie_token):
        raise HTTPException(status_code=403, detail="CSRF verification failed")

    # Check if user exists (might have been created by Stripe webhook)
    user = db.query(User).filter(User.email == email).first()
    
    # If user exists and already has an ACTIVE vault, don't allow overwrite
    # But if vault was triggered (is_dead = True), allow creating new vault
    if user and user.shard_c and not user.is_dead:
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "error": "A vault already exists for this email. If you need to reset it, please contact support."
        })

    heartbeat_token = secrets.token_urlsafe(32)
    created_timestamp = datetime.now()
    
    # IMMUTABILITY PROTECTION: Create hash of critical config
    config_string = f"{beneficiary_email}|{shard_c}|{created_timestamp.isoformat()}"
    config_hash = hashlib.sha256(config_string.encode()).hexdigest()
    
    # Encrypt shard_c before storing (key derived from heartbeat_token)
    encrypted_shard = encrypt_shard(shard_c, heartbeat_token)
    
    if not user:
        user = User(email=email)
        db.add(user)
    
    # Encrypt heartbeat_token to protect it in DB
    # We use the server SECRET_KEY (env var) as the master key
    server_master_key = os.getenv('SECRET_KEY', 'changeme_in_prod')
    encrypted_heartbeat_token = encrypt_token(heartbeat_token, server_master_key)

    user.beneficiary_email = beneficiary_email
    user.shard_c = encrypted_shard
    user.config_hash = config_hash
    user.heartbeat_token = encrypted_heartbeat_token
    user.last_heartbeat = created_timestamp
    
    db.commit()
    db.refresh(user)

    # Track in PostHog
    posthog.capture(
        distinct_id=email,
        event="vault_created",
        properties={
            "beneficiary_email": beneficiary_email
        }
    )

    # Calendar reminder (29 days from now)
    reminder_dt = datetime.now() + timedelta(days=29)
    cal_date = reminder_dt.strftime('%Y%m%d')
    cal_end = (reminder_dt + timedelta(days=1)).strftime('%Y%m%d')
    cal_title = quote_plus("Deadhand Heartbeat - Reset Your 30-Day Timer")
    cal_details = quote_plus(f"Time to visit deadhandprotocol.com/heartbeat/{user.id}/{heartbeat_token} to reset your watchdog timer.")
    welcome_cal_url = f"https://www.google.com/calendar/render?action=TEMPLATE&text={cal_title}&dates={cal_date}/{cal_end}&details={cal_details}&sf=true&output=xml"

    # Send human-centered "Chewy-style" welcome email
    welcome_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Georgia, serif; line-height: 1.6; color: #222; max-width: 600px; margin: 0 auto; padding: 40px 20px; background: #fff; }}
            .content {{ background: #fff; padding: 0; }}
            h1 {{ font-size: 22px; color: #000; font-weight: normal; margin-top: 0; text-decoration: underline; }}
            .image-container {{ text-align: left; margin: 40px 0; }}
            .image-container img {{ max-width: 100%; border: 1px solid #eee; }}
            .instructions {{ background: #fefefe; padding: 20px; border: 1px dashed #ccc; margin: 30px 0; font-family: monospace; font-size: 13px; }}
            .heartbeat-link {{ display: inline-block; color: #000 !important; text-decoration: underline; font-weight: bold; margin: 20px 0; }}
            .footer {{ font-size: 11px; color: #999; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="content">
            <h1>it's not just a welcome email.</h1>
            
            <p>hey there,</p>
            
            <p>i'm max, the founder of deadhand.</p>
            
            <p>i could have sent you a shiny, corporate html template with "action required" in the subject. but deadhand isn't a typical app, and you aren't a typical user.</p>
            
            <p>you just made a hard choice. thinking about what happens "after" isn't exactly fun. but the fact that you're here means you deeply care about someone and you want to protect them no matter what. that’s a powerful thing, and it deserves more than a form letter.</p>
            
            <p>in a digital world that's getting colder by the second, i wanted to give you something "handmade." since my actual drawing skills stopped improving in kindergarten, i used a specialized ai to help me create a "photo" of a crayon drawing i made while thinking about this project. it’s imperfect, it's a bit silly, but it’s real to me.</p>

            <div class="image-container">
                <img src="https://deadhandprotocol.com/static/Deadhand_welcome_crayon_polaroid_en.png" alt="a drawing of a family for you">
            </div>

            <p>i want you to know that on the other side of this complex math is a real person who understands the weight of what you're setting up. i don't take that trust lightly.</p>

            <div class="instructions">
                <strong>vault active for: {email}</strong><br>
                beneficiary: {beneficiary_email}<br>
                system: 2-of-3 shamir's secret sharing<br>
                status: secured
            </div>

            <p>take a breath. your family is safe now. there’s no rush to do anything else right now. just keep your shard a safe, and make sure your beneficiary has shard b.</p>

            <p><strong>one critical thing:</strong> to make sure you're still with us, we need a "heartbeat." click the link below once just to verify you can access it. it resets your 90-day timer.</p>

            <a href="https://deadhandprotocol.com/heartbeat/{user.id}/{heartbeat_token}" class="heartbeat-link">verify my heartbeat & reset timer</a>

            <p><strong>pro tip:</strong> set a reminder so you don't forget. <a href="{welcome_cal_url}" target="_blank">add a reminder to my google calendar</a> (for 30 days from now).</p>

            <div class="image-container">
                <img src="https://deadhandprotocol.com/static/Deadhand_napkin_note.png" alt="handwritten note on a napkin: your family is safe now">
            </div>

            <p><strong>this is my personal email.</strong> if you have a question, a fear, or just want to tell me how your setup went, just reply. i read them. i answer them.</p>
            
            <p>deeply grateful you're here,</p>
            
            <p><strong>max</strong><br>
            founder of deadhand<br>
            <i>(the guy who sends you crayon drawings)</i></p>

            <div class="footer">
                <p>deadhand - protecting your crypto legacy.</p>
                <p>built with care in argentina. open source. trustless by design.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(email, "not just a welcome email (and a drawing for you)", welcome_html)

    return templates.TemplateResponse("success.html", {"request": request})

@app.get("/heartbeat/{user_id}/{token}", response_class=HTMLResponse)
async def heartbeat(request: Request, user_id: int, token: str, db: Session = Depends(get_db)):
    # We query by ID first (user_id is primary key)
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return HTMLResponse("Invalid link", status_code=404)
        
    # Verify token
    server_master_key = os.getenv('SECRET_KEY', 'changeme_in_prod')
    # Decrypt the stored token to compare with the one in the URL
    stored_token_decrypted = decrypt_token(user.heartbeat_token, server_master_key)
    
    # Constant-time comparison
    if not secrets.compare_digest(stored_token_decrypted, token):
         return HTMLResponse("Invalid link or token", status_code=403)
    
    # CRITICAL: If user was marked dead, shard C was already released
    # They CANNOT resurrect - must create new vault with new seed
    if user.is_dead:
        return templates.TemplateResponse("vault_triggered.html", {
            "request": request,
            "email": user.email,
            "beneficiary_email": user.beneficiary_email
        })
    
    user.last_heartbeat = datetime.now()
    db.commit()
    
    # Calculate next dates
    now = datetime.now()
    next_check_in_dt = now + timedelta(days=30)
    reminder_dt = now + timedelta(days=29)
    
    next_check_in_str = next_check_in_dt.strftime('%B %d, %Y').lower()
    
    # Create Google Calendar link (all-day event)
    cal_date = reminder_dt.strftime('%Y%m%d')
    cal_end = (reminder_dt + timedelta(days=1)).strftime('%Y%m%d')
    title = quote_plus("Deadhand Heartbeat - Reset Your 30-Day Timer")
    details = quote_plus(f"Time to visit deadhandprotocol.com/heartbeat/{user_id}/{token} to reset your watchdog timer. If you miss this, your beneficiary will eventually receive shard C.")
    cal_url = f"https://www.google.com/calendar/render?action=TEMPLATE&text={title}&dates={cal_date}/{cal_end}&details={details}&sf=true&output=xml"
    
    return templates.TemplateResponse("check_in.html", {
        "request": request, 
        "next_date": next_check_in_str,
        "calendar_url": cal_url
    })

@app.get("/recover", response_class=HTMLResponse)
async def recover_page(request: Request):
    return templates.TemplateResponse("recover.html", {"request": request})

@app.get("/careers", response_class=HTMLResponse)
async def careers(request: Request):
    return templates.TemplateResponse("careers.html", {"request": request})

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
        results = {"reminders_30d": 0, "warnings_60d": 0, "deaths_90d": 0, "errors": 0}
        
        # Get all active (not dead) users with a valid payment status
        active_users = db.query(User).filter(User.is_dead == False, User.is_active == True).all()
        
        for user in active_users:
            try:
                # Decrypt token for use in emails/links
                server_master_key = os.getenv('SECRET_KEY', 'changeme_in_prod')
                heartbeat_token_plain = decrypt_token(user.heartbeat_token, server_master_key)

                # Handle timezone-aware vs naive datetime
                last_hb = user.last_heartbeat
                if last_hb is None:
                    continue
                if hasattr(last_hb, 'replace') and last_hb.tzinfo is not None:
                    last_hb = last_hb.replace(tzinfo=None)
                days_since_heartbeat = (now - last_hb).days
                
                # 30-day reminder - chewy style
                if 29 <= days_since_heartbeat <= 31:
                    reminder_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Georgia, serif; line-height: 1.6; color: #222; max-width: 600px; margin: 0 auto; padding: 40px 20px; background: #fff; }}
                            .heartbeat-link {{ display: inline-block; color: #000 !important; text-decoration: underline; font-weight: bold; margin: 20px 0; }}
                            .footer {{ font-size: 11px; color: #999; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; }}
                        </style>
                    </head>
                    <body>
                        <p>hey,</p>
                        <p>it's been 30 days since we last heard from you. i'm just checking in to make sure everything is okay.</p>
                        <p>could you click the link below? it just tells our system you're still with us and resets your timer. it takes two seconds.</p>
                        
                        <a href="https://deadhandprotocol.com/heartbeat/{user.id}/{heartbeat_token_plain}" class="heartbeat-link">i'm still here</a>

                        <p><strong>pro tip:</strong> if you're busy now, add a reminder to your calendar for tomorrow so you don't forget.<br>
                        <a href="https://www.google.com/calendar/render?action=TEMPLATE&text={quote_plus('Deadhand Heartbeat Reminder')}&dates={(datetime.now()+timedelta(days=1)).strftime('%Y%m%d')}/{(datetime.now()+timedelta(days=2)).strftime('%Y%m%d')}&details={quote_plus('Visit deadhandprotocol.com/heartbeat/'+str(user.id)+'/'+str(heartbeat_token_plain))}&sf=true&output=xml" target="_blank">add reminder for tomorrow</a></p>

                        <p>if you don't click it, no big deal for now. i'll check in again in another 30 days. but after 90 days of silence, we'll have to send shard c to your beneficiary.</p>
                        
                        <p>stay safe out there,</p>
                        <p><strong>deadhand protocol</strong></p>

                        <div class="footer">
                            <p>sent by Deadhand - built with care in argentina.</p>
                        </div>
                    </body>
                    </html>
                    """
                    send_email(user.email, "quick check-in from Deadhand", reminder_html)
                    results["reminders_30d"] += 1
                
                # 60-day warning - urgent but human
                elif 59 <= days_since_heartbeat <= 61:
                    warning_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Georgia, serif; line-height: 1.6; color: #222; max-width: 600px; margin: 0 auto; padding: 40px 20px; background: #fff; }}
                            .heartbeat-link {{ display: inline-block; color: #000 !important; text-decoration: underline; font-weight: bold; margin: 20px 0; }}
                            .footer {{ font-size: 11px; color: #999; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; }}
                            .warning-box {{ border: 1px dashed #ff4444; padding: 20px; margin: 20px 0; }}
                        </style>
                    </head>
                    <body>
                        <p>hey,</p>
                        <p>i'm getting a little worried. we haven't heard from you in 60 days.</p>
                        
                        <div class="warning-box">
                            <p><strong>just 30 days left.</strong></p>
                            <p>if you don't click the link below within the next month, our system will assume the worst and automatically send shard c to your beneficiary.</p>
                        </div>

                        <p>if you're just busy, i totally get it. but please, click this now so we don't worry your family unnecessarily:</p>
                        
                        <a href="https://deadhandprotocol.com/heartbeat/{user.id}/{heartbeat_token_plain}" class="heartbeat-link">i'm here, reset the timer</a>

                        <p>talk soon,</p>
                        <p><strong>deadhand protocol</strong></p>

                        <div class="footer">
                            <p>sent by Deadhand - protecting your crypto legacy.</p>
                        </div>
                    </body>
                    </html>
                    """
                    send_email(user.email, "urgent: we haven't heard from you in 60 days", warning_html)
                    results["warnings_60d"] += 1
                
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
                            results["errors"] += 1
                            continue
                    
                    try:
                        shard_c_value = decrypt_shard(user.shard_c, heartbeat_token_plain)
                    except Exception:
                        # Old user with unencrypted shard - use raw value
                        shard_c_value = user.shard_c
                    
                    user.is_dead = True
                    death_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Georgia, serif; line-height: 1.6; color: #222; max-width: 600px; margin: 0 auto; padding: 40px 20px; background: #fff; }}
                            h1 {{ font-size: 22px; color: #000; font-weight: normal; margin-top: 0; text-decoration: underline; }}
                            .shard-box {{ background: #fefefe; border: 1px dashed #ccc; padding: 25px; margin: 30px 0; font-family: monospace; font-size: 13px; word-break: break-all; color: #222; }}
                            .instructions {{ background: #fff; border: 1px solid #eee; padding: 20px; border-radius: 4px; margin: 30px 0; }}
                            .footer {{ font-size: 11px; color: #999; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; }}
                            .cta-box {{ background: #fafafa; border: 1px solid #ddd; padding: 25px; margin-top: 40px; text-align: center; }}
                            .cta-link {{ display: inline-block; background: #222; color: #fff !important; text-decoration: none; padding: 12px 20px; border-radius: 4px; font-weight: bold; margin-top: 15px; }}
                        </style>
                    </head>
                    <body>
                        <h1>a message from Deadhand.</h1>
                        
                        <p>hello,</p>
                        <p>i'm writing to you because 90 days ago, <strong>{user.email}</strong> entrusted our system to reach out to you if we stopped hearing from them.</p>
                        
                        <p>we haven't received a heartbeat check-in from them in three months. as per their explicit instructions, i am now releasing the final piece of their digital legacy to you.</p>

                        <p>this is <strong>shard c</strong>. it's one of three pieces needed to access their crypto assets. if they followed our setup guide, you should already have <strong>shard b</strong> (likely a printed document or a digital file they gave you).</p>

                        <div class="shard-box">
                            <strong>shard c value:</strong><br>
                            {shard_c_value}
                        </div>

                        <div class="instructions">
                            <p><strong>how to use this:</strong></p>
                            <ol>
                                <li>locate <strong>shard b</strong> (the one they gave you).</li>
                                <li>go to <a href="https://deadhandprotocol.com/recover">deadhandprotocol.com/recover</a>.</li>
                                <li>enter both shard b and shard c into the tool.</li>
                                <li>the tool will reconstruct their original seed phrase for you.</li>
                            </ol>
                        </div>

                        <p>my deepest condolences for whatever situation has led to this email. i built Deadhand specifically so that people wouldn't have to worry about their loved ones being locked out of their hard-earned assets during difficult times.</p>
                        
                        <p>i hope this tool helps you in some small way.</p>

                        <p>with respect,</p>
                        <p><strong>deadhand protocol</strong></p>

                        <div class="cta-box">
                            <p style="font-size: 14px;"><strong>protect your own legacy</strong></p>
                            <p style="font-size: 13px; color: #666;">you've just seen how Deadhand works. if you have crypto, don't leave your family in the dark. set up your own trustless switch in 5 minutes.</p>
                            <a href="https://deadhandprotocol.com" class="cta-link">create your vault</a>
                        </div>

                        <div class="footer">
                            <p>sent by Deadhand - built with care in argentina.</p>
                        </div>
                    </body>
                    </html>
                    """
                    send_email(user.beneficiary_email, "important: digital recovery key for " + user.email, death_html)
                    results["deaths_90d"] += 1
                    
            except Exception as e:
                results["errors"] += 1
                results["last_error"] = str(e)
                continue
        
        db.commit()
        results["users_checked"] = len(active_users)
        return {"status": "ok", "results": results}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Simulate endpoint removed
