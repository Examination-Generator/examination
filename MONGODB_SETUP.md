# MongoDB Setup Guide

## ⚠️ MongoDB is Not Running!

The error you're seeing means MongoDB is not installed or not running on your system.

## 🚀 Quick Fix Options

### Option 1: Install MongoDB Community Edition (Recommended)

1. **Download MongoDB:**
   - Go to: https://www.mongodb.com/try/download/community
   - Download MongoDB Community Server for Windows
   - Choose the latest version (7.x or 8.x)

2. **Install MongoDB:**
   - Run the installer
   - Choose "Complete" installation
   - Check "Install MongoDB as a Service" ✅
   - Check "Install MongoDB Compass" (GUI tool) ✅

3. **Verify Installation:**
   ```powershell
   # Check if MongoDB service is running
   Get-Service MongoDB
   
   # Should show: Status = Running
   ```

4. **Test Connection:**
   ```powershell
   cd backend
   node test-db-connection.js
   ```

### Option 2: Use MongoDB Atlas (Cloud - FREE)

1. **Create Free Account:**
   - Go to: https://www.mongodb.com/cloud/atlas/register
   - Sign up for free (no credit card required)

2. **Create Cluster:**
   - Click "Build a Database"
   - Choose "FREE" (M0 Sandbox)
   - Select closest region
   - Click "Create"

3. **Setup Access:**
   - **Database Access**: Create user with password
   - **Network Access**: Add IP `0.0.0.0/0` (allow all)

4. **Get Connection String:**
   - Click "Connect" on your cluster
   - Choose "Connect your application"
   - Copy connection string

5. **Update `.env` file:**
   ```properties
   MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/test?retryWrites=true&w=majority
   ```
   Replace `username`, `password`, and cluster URL with yours.

## 🔍 Current Issue Explained

The error message `ENOTFOUND testing` is misleading. What's actually happening:

1. Your app tries to connect to: `mongodb://localhost:27017/test`
2. MongoDB is not running at localhost:27017
3. Node.js tries to resolve "localhost" as a hostname
4. The connection fails

The word "testing" in the error is from the database name being parsed incorrectly when the connection fails.

## ✅ After MongoDB is Running

1. **Seed the database:**
   ```powershell
   cd backend
   npm run seed
   ```

2. **Start the server:**
   ```powershell
   npm run dev
   ```

3. **You should see:**
   ```
   ✅ MongoDB Connected: localhost
   📚 Database: test
   🚀 Server running on port 5000
   ```

## 🆘 Still Having Issues?

### Check if MongoDB is installed:
```powershell
# Try to find MongoDB installation
Get-Service | Where-Object {$_.Name -like "*mongo*"}
```

### Check if port 27017 is in use:
```powershell
netstat -ano | findstr :27017
```

### Manual MongoDB start (if service not running):
```powershell
# Navigate to MongoDB bin directory (adjust path)
cd "C:\Program Files\MongoDB\Server\7.0\bin"
mongod.exe --dbpath "C:\data\db"
```

## 📝 Recommended: Option 1

For development, installing MongoDB Community Edition locally is best because:
- ✅ Works offline
- ✅ Faster (no network latency)
- ✅ Full control
- ✅ Free forever
- ✅ No connection string complexity

## 🌐 Alternative: Option 2

Use MongoDB Atlas if:
- ✅ Don't want to install locally
- ✅ Need to share database with team
- ✅ Want automatic backups
- ✅ Need production-like environment

---

**Choose one option and follow the steps above. After MongoDB is running, everything will work!** 🎉
