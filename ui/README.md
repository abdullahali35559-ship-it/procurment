# 🚀 Procurement Agent UI - Quick Start Guide

## 📄 **Single Command to Open All Pages**

### **Option 1: Launcher Page (Recommended)**
```powershell
# Open beautiful launcher with all pages
start ui\launcher.html
```

**Features:**
- 🎨 Beautiful gradient design
- 📱 All 6 pages in one view
- 🔗 Click any card to open that page
- ⚡ Fast & easy navigation

---

### **Option 2: Python Web Server (All Pages)**
```powershell
# Start local web server on port 3000
cd "D:\Procurement agent\ui"
python -m http.server 3000
```

**Then open in browser:**
```
http://localhost:3000/launcher.html
```

**Benefits:**
- ✅ No file:// path issues
- ✅ All pages work together
- ✅ Proper CORS for backend
- ✅ Professional development setup

---

## 🔄 **Outlook Token Refresh**

### **Automatic Refresh Script Created!**

**File:** `refresh_outlook_token.py`

### **Usage:**

#### **Manual Refresh:**
```powershell
python refresh_outlook_token.py
```

**What it does:**
```
✅ Checks if token is expired
✅ Automatically refreshes if needed
✅ Saves new token to .outlook_oauth_token.json
✅ Tests token with Graph API
✅ Shows expiry time
```

#### **In Your Code:**
```python
from refresh_outlook_token import get_valid_token

# Get valid token (auto-refreshes if needed)
access_token = get_valid_token()

if access_token:
    # Use token to call Microsoft Graph API
    headers = {"Authorization": f"Bearer {access_token}"}
    # ... make API calls
```

---

## 🧪 **Test Token Refresh Now:**

```powershell
cd "D:\Procurement agent"
python refresh_outlook_token.py
```

**Expected Output:**
```
🔄 Outlook Token Refresh
============================================
✅ Token is still valid for 58 minutes

OR

⏳ Token expired or expiring soon. Refreshing...
✅ Token saved to .outlook_oauth_token.json
🎉 Token refreshed successfully!
✅ New token expires in: 60 minutes
```

---

## 📁 **File Structure:**

```
D:/Procurement agent/
├── ui/
│   ├── launcher.html          ← 🆕 Single launch page for all
│   ├── index.html             ← Dashboard
│   ├── tenders.html           ← Tenders
│   ├── emails.html            ← Emails
│   ├── clients.html           ← Clients
│   ├── documents.html         ← Documents
│   └── settings.html          ← Settings
│
├── refresh_outlook_token.py   ← 🆕 Auto-refresh script
├── .outlook_oauth_token.json  ← Token storage
└── test_backend_api.py        ← Test backend
```

---

## ⚡ **Complete Workflow:**

### **1. Start Backend:**
```powershell
cd "D:\Procurement agent"
python test_backend_api.py
```

### **2. Open UI Launcher:**
```powershell
start ui\launcher.html
```

### **3. Refresh Token (if needed):**
```powershell
python refresh_outlook_token.py
```

### **4. Navigate:**
- Click any card in launcher
- Access all 6 pages
- Everything connected!

---

## 🎨 **Launcher Features:**

```
┌────────────────────────────────────┐
│     🚀 Procurement Agent                   │
│     Modern Tender Management       │
├────────────────────────────────────┤
│  [Dashboard]    [Tenders]          │
│  Overview       All tenders        │
│                                    │
│  [Emails]       [Documents]        │
│  Messages       File manager       │
│                                    │
│  [Clients]      [Settings]         │
│  Management     Configuration      │
└────────────────────────────────────┘
```

---

## 🔐 **Token Auto-Refresh in Backend:**

Add to your FastAPI backend:

```python
from refresh_outlook_token import get_valid_token

@app.get("/api/emails")
async def fetch_outlook_emails():
    # Automatically gets valid token (refreshes if needed)
    access_token = get_valid_token()
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Outlook not authenticated")
    
    # Use token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/messages",
        headers=headers
    )
    
    return response.json()
```

**Benefits:**
- ✅ No manual token refresh needed
- ✅ Automatic expiry checking
- ✅ Seamless token rotation
- ✅ Always valid tokens

---

## 🎯 **Quick Commands Summary:**

```powershell
# Open everything at once
start ui\launcher.html

# Refresh Outlook token
python refresh_outlook_token.py

# Start backend
python test_backend_api.py

# Start web server (alternative)
cd ui && python -m http.server 3000
```

---

**All set! One click ab sab pages khul jayenge! 🚀**
