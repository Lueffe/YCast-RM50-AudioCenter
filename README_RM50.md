# YCast for Sagem RM50 1&1 AudioCenter

Enhanced YCast fork specifically optimized for **Sagem RM50 1&1 AudioCenter** devices.

## 🎯 R50 AudioCenter Specific Features

### ✅ Compatibility Fixes
- **HTTP-only Stream Filtering** - Automatically filters out HTTPS streams that R50 cannot handle
- **URL Encoding Fix** - Properly handles spaces and special characters in station names and search queries
- **Case-insensitive Search** - Converts search terms to lowercase for better Radio Browser API results
- **XML Response Optimization** - Simplified XML format for reliable R50 device parsing
- **Missing Import Fix** - Adds required `http.client` import for stable API connections

### 🚀 Enhanced Features
- **Systemd Auto-start Service** - Automatic YCast startup on system boot
- **Improved Error Handling** - Better logging and connection stability
- **Radio Browser Integration** - Full genre, name, and location search functionality

## 📱 Tested Devices
- ✅ **Sagem RM50 1&1 AudioCenter** - Fully tested and optimized
- ✅ **Radio Browser API** - Complete integration with search functions
- ✅ **Genre/Location/Name Search** - All search types working reliably

## 🔧 Installation & Setup

### Quick Start
```bash
# Clone the repository
git clone https://github.com/[YOUR_USERNAME]/YCast-RM50-AudioCenter.git
cd YCast-RM50-AudioCenter

# Install dependencies
pip3 install -r requirements.txt

# Run YCast
python3 -m ycast
```

### Systemd Service (Recommended)
```bash
# Copy service file
sudo cp examples/ycast.service /etc/systemd/system/

# Enable auto-start
sudo systemctl enable ycast
sudo systemctl start ycast

# Check status
sudo systemctl status ycast
```

## 🌐 DNS Configuration for R50

Configure your router to redirect vTuner domains to your YCast server:
- `radioyamaha.vtuner.com` → Your YCast IP
- `denon.vtuner.com` → Your YCast IP  
- `onkyo.vtuner.com` → Your YCast IP

## 📋 R50-Specific Changes

### radiobrowser.py
- Fixed URL encoding in `search()` and `search_by_genre()` functions
- Added case-insensitive search term handling
- Added missing `http.client` import
- HTTP-only stream filtering for R50 compatibility

### server.py  
- Optimized XML response format for R50 parsing
- Simplified station list structure
- Enhanced error handling for device requests

### systemd Integration
- Created `ycast.service` for automatic startup
- Configured proper restart policies
- Integrated with system logging

## 🐛 Known Issues & Solutions

### R50 Cannot Play HTTPS Streams
**Solution:** YCast automatically filters to HTTP-only streams

### Search Returns No Results  
**Solution:** Fixed URL encoding and case sensitivity issues

### Service Doesn't Start on Boot
**Solution:** Use provided systemd service configuration

## 🤝 Contributing

This fork focuses specifically on Sagem RM50 1&1 AudioCenter compatibility. 

### Reporting Issues
Please include:
- R50 AudioCenter model/firmware version
- YCast log output (`journalctl -u ycast`)
- Specific search terms or stations causing issues

## 📄 License

GPL-3.0 License (same as original YCast)

## 🙏 Credits

Based on [THanika/YCast](https://github.com/THanika/YCast) and original [milaq/YCast](https://github.com/milaq/YCast)

Special thanks to the Radio Browser community for the excellent API.

---

**Made with ❤️ for Sagem RM50 1&1 AudioCenter users**
