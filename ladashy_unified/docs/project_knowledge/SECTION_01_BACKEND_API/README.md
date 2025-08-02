

## ✅ FIXED - August 1, 2025

### What was wrong:
1. `get_collector()` was called without the required `config` parameter
2. Service names were case-sensitive (needed 'Plex' not 'plex')
3. `test_connection()` was called with parameters it doesn't accept

### How it was fixed:
1. Added `config` parameter to `get_collector()` call
2. Made collector lookup case-insensitive in `manager.py`
3. Changed `test_connection()` call to use no parameters

### Verified working:
- Tested with curl: Returns 200 with success message
- Tested with real Radarr instance: Connection successful
