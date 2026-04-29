# AOSP Build on Colab - Setup Instructions

## Step 1: Download Files

All files are in: `/home/kartiks-fedora/.copilot/session-state/332b1724-1d14-4b47-8b14-505b93c2d731/files/`

Download these 4 files:
- **AOSP_Build_Colab.ipynb** - Main notebook (use this!)
- **aosp_build_manager.py** - Helper module (copy into notebook)
- **build_orchestrator.py** - Advanced checkpointing (optional)
- **README.md** - Reference guide

## Step 2: Open Notebook in Colab

1. Go to https://colab.research.google.com/
2. Click **File → Upload notebook**
3. Select `AOSP_Build_Colab.ipynb`
4. Choose **Colab Pro** runtime (if you have it)

## Step 3: Configure Before First Run

Open the notebook and update these cells:

### Cell 11: Lunch Target
```python
LUNCH_TARGET = "cheetah-userdebug" # ← Change to your device
```

Common targets:
- `cheetah-userdebug` - Pixel 7 Pro
- `bluejay-userdebug` - Pixel 6 Pro
- `redfin-userdebug` - Pixel 5a
- `oriole-userdebug` - Pixel 6

### Cell 11: Job Count
```python
JOBS = 20 # ← Adjust based on available memory
```

Recommended:
- 20 jobs (Colab Pro default, 47GB RAM)
- 16 jobs (if running low on memory)
- 12 jobs (if build crashes with OOM)

### Cell 7: Drive Path (Optional)
```python
DRIVE_PATH = "/root/gdrive/MyDrive/AOSP" # ← Custom location
```

## Step 4: Run First Build

Execute cells in order:

```
Cells 1-3 → Mount Drive, install dependencies (3 min)
Cells 4-6 → Setup build manager (2 min)
Cells 7-9 → Initialize & sync repo (30 min) ⏱
Cells 10-11 → BUILD! (50 min) 
Cells 12-13 → Upload to Drive (15 min)
```

**Total: ~90 minutes** (first build, includes full source sync)

## Step 5: Resume Next Session

Next day, just:
1. Run cells 1-3 (setup)
2. **Skip to cell 10** - ccache auto-restores
3. Build runs in ~50 min

## What Happens Each Session

### Session 1 (Day 1)
- Download full AOSP source (~100-150GB) → takes 30 min
- Build ROM → 50 min
- Backup ccache + upload /out to Drive → 15 min
- **Result**: ccache.tar.gz + out_*.tar.gz on Drive

### Session 2+ (Day 2, 3, etc.)
- Restore ccache from Drive → 2 min
- Source already cached locally
- Build resumes from same checkpoint
- Upload new /out
- **Result**: Faster builds (~50 min vs 90 min)

## Drive Organization After First Build

```
MyDrive/
 AOSP/
 build_state.json # Metadata (session count, status)
 ccache.tar.gz # Compiler cache (~15GB)
 out_1704067200.tar.gz # First build output (compressed)
 out_1704153600.tar.gz # Second build output
 source/ # (Optional) AOSP source symlink
```

## Quick Reference

| Task | Cell | Time |
|------|------|------|
| Mount & Setup | 1-6 | 5 min |
| First sync | 7-9 | 30 min |
| Build | 10-11 | 50 min |
| Upload | 12-13 | 15 min |
| **Total (first)** | **All** | **~90 min** |
| **Total (resume)** | **Skip 7-9** | **~60 min** |

## Authorization

When you run cell 1, Colab will ask for Google Drive authorization:
1. Click the auth link
2. Select your Google account
3. Grant Colab permission
4. Copy the code back to Colab

This only needs to happen once per Colab session.

## Success Indicators

- Cell 1: " Google Drive mounted"
- Cell 3: " Dependencies installed"
- Cell 9: " Repo synced"
- Cell 11: Build completes with " BUILD SUCCESSFUL!"
- Cell 13: " Uploaded! out_*.tar.gz"

## Common Issues

### "ModuleNotFoundError: No module named 'aosp_build_manager'"
→ Run cell 8 first (it creates the module inline)

### Build fails with "out of memory"
→ Reduce JOBS from 20 to 16 in cell 11
→ Free space: run cell 14 (cleanup)

### "No permission to access Drive"
→ Re-run cell 1 and re-authorize

### "repo sync" gets stuck
→ Restart the cell - it will resume
→ Try `-j 4` if hitting rate limits (edit cell 9)

## Advanced: Build from Command Line

If you prefer terminal instead of notebook cells:

```bash
# Connect to Colab via SSH (optional)
cd /root/aosp/source
source build/envsetup.sh
lunch cheetah-userdebug
make -j20
```

But the notebook approach is recommended for easy resumption.

## Learn More

- PixelOS: https://github.com/PixelOS-AOSP
- AOSP Build Guide: https://source.android.com/docs/setup/build/initializing
- Colab Pro: https://colab.research.google.com/

## Pro Tips

1. **Parallel builds**: Colab Pro has 24 cores, using 20 is safe
2. **ccache is gold**: Saves 30 min on rebuilds - don't delete!
3. **Multiple ROMs**: Build different targets (e.g., cheetah + redfin) - share same ccache
4. **Monitor storage**: Check cell 7 output to watch space usage
5. **Build logs**: Always saved to `/root/aosp/build.log` if something fails

**Ready?** Download the notebook and start building! 
