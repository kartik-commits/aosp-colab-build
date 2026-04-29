# AOSP Colab Build System 

> **Complete system for building PixelOS (AOSP) on Google Colab Pro** with persistent caching, resumable builds, and 1-hour daily sessions.

## What This Is

A production-ready solution for building custom Android ROM (PixelOS) on Google Colab Pro within daily time constraints. Perfect for:
- Developers with limited build server access
- Testing AOSP builds without local hardware
- Daily incremental builds that resume automatically
- Multiple device variants with shared ccache

## Key Features

- **Resumable Builds** - Pick up where you left off each day
- **Persistent Caching** - ccache on Google Drive speeds up rebuilds 2-3x
- **Automatic Uploads** - Compressed /out automatically sent to Drive
- **Session Tracking** - Build state persisted across sessions
- **Full Documentation** - Step-by-step guides + troubleshooting
- **Multi-Device** - Build different targets with same cache
- **Error Handling** - Comprehensive logging and recovery

## Specs

**Colab Pro Hardware:**
- 47GB RAM
- 24 CPU cores
- 200GB storage
- 1 hour daily uptime

**Build Times:**
- First build: ~100 min (download + build)
- Subsequent: ~70 min (cache-assisted)

## Quick Start

### 1. Download
- Get `AOSP_Build_Colab.ipynb` from this repo

### 2. Open in Colab
```
https://colab.research.google.com
→ File → Upload notebook
→ Select AOSP_Build_Colab.ipynb
```

### 3. Configure (Cell 11)
```python
LUNCH_TARGET = "cheetah-userdebug" # Your device
JOBS = 20 # CPU parallelization
DRIVE_PATH = "/root/gdrive/MyDrive/AOSP"
```

### 4. Run
Execute cells 1-7 in order. First build takes ~100 min.

### 5. Result
Find your ROM in Google Drive: `out_[timestamp].tar.gz`

## What's Included

| File | Purpose |
|------|---------|
| **AOSP_Build_Colab.ipynb** | Main notebook (8 cells) |
| **START_HERE.txt** | Quick overview |
| **SETUP.md** | Step-by-step guide |
| **README.md** | Configuration reference |
| **TROUBLESHOOTING.md** | Problem solving |
| **INDEX.md** | Complete documentation |
| aosp_build_manager.py | Build orchestration |
| build_orchestrator.py | Advanced checkpointing |

## How It Works

```
Day 1 (First Build):
 Mount Google Drive (5 min)
 Install dependencies (5 min)
 Sync AOSP source (30 min) ← Full download
 Build ROM (50 min) ← Main compilation
 Upload to Drive (15 min)
TOTAL: ~105 min

Day 2+ (Subsequent Builds):
 Mount & Setup (5 min)
 Restore ccache (2 min) ← Faster!
 Build ROM (50 min) ← Benefits from cache
 Upload to Drive (15 min)
TOTAL: ~70 min
```

## Storage Strategy

**On Google Drive:**
```
MyDrive/AOSP/
 source/ (100-150GB, synced once)
 ccache.tar.gz (15GB, backed up each session)
 out_*.tar.gz (30-50GB, compressed ROMs)
 build_state.json (metadata)
```

**On Colab (ephemeral):**
- Working directory (~50GB temp files)
- Cleared each session

## Device Targets

Build for any Pixel device supported by PixelOS:

```python
LUNCH_TARGET = "cheetah-userdebug" # Pixel 7 Pro
LUNCH_TARGET = "bluejay-userdebug" # Pixel 6 Pro
LUNCH_TARGET = "redfin-userdebug" # Pixel 5a
LUNCH_TARGET = "oriole-userdebug" # Pixel 6
# ... and more
```

## Documentation

Start here based on your needs:

| Goal | Read |
|------|------|
| Quick overview | START_HERE.txt |
| First-time setup | SETUP.md |
| Configuration | README.md |
| Having issues? | TROUBLESHOOTING.md |
| Everything | INDEX.md |

## ⏱ Build Timeline

- **Cell 1-3**: Setup & dependencies → 5 min
- **Cell 4-6**: Build manager initialization → 2 min 
- **Cell 7-9**: Repo sync → 30 min (first build only)
- **Cell 10-11**: Build → 50 min (main work)
- **Cell 12-13**: Upload & cleanup → 15 min

## Pro Tips

1. **Keep ccache.tar.gz** on Drive - don't delete it!
 → 2-3x faster rebuilds with cache

2. **Start with JOBS=20** for Colab Pro
 → Reduce to 16 if running low on memory

3. **Monitor space** between cells
 → Check storage with `df -h /root`

4. **Build multiple devices** with same cache
 → Pixel 7 Pro on Day 1 → Pixel 6 Pro on Day 2

5. **Save build.log**
 → Contains error details for debugging

## Features

- No hardcoded credentials (standard Colab Drive auth)
- All sources from official PixelOS/AOSP repos
- Secure build process
- Open source code

## Build System

- **AOSP Version**: Android 16 (PixelOS sixteen-qpr2)
- **Build System**: Soong (Android 16)
- **Source**: https://github.com/PixelOS-AOSP/android_manifest.git

## Requirements

- Google Colab Pro account (recommended)
- 200GB free space on Google Drive
- Stable internet connection
- 1 hour/day Colab uptime (minimum)

## Advanced Usage

### Build Different Targets
```python
# Day 1: Pixel 7 Pro
LUNCH_TARGET = "cheetah-userdebug"

# Day 2: Pixel 6 Pro (reuse cache!)
LUNCH_TARGET = "bluejay-userdebug"
```

### Optimize for Speed
```python
# Colab Pro: 24 cores
JOBS = 24 # Max parallelization

# Colab Free: 8 cores, less RAM
JOBS = 8 # Lower parallelization
```

### Clean Rebuild
```python
# If cache is stale
!rm -rf /root/aosp/.ccache

# Then re-run build (cell 11)
```

## Troubleshooting

**Build fails with "out of memory"?**
- Reduce JOBS from 20 to 16 in cell 11

**Repo sync hangs?**
- Press Ctrl+C and re-run cell 9
- Repo will resume from where it stopped

**Can't extract ROM?**
```bash
# After downloading out_*.tar.gz
tar -xzf out_*.tar.gz

# Find ROM
ls -lh out/target/product/cheetah/*.zip
```

See `TROUBLESHOOTING.md` for comprehensive debugging guide.

## Support

- **AOSP Docs**: https://source.android.com/docs/setup/build
- **PixelOS**: https://github.com/PixelOS-AOSP
- **Issues**: Check TROUBLESHOOTING.md first

## Commit Info

```
Signed-off-by: kartik-commits <lashkare@duck.com>
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## License

This is a guide/tool collection. AOSP source follows Google's license.

**Ready to build?** Download `AOSP_Build_Colab.ipynb` and start! 

**Questions?** See the documentation files in this repo.
