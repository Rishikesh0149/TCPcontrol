# PowerShell launcher for TCP Simulator
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting TCP Performance on Packet Loss Simulator... " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

python -m streamlit run app.py
