# TOKUMA 3-in-1 Deployment Guide

## Quick Deploy to Streamlit Cloud (Recommended)

### Step 1: Prepare GitHub Repository
✅ Already done! Your code is pushed to `https://github.com/Caratoko/Allaallaa.git`

### Step 2: Create PostgreSQL Database

Choose one of these free/affordable options:

**Option A: ElephantSQL (Free tier 20 MB)**
1. Go to https://www.elephantsql.com/
2. Sign up and create a new instance (free tier available)
3. Copy credentials (Host, Database, User, Password)

**Option B: Neon (Free tier 3 GB)**
1. Go to https://neon.tech/
2. Create a new project
3. Copy the connection string

**Option C: AWS RDS / Google Cloud SQL**
1. Set up RDS with PostgreSQL
2. Configure security groups to allow inbound on port 5432
3. Copy connection details

**Option D: Local PostgreSQL (for testing)**
```bash
# Install PostgreSQL locally first, then:
createdb tokuma_phd_research
# Connection: localhost, postgres user, default password
```

### Step 3: Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click **"New app"**
4. Select repository: `Caratoko/Allaallaa`
5. Select branch: `pre-sensitivity-analysis` (or your current branch)
6. Set main file path: `app.py`
7. Click **"Deploy"**

### Step 4: Configure Secrets

Once deployed on Streamlit Cloud:

1. Navigate to your app settings (gear icon → **Secrets**)
2. Add these secrets in the format below:

```toml
host = "your-postgres-host.amazonaws.com"
database = "your_database_name"
user = "your_username"
password = "your_password"
port = 5432
```

**Example (ElephantSQL):**
```toml
host = "flora.db.elephantsql.com"
database = "xxxxxxxx"
user = "xxxxxxxx"
password = "your_super_secret_password"
port = 5432
```

5. Click **"Save"** — Streamlit will restart automatically

### Step 5: Test the Deployment

- Open your live app URL (shown in the Streamlit Cloud dashboard)
- Login with any name and institution
- Run the simulation
- Verify that Phase 3, 4, 5 all work
- Check that irrigation schedules and field requests are stored in the database

---

## Local Testing (Before Deployment)

```bash
# Install dependencies
pip install -r requirements.txt

# For local PostgreSQL testing, create ~/.streamlit/secrets.toml:
cat > ~/.streamlit/secrets.toml << 'EOF'
host = "localhost"
database = "tokuma_phd_research"
user = "postgres"
password = "your_local_password"
port = 5432
EOF

# Run locally
streamlit run app.py
```

---

## Post-Deployment Checklist

- [ ] App loads without errors
- [ ] Login screen appears
- [ ] Phase 1: Dashboard shows metrics
- [ ] Phase 2: Optimization, GIS, ML tabs render
- [ ] Phase 3: Irrigation scheduling generates schedules
- [ ] Phase 4: Field communication, SMS, hardware tabs accessible
- [ ] Phase 5: Reports and export download CSV files
- [ ] Database records are persisted (refresh page → data still there)

---

## Troubleshooting

### "PostgreSQL connection failed"
- Check `host`, `database`, `user`, `password` in Streamlit Secrets
- Verify database is running and accessible
- For cloud databases, whitelist Streamlit Cloud IP: `0.0.0.0/0` (temporary for testing)

### "Module not found: psycopg2"
- `pip install psycopg2-binary` locally
- Already in `requirements.txt`, Streamlit Cloud will auto-install

### App is slow / queries timeout
- Increase PostgreSQL instance size
- Consider adding database connection pooling (pgBouncer)
- Add indexes to frequently queried columns

### "Permission denied" on database
- Verify user has CREATE TABLE permissions
- Check password special characters are URL-encoded

---

## Future Enhancements

1. **Add database backups** → Use PostgreSQL automated backups
2. **Scale to multiple users** → Add user authentication with Streamlit Community Cloud authentication
3. **Real SMS integration** → Uncomment Twilio/AfricasTalking keys in `secrets.toml` and implement in Phase 4
4. **Mobile app backend** → Deploy FastAPI server alongside Streamlit (advanced)
5. **Hardware integration** → Connect actual irrigation valves via MQTT/REST (Phase 4)

---

## Support

For issues:
1. Check Streamlit Cloud logs (in dashboard)
2. Run `streamlit run app.py` locally to isolate issues
3. Verify database connectivity with `psql` CLI
4. Check `.streamlit/config.toml` settings
