# NeuraCity Database Setup Guide

Complete step-by-step guide to set up your NeuraCity database from scratch.

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] Internet connection
- [ ] Web browser
- [ ] Text editor

## Step-by-Step Setup

### Step 1: Create Supabase Project (5 minutes)

1. **Sign up for Supabase**
   - Go to [supabase.com](https://supabase.com)
   - Click "Start your project"
   - Sign up with GitHub, Google, or email

2. **Create a new project**
   - Click "New Project"
   - Choose your organization
   - Fill in project details:
     - **Name**: `neuracity` (or any name you prefer)
     - **Database Password**: Generate a strong password (save it!)
     - **Region**: Choose closest to you
   - Click "Create new project"
   - Wait ~2 minutes for provisioning

3. **Get your API credentials**
   - Once project is ready, go to **Settings** → **API**
   - Copy and save these two values:
     - **Project URL** (e.g., `https://xxxxxxxxxxxxx.supabase.co`)
     - **anon public** key (long string starting with `eyJ...`)

### Step 2: Configure Environment (2 minutes)

1. **Navigate to database directory**
   ```bash
   cd C:\Users\mianm\Downloads\NeuraCity\database
   ```

2. **Create .env file**
   ```bash
   # Windows Command Prompt
   copy .env.example .env

   # Windows PowerShell
   Copy-Item .env.example .env

   # Git Bash / WSL
   cp .env.example .env
   ```

3. **Edit .env file**
   - Open `.env` in any text editor (Notepad, VS Code, etc.)
   - Replace the placeholder values:
     ```env
     SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
     SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
     ```
   - Save the file

### Step 3: Install Python Dependencies (1 minute)

```bash
# Make sure you're in the database directory
cd C:\Users\mianm\Downloads\NeuraCity\database

# Install required packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed supabase-2.3.0 Faker-22.0.0 python-dotenv-1.0.0 ...
```

### Step 4: Create Database Schema (5 minutes)

Since Supabase Python client doesn't support raw SQL execution, we'll use the SQL Editor:

1. **Open Supabase SQL Editor**
   - Go to your Supabase project dashboard
   - Click **SQL Editor** in the left sidebar
   - Click **New query**

2. **Run schema.sql**
   - Open `C:\Users\mianm\Downloads\NeuraCity\database\schema.sql` in a text editor
   - Copy the **entire contents** (Ctrl+A, Ctrl+C)
   - Paste into the Supabase SQL Editor
   - Click **Run** (or press Ctrl+Enter)

3. **Verify success**
   - You should see messages in the output panel
   - Look for "NeuraCity Database Schema Created Successfully"
   - Check **Table Editor** (left sidebar) - you should see 7 tables:
     - contractors
     - emergency_queue
     - issues
     - mood_areas
     - noise_segments
     - traffic_segments
     - work_orders

### Step 5: Load Seed Data (5 minutes)

Load each seed file in order:

#### 5.1 Load Contractors

- In Supabase SQL Editor, click **New query**
- Open `seeds/001_contractors.sql`
- Copy all contents
- Paste into SQL Editor
- Click **Run**
- Verify: Should see "Contractors seeded successfully" with count

#### 5.2 Load City Areas

- Click **New query**
- Open `seeds/002_city_areas.sql`
- Copy all contents
- Paste and **Run**
- Verify: Should see "City areas seeded successfully"

#### 5.3 Load Initial Data

- Click **New query**
- Open `seeds/003_initial_data.sql`
- Copy all contents
- Paste and **Run**
- Verify: Should see counts for traffic, noise, issues, work orders, emergency queue

### Step 6: Generate Synthetic Data (5-10 minutes)

Now use the Python data generator to create realistic time-series data:

```bash
# Make sure you're in the database directory
cd C:\Users\mianm\Downloads\NeuraCity\database

# Generate 7 days of data
python seeds/generate_data.py --days=7
```

**What happens:**
- Generates ~5,000+ mood data points
- Generates ~13,000+ traffic records
- Generates ~13,000+ noise measurements
- Generates 50 sample infrastructure issues
- Progress bars show real-time updates

**Expected output:**
```
============================================================
NeuraCity Synthetic Data Generator
============================================================
✓ Connected to Supabase

📝 Generating mood posts for 7 days (100 posts/day)...
  ✓ Inserted 100 mood data points (Total: 100)
  ✓ Inserted 100 mood data points (Total: 200)
  ...

🚗 Generating traffic data for 7 days (96 intervals/day)...
  ✓ Inserted 100 traffic records (Total: 100)
  ...

🔊 Generating noise data for 7 days (96 intervals/day)...
  ✓ Inserted 100 noise records (Total: 100)
  ...

🚧 Generating 50 sample issues...
✓ Generated 50 sample issues

============================================================
✓ Data generation complete!
============================================================
Mood data points:    700
Traffic records:     13,104
Noise records:       13,104
Sample issues:       50
Total records:       26,958
============================================================
```

### Step 7: Verify Setup (1 minute)

```bash
python verify.py
```

**Expected output:**
```
============================================================
NeuraCity Database Verification
============================================================
✓ Configuration loaded successfully
✓ Connected to Supabase

============================================================
Database Verification
============================================================

📋 Checking table: issues
   Description: Citizen-reported infrastructure issues
   ✓ Table exists
   ✓ All required columns present
   📊 Record count: 50+

📋 Checking table: mood_areas
   Description: Sentiment analysis by area
   ✓ Table exists
   📊 Record count: 700+

... (for all 7 tables)

============================================================
Checking Views
============================================================
   ✓ active_issues_summary - accessible
   ✓ pending_work_orders_details - accessible
   ✓ emergency_queue_details - accessible

============================================================
Data Quality Checks
============================================================
   ✓ All issues have valid coordinates
   ✓ All work orders reference valid issues
   ✓ All contractors have valid email formats

============================================================
Verification Summary
============================================================

📊 Tables: 7/7 exist
📐 Structure: 7/7 valid
📈 Total records: 27,000+
👁️  Views: ✓ All accessible
✅ Data quality: ✓ All checks passed

============================================================
✓ Database is fully set up and ready to use!
============================================================
```

## Troubleshooting

### Problem: "SUPABASE_URL is not set"

**Solution:**
1. Make sure you created `.env` file (not `.env.example`)
2. Check that `.env` contains your actual Supabase URL and key
3. No quotes needed around values in `.env`

### Problem: "Failed to connect to Supabase"

**Solution:**
1. Check your internet connection
2. Verify SUPABASE_URL starts with `https://`
3. Verify you copied the **anon/public key**, not the service role key
4. Try visiting your Supabase project URL in a browser

### Problem: "Table does not exist"

**Solution:**
1. Make sure you ran `schema.sql` in Supabase SQL Editor
2. Check for errors in the SQL Editor output
3. Verify tables exist in **Table Editor** sidebar

### Problem: "pip: command not found"

**Solution:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. Make sure "Add Python to PATH" is checked during installation
3. Restart your terminal/command prompt
4. Try `python -m pip install -r requirements.txt`

### Problem: Data generator runs very slowly

**Solution:**
This is normal for large datasets. Options:
1. **Reduce data volume:**
   ```bash
   python seeds/generate_data.py --days=1 --issues=10
   ```
2. **Skip certain data types:**
   ```bash
   python seeds/generate_data.py --skip-traffic --skip-noise
   ```
3. **Be patient** - 7 days of data takes ~5-10 minutes

### Problem: "ModuleNotFoundError: No module named 'supabase'"

**Solution:**
1. Make sure you ran `pip install -r requirements.txt`
2. Check you're using the correct Python:
   ```bash
   python --version  # Should be 3.8+
   pip --version     # Should match your Python version
   ```
3. Try: `python -m pip install supabase faker python-dotenv`

## Quick Commands Reference

```bash
# Navigate to database directory
cd C:\Users\mianm\Downloads\NeuraCity\database

# Install dependencies
pip install -r requirements.txt

# Generate data (full)
python seeds/generate_data.py --days=7

# Generate data (quick test)
python seeds/generate_data.py --days=1 --issues=10

# Verify database
python verify.py

# Verify with detailed checks
python verify.py --detailed

# Reset database (DANGER: deletes all data!)
python reset.py

# View help for any script
python seeds/generate_data.py --help
python verify.py --help
python reset.py --help
```

## What's Next?

After successful setup, you can:

1. **Explore the data** in Supabase Table Editor
2. **Run sample queries** from `README.md`
3. **Start building the backend** (FastAPI)
4. **Connect the frontend** (React)

## Additional Resources

- **Database Documentation**: `README.md` - Complete API reference
- **Schema Details**: `SCHEMA.md` - Visual schema documentation
- **Supabase Docs**: https://supabase.com/docs
- **Python Supabase Client**: https://github.com/supabase/supabase-py

## Support

If you encounter issues not covered here:

1. Check `README.md` for detailed documentation
2. Review `SCHEMA.md` for schema details
3. Check Supabase dashboard for error messages
4. Review Python script output for specific errors

## Success Criteria

Your database is ready when:

- ✓ All 7 tables exist in Supabase
- ✓ All 3 views are accessible
- ✓ Contractors table has ~18 contractors
- ✓ Mood, traffic, and noise data is present
- ✓ Sample issues exist
- ✓ `python verify.py` shows all checks passed

**Congratulations! Your NeuraCity database is ready for development!**
