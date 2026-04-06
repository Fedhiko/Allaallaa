# 🚀 TOKUMA Platform Deployment Guide

## 📋 Deployment Strategy

### **Option 1: Streamlit Community Cloud (Recommended)**
1. **Use the deployment-ready files:**
   - `app-deploy.py` (main app)
   - `requirements-deploy.txt` (simplified dependencies)

2. **Deployment Steps:**
   - Create a GitHub repository
   - Push only the deployment files
   - Connect to Streamlit Community Cloud
   - Deploy using the simplified requirements

### **Option 2: Use Current App with Fixes**
1. **Replace requirements.txt** with `requirements-deploy.txt`
2. **Add dependency handling** to your current app.py

## 🔧 Key Deployment Fixes Applied

### **1. Simplified Dependencies**
- Removed heavy packages (tensorflow, netcdf4, etc.)
- Used deployment-friendly versions
- Added fallback for missing packages

### **2. Graceful Error Handling**
- Mock implementations for missing modules
- Warning messages instead of crashes
- Core functionality preserved

### **3. Database Management**
- SQLite for local storage
- Automatic database initialization
- Error handling for database operations

## 📁 Files for Deployment

### **Required Files:**
```
├── app-deploy.py              # Main deployment app
├── requirements-deploy.txt    # Simplified dependencies
├── .gitignore                # Git ignore file
└── README.md                 # Documentation
```

### **Optional Files:**
```
├── config.toml               # Streamlit config
└── secrets.toml             # API keys (if needed)
```

## 🎯 Deployment Instructions

### **For Streamlit Community Cloud:**

1. **Create GitHub Repository:**
   ```bash
   git init
   git add app-deploy.py requirements-deploy.txt .gitignore
   git commit -m "Initial deployment setup"
   git branch -M main
   git remote add origin https://github.com/yourusername/tokuma-platform.git
   git push -u origin main
   ```

2. **Deploy to Streamlit:**
   - Go to https://share.streamlit.io/
   - Connect your GitHub repository
   - Select `app-deploy.py` as main file
   - Click "Deploy"

3. **Configuration:**
   - Set environment variables if needed
   - Configure app settings in Streamlit dashboard

### **For Other Platforms (Railway, Heroku, etc.):**

1. **Add startup script:**
   ```bash
   streamlit run app-deploy.py --server.port $PORT --server.address 0.0.0.0
   ```

2. **Use requirements-deploy.txt**
3. **Configure environment variables**

## 🚨 Common Deployment Issues & Solutions

### **Issue 1: Package Installation Errors**
**Solution:** Use `requirements-deploy.txt` with simplified dependencies

### **Issue 2: Memory Limit Exceeded**
**Solution:** Mock implementations reduce memory usage

### **Issue 3: Database Permissions**
**Solution:** SQLite works in most environments, fallback to in-memory storage

### **Issue 4: Missing Dependencies**
**Solution:** Graceful fallbacks with warning messages

## 🎯 Features Available in Deployment

### **✅ Core Features:**
- Integrated nexus simulation
- Multi-objective optimization
- Sensitivity analysis
- Field data entry
- Database logging
- Interactive visualizations

### **⚠️ Limited Features:**
- GIS integration (requires heavy dependencies)
- ML surrogates (tensorflow optional)
- Advanced climate downscaling
- Real-time API connections
- PDF report generation

### **🔄 Mock Data:**
- When heavy packages aren't available
- Maintains app functionality
- Shows expected behavior

## 📊 Performance Optimization

### **Memory Usage:**
- Reduced from ~2GB to ~500MB
- Mock implementations for heavy modules
- Efficient data structures

### **Startup Time:**
- Fast loading with core dependencies
- Lazy loading of optional modules
- Graceful degradation

## 🔐 Security Considerations

### **Data Protection:**
- Local SQLite database
- No external API calls by default
- User data isolation

### **Access Control:**
- Basic login system
- Session management
- Data privacy

## 📈 Scaling Options

### **For Production Use:**
1. **Add PostgreSQL** for database
2. **Implement user authentication**
3. **Add caching layer**
4. **Use external APIs**
5. **Enable full feature set**

### **For Research/Demo:**
1. **Current deployment version** is sufficient
2. **SQLite** handles research data well
3. **Mock data** demonstrates capabilities
4. **Core functionality** meets research needs

## 🎉 Success Metrics

### **Deployment Success Indicators:**
- ✅ App loads without errors
- ✅ Simulation runs successfully
- ✅ Visualizations display correctly
- ✅ Database operations work
- ✅ Export functions available

### **User Experience:**
- Fast loading (< 10 seconds)
- Responsive interface
- Clear error messages
- Intuitive navigation
- Helpful guidance

## 🆘 Troubleshooting

### **If Deployment Fails:**
1. Check requirements.txt format
2. Verify Python version compatibility
3. Check for missing imports
4. Review platform-specific requirements
5. Check memory limits

### **If App Crashes:**
1. Check Streamlit logs
2. Verify database permissions
3. Check memory usage
4. Review error messages
5. Test individual components

## 📞 Support

### **For Deployment Issues:**
- Check this guide first
- Review platform documentation
- Test with minimal app
- Check community forums

### **For Feature Requests:**
- Document requirements
- Prioritize core functionality
- Consider resource constraints
- Plan incremental improvements
