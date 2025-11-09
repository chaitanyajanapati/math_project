MathAI Backend - Installation and Usage Guide
=============================================

SYSTEM REQUIREMENTS:
-------------------
- Windows 10/11 (64-bit)
- No Python installation needed (included in executable)
- 100MB free disk space
- Port 8000 must be available

INSTALLATION STEPS:
------------------
1. Extract the entire folder to a location (e.g., C:\MathAI)
2. DO NOT separate files - keep all folders together:
   - mathai_backend.exe
   - data/
   - mathai_ai_models/

RUNNING THE BACKEND:
-------------------
1. Double-click "mathai_backend.exe" to start the server
2. A console window will open showing server logs
3. Wait for the message: "Uvicorn running on http://0.0.0.0:8000"
4. Keep this window open while using the application

ACCESSING THE APPLICATION:
-------------------------
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- If you have the frontend, configure it to use: http://localhost:8000

STOPPING THE SERVER:
-------------------
- Close the console window, OR
- Press Ctrl+C in the console window

TROUBLESHOOTING:
---------------
1. "Port 8000 already in use":
   - Another application is using port 8000
   - Close other applications or restart your computer

2. "Module not found" errors:
   - Ensure all folders (data/, mathai_ai_models/) are in the same directory as the .exe
   - Re-extract the entire package

3. Server won't start:
   - Check Windows Firewall settings
   - Run as Administrator (right-click .exe → Run as Administrator)

4. Antivirus blocks the .exe:
   - PyInstaller executables may trigger false positives
   - Add an exception for mathai_backend.exe in your antivirus

OPTIONAL: LLM Integration
-------------------------
If you want AI-powered question generation (optional):
1. Install Ollama from: https://ollama.ai/download
2. Run: ollama pull phi
3. Restart mathai_backend.exe

NOTES:
------
- First startup may take 10-20 seconds
- The server runs locally on your machine (no internet required)
- Data is stored in the data/ folder
- Logs are printed to the console window

SUPPORT:
--------
For issues or questions, contact your system administrator.

Version: 1.0
Last Updated: November 2025
