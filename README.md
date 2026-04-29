# AOSP Colab Build - Quick Start Guide

## What's Included

1. **AOSP_Build_Colab.ipynb** - Main notebook with 8 sections
2. **aosp_build_manager.py** - Python utility for build orchestration

## First Build (Fresh Session)

1. Open the notebook in Colab
2. Run cells in order:
 - **Cell 1-3**: Mount Drive, install dependencies
 - **Cell 4-6**: Initialize build manager, restore cache if exists
 - **Cell 7-9**: Init repo + sync source code (~100-150GB, ~30 min)
 - **Cell 10-11**: Configure build environment + BUILD (40-50 min)
 - **Cell 12-13**: Backup ccache + upload /out to Drive (10-15 min)

**Total time: ~90 min** (first build with full sync)

## Resume Build (Next Sessions)

1. Run cells 1-3 again (setup)
2. **Jump directly to cell 10** - ccache auto-restores, source is cached
3. Build resumes in ~50 min

**Total time: ~60 min** (resumable build)

## Key Configurations

### Modify Lunch Target
```python
LUNCH_TARGET = "cheetah-userdebug" # Change to your device
```

Available targets for PixelOS (check your branch):
- `cheetah-userdebug` - Pixel 7 Pro
- `bluejay-userdebug` - Pixel 6 Pro
- `redfin-userdebug` - Pixel 5a
- `oriole-userdebug` - Pixel 6
- See: `lunch` in source for full list

### Adjust Parallelization
```python
JOBS = 20 # Change based on CPU cores (Colab Pro = 24 cores)
```

### Change Drive Storage Path
```python
DRIVE_PATH = "/root/gdrive/MyDrive/AOSP" # Your preferred location
```

## Storage Breakdown

| Component | Size | Storage |
|-----------|------|---------|
| Source Code | 100-150GB | Drive (persistent) |
| ccache | 10-20GB | Drive (persistent) |
| /out (builds) | 30-50GB | Uploaded to Drive |
| Ephemeral work | ~50GB | Colab (temp) |
| **Total needed** | **200GB** | Fits in Colab Pro |

## Drive Organization

```
MyDrive/AOSP/
 ccache.tar.gz # Restored each session
 build_state.json # Metadata (session count, status)
 out_1704067200.tar.gz # Build output (compressed)
 out_1704153600.tar.gz # Previous build
 source/ # AOSP source (optional, can be symlink)
```

## Environment Details

**Colab Pro Hardware:**
- 24 CPU cores
- 47GB RAM
- 200GB storage
- NVIDIA T4 GPU (not used for AOSP)

**Build Configuration:**
- USE_CCACHE=1 (compiler cache enabled)
- CCACHE_MAXSIZE=50G
- Parallel jobs: 20 (adjust if out of memory)

## Troubleshooting

### Build fails with "out of memory"
→ Reduce JOBS from 20 to 16 or 12

### Sync fails / Repo stuck
→ Restart cell, repo will resume
→ Try `-j 4` if hitting rate limits

### Drive quota warning
→ Delete old `out_*.tar.gz` files to free space
→ ccache.tar.gz is essential, keep it

### Can't mount Drive in Colab
→ Re-run cell 1, authorize with your Google account

## Manual Steps for Extracting ROM

If you want to extract the ROM locally:

```bash
# On your machine, download out_*.tar.gz from Drive
tar -xzf out_*.tar.gz

# Find ROM image
ls -lh out/target/product/cheetah/*.zip
# Usually: cheetah-userdebug-[timestamp].zip
```

## Useful Commands (in notebook cells)

```python
# Check available lunch targets
!source build/envsetup.sh > /dev/null && lunch

# View ccache stats
!ccache -s

# Force rebuild (clear ccache)
!rm -rf /root/aosp/.ccache

# List files in /out
!ls -lh /root/aosp/out/target/product/*/

# Check build errors
!grep -i "error\|failed" /root/aosp/build.log | head -20
```

## How It Works

1. **Persistent Cache (Drive)**
 - AOSP source synced once, stored on Drive
 - ccache (compiler cache) uploaded after each build
 - Subsequent builds reuse cache → 2-3x faster

2. **Resume Logic**
 - build_state.json tracks session count + status
 - Each session increments counter
 - ccache auto-restored if previous build succeeded

3. **Smart Upload**
 - /out compressed with tar+gzip (~60% ratio)
 - Timestamp in filename for multiple builds
 - Old builds can be deleted to free space

## PixelOS Build Details

- **Branch**: sixteen-qpr2 (Android 16)
- **Manifest**: https://github.com/PixelOS-AOSP/android_manifest.git
- **Build system**: Android 16 build system (Soong)
- **Git LFS**: Required for large files (auto-installed)

## Important Notes

- **1 hour per day limit**: Build will pause if time runs out
 - Save state automatically via build_state.json
 - Next session resumes from where you left
 
- **Storage limits**: 200GB total in Colab
 - Don't keep multiple /out folders extracted locally
 - Always compress before uploading

- **Network**: Colab upload to Drive is fast
 - 50GB → ~10-15 min (good bandwidth)

**Questions?** Check Colab notebook cells for inline comments and error handling.
