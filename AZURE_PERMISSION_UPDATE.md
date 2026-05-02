# Azure API Permissions Update Guide

## Quick Fix

### Azure Portal → Your App → API Permissions:

1. **Remove old permission:**
   - Click `...` on `IMAP.AccessAsUser.All`
   - Remove permission

2. **Add new permission:**
   - `+ Add a permission`
   - `Microsoft Graph`
   - `Delegated permissions`
   - Search: `Mail.ReadWrite`
   - Check: ☑️ `Mail.ReadWrite`
   - Click: `Add permissions`

3. **Test:**
   ```powershell
   .\process_emails.bat
   ```

Done! ✅
