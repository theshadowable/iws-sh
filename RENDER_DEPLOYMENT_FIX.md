# Render Deployment Fix - MongoDB URL Encoding

## Problem
The deployment on Render was failing with the following error:
```
pymongo.errors.InvalidURI: Username and password must be escaped according to RFC 3986, use urllib.parse.quote_plus
```

## Root Cause
MongoDB connection strings with special characters in the username or password need to be URL-encoded according to RFC 3986. Characters like `@`, `:`, `/`, `?`, `#`, `[`, `]`, and others must be percent-encoded.

## Solution Implemented

### Backend Fix (server.py)

1. **Added import**: `from urllib.parse import quote_plus`

2. **Created `get_mongo_url()` function** that:
   - Automatically detects if credentials are present in the MONGO_URL
   - Extracts username and password from the connection string
   - URL-encodes both username and password using `quote_plus()`
   - Reconstructs the connection string with encoded credentials
   - Supports both `mongodb://` and `mongodb+srv://` protocols
   - Handles errors gracefully and logs warnings if parsing fails

### How It Works

#### Example 1: Simple URL (no change needed)
```
mongodb://localhost:27017
→ mongodb://localhost:27017
```

#### Example 2: URL with special characters
```
mongodb://user@name:p@ssw0rd!@cluster0.mongodb.net/mydb
→ mongodb://user%40name:p%40ssw0rd%21@cluster0.mongodb.net/mydb
```

#### Example 3: MongoDB Atlas URL
```
mongodb+srv://admin:My$ecret!Pass@cluster0.abc123.mongodb.net/?retryWrites=true
→ mongodb+srv://admin:My%24ecret%21Pass@cluster0.abc123.mongodb.net/?retryWrites=true
```

## Configuration for Render

### Option 1: Use URL-Encoded Password Directly (Recommended)

Set the MONGO_URL environment variable in Render with pre-encoded credentials:

```bash
# If your password is: MyP@ssw0rd!123
# Encode it using Python:
python3 -c "from urllib.parse import quote_plus; print(quote_plus('MyP@ssw0rd!123'))"
# Output: MyP%40ssw0rd%21123

# Then set in Render:
MONGO_URL=mongodb+srv://username:MyP%40ssw0rd%21123@cluster0.mongodb.net/dbname?retryWrites=true&w=majority
```

### Option 2: Let the Code Auto-Encode (Current Implementation)

Simply set the MONGO_URL with raw credentials, and the code will automatically encode them:

```bash
MONGO_URL=mongodb+srv://username:MyP@ssw0rd!123@cluster0.mongodb.net/dbname?retryWrites=true&w=majority
```

The `get_mongo_url()` function will automatically convert it to:
```bash
mongodb+srv://username:MyP%40ssw0rd%21123@cluster0.mongodb.net/dbname?retryWrites=true&w=majority
```

## Setting Up MongoDB Atlas for Render

### Step 1: Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for a FREE account
3. Create a new cluster (FREE M0 tier)

### Step 2: Create Database User
1. In Atlas, go to **Database Access**
2. Click **Add New Database User**
3. Choose **Password Authentication**
4. Username: `indowater_user` (or any name)
5. Password: Use **Autogenerate Secure Password** or create your own
   - **IMPORTANT**: Save this password securely!
6. Database User Privileges: **Read and write to any database**
7. Click **Add User**

### Step 3: Whitelist Render's IP
1. In Atlas, go to **Network Access**
2. Click **Add IP Address**
3. Click **Allow Access from Anywhere** (0.0.0.0/0)
   - This is necessary for Render's dynamic IPs
4. Click **Confirm**

### Step 4: Get Connection String
1. In Atlas, go to **Database** → **Connect**
2. Choose **Connect your application**
3. Select **Driver: Python**, **Version: 3.11 or later**
4. Copy the connection string:
   ```
   mongodb+srv://indowater_user:<password>@cluster0.abc123.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password

### Step 5: Configure Render Environment Variables

In your Render dashboard:

1. Go to your service → **Environment** tab
2. Add/Update the following environment variables:

```bash
MONGO_URL=mongodb+srv://indowater_user:YOUR_PASSWORD_HERE@cluster0.abc123.mongodb.net/indowater_db?retryWrites=true&w=majority
DB_NAME=indowater_db
SECRET_KEY=your-secret-key-here-change-in-production
CORS_ORIGINS=https://your-frontend-domain.com
```

**Note**: The code will automatically URL-encode the password, so you can paste it as-is.

## Common Special Characters That Need Encoding

| Character | Encoded | Character | Encoded |
|-----------|---------|-----------|---------|
| `@`       | `%40`   | `!`       | `%21`   |
| `#`       | `%23`   | `$`       | `%24`   |
| `%`       | `%25`   | `&`       | `%26`   |
| `/`       | `%2F`   | `:`       | `%3A`   |
| `?`       | `%3F`   | `=`       | `%3D`   |

## Manual Encoding (if needed)

If you prefer to encode manually:

```python
from urllib.parse import quote_plus

username = "myuser@email"
password = "MyP@ssw0rd!123"

encoded_username = quote_plus(username)  # myuser%40email
encoded_password = quote_plus(password)  # MyP%40ssw0rd%21123

print(f"mongodb+srv://{encoded_username}:{encoded_password}@cluster0.mongodb.net/dbname")
```

## Testing the Connection

After deploying to Render:

1. Check the logs in Render dashboard
2. Look for successful MongoDB connection message
3. If you see connection errors, verify:
   - Database user exists in Atlas
   - Password is correct
   - IP whitelist includes 0.0.0.0/0
   - Connection string format is correct

## Troubleshooting

### Error: "Authentication failed"
- Verify username and password are correct
- Check that the database user has proper permissions

### Error: "Connection timeout"
- Verify IP whitelist includes 0.0.0.0/0
- Check if cluster is running (not paused)

### Error: "Invalid URI"
- Use the auto-encoding solution implemented in server.py
- Or manually encode special characters in password

## Files Modified

1. **backend/server.py**
   - Added `from urllib.parse import quote_plus`
   - Created `get_mongo_url()` function
   - Updated MongoDB client initialization

## Deployment Checklist

- [ ] MongoDB Atlas cluster created (FREE M0)
- [ ] Database user created with password
- [ ] IP whitelist set to 0.0.0.0/0
- [ ] Connection string copied from Atlas
- [ ] MONGO_URL set in Render environment variables
- [ ] DB_NAME set in Render environment variables
- [ ] Code deployed to Render
- [ ] Logs checked for successful connection
- [ ] Backend health check passes

## Next Steps

1. Push the updated `server.py` to GitHub
2. Render will automatically redeploy
3. Check deployment logs for successful MongoDB connection
4. Test API endpoints to verify database connectivity

---

**Fixed**: January 2025
**Status**: Ready for Production Deployment ✅
