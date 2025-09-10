# Changelog - YCast RM50 AudioCenter

## R50-Specific Fixes and Enhancements

### Fixed Issues
- **URL Encoding**: Fixed spaces and special characters in API requests
- **Case Sensitivity**: Search terms now converted to lowercase for better results
- **Missing Import**: Added `http.client` import to fix connection errors
- **HTTPS Filtering**: Only HTTP streams are returned for R50 compatibility
- **XML Response**: Optimized XML format for reliable R50 parsing

### Enhanced Features
- **Systemd Service**: Automatic startup on system boot
- **Error Handling**: Improved logging and connection stability
- **Radio Browser Integration**: Full genre, name, and location search

### Files Modified
- `ycast/radiobrowser.py` - API request fixes and HTTP filtering
- `ycast/server.py` - XML response optimization
- `examples/ycast.service.example` - Systemd service configuration

### Tested With
- Sagem RM50 1&1 AudioCenter
- Radio Browser API search functionality
- Genre/Name/Location searches working reliably
