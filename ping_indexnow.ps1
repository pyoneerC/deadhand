# IndexNow Ping Script for Deadhand Protocol
# Run this after deploying to get Bing/Yandex to crawl immediately

$key = "d3adh4ndpr0t0c0l2026x"
$baseUrl = "https://deadhandprotocol.com"

$pages = @(
    "/",
    "/tools/dead-switch",
    "/tools/optical-splitting",
    "/tools/acoustic-masking",
    "/buy",
    "/buy/annual",
    "/buy/lifetime",
    "/blog",
    "/docs",
    "/docs/how-it-works",
    "/docs/security",
    "/docs/faq",
    "/docs/roadmap",
    "/recover"
)

Write-Host "🚀 Pinging IndexNow for Deadhand Protocol..." -ForegroundColor Cyan
Write-Host ""

foreach ($page in $pages) {
    $url = "$baseUrl$page"
    $pingUrl = "https://api.indexnow.org/indexnow?url=$url&key=$key"
    
    try {
        $response = Invoke-WebRequest -Uri $pingUrl -Method Get -TimeoutSec 10 -ErrorAction SilentlyContinue
        Write-Host "✅ $page" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ $page (may still work)" -ForegroundColor Yellow
    }
    
    # Small delay to avoid rate limiting
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "✅ Done! Bing/Yandex should crawl these pages within minutes." -ForegroundColor Green
Write-Host ""
Write-Host "Verify your key is working:" -ForegroundColor Cyan
Write-Host "$baseUrl/$key.txt" -ForegroundColor White
