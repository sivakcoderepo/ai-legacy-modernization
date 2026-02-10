# Quick Start Guide - Legacy Code Modernization Platform

## 🚀 5-Minute Setup

### Prerequisites Check
- ✅ Node.js 18+ installed
- ✅ Python 3.11+ installed
- ✅ OpenAI API key ready

### Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies (if not already done)
pip install fastapi uvicorn langchain langchain-openai python-dotenv langgraph

# Set OpenAI API key
# Create .env file with: OPENAI_API_KEY=your-key-here

# Start backend
uvicorn main:app --reload
```

Backend should now be running at `http://127.0.0.1:8000`

### Step 2: Angular UI Setup (3 minutes)

**Option A: Automatic Setup**
```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh
./setup.sh
```

**Option B: Manual Setup**
```bash
cd angular-modernization-ui
npm install
npm start
```

Application will open at `http://localhost:4200`

## 📖 How to Use

### 1. Upload VB File
- Click the upload area or drag your VB file
- Supported formats: .vb, .bas, .cls, .frm
- Preview will show first 500 characters

### 2. Start Modernization
- Click "🚀 Start Modernization"
- Watch real-time progress through 5 steps

### 3. Review Each Step
Each step shows AI-generated output:
- ✅ **Approve & Continue** - Move to next step
- ✏️ **Modify** - Edit output (coming soon)
- 🔄 **Start Over** - Reset entire process

### 4. Download Results
- Download individual step outputs
- Download complete modernization package at the end

## 🎯 Expected Flow

```
Upload VB File
    ↓
Business Logic Analysis (Step 1)
    ↓ [Approve]
Domain Model (Step 2)
    ↓ [Approve]
Backend Design (Step 3)
    ↓ [Approve]
Frontend Design (Step 4)
    ↓ [Approve]
Cloud Architecture (Step 5)
    ↓ [Approve]
Complete! 🎉
```

## 💡 Tips

- **Larger Files**: May take 2-5 minutes to process
- **Streaming**: Results appear in real-time as AI generates them
- **Approval Required**: You must approve each step to proceed
- **Downloads**: Available at each step and at completion

## 🐛 Common Issues

### "Backend not running" error
**Solution**: Ensure backend is started and accessible at http://127.0.0.1:8000

### CORS errors in browser console
**Solution**: Check backend CORS settings include `http://localhost:4200`

### No streaming updates
**Solution**: 
1. Verify updated agents are copied to main project
2. Check orchestrator.py supports streaming
3. Restart backend

### File upload not working
**Solution**: Check file format is .vb, .bas, .cls, or .frm

## 📊 Test Example

Use the VB code from `main.py` as a test:
1. Copy the VB code section
2. Save as `test.vb`
3. Upload to application
4. Process through all steps

## 🔧 Architecture

```
User Interface (Angular)
        ↓
FastAPI Backend (/chat/stream)
        ↓
LangGraph Orchestrator
        ↓
AI Agents (5 steps)
        ↓
Streaming Response
```

## 📞 Support

If you encounter issues:
1. Check browser console for errors
2. Check backend terminal for Python errors
3. Verify OpenAI API key is valid
4. Ensure all dependencies are installed

## 🎓 Next Steps

After successful setup:
- Try with your own VB files
- Customize agent prompts in `agents/` directory
- Modify UI styling in component CSS files
- Add authentication (future enhancement)
- Implement output editing (future enhancement)

## ✨ Features Overview

| Feature | Status |
|---------|--------|
| File Upload | ✅ Working |
| Real-time Streaming | ✅ Working |
| Step-by-step Approval | ✅ Working |
| Download Outputs | ✅ Working |
| Output Modification | 🚧 Coming Soon |
| Multi-file Upload | 🚧 Future |
| Session Persistence | 🚧 Future |
| User Authentication | 🚧 Future |

Ready to modernize your legacy code! 🚀
