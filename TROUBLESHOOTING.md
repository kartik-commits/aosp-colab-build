# AOSP Colab Build - Troubleshooting Guide

## Build Fails to Start

### Issue: "ModuleNotFoundError: No module named..."
**Solution:**
- Run cell 8 first (it creates aosp_build_manager inline)
- Or copy `aosp_build_manager.py` content directly into a cell

### Issue: "Permission denied" when mounting Drive
**Solution:**
- Re-run cell 1
- Click auth link and grant permissions
- Make sure you're using the correct Google account

### Issue: "No space left on device"
**Solution:**
1. Check space: `df -h /root`
2. Clear unnecessary files: `rm -rf /root/aosp/out`
3. Reduce JOBS from 20 to 12
4. Use cell 14 to cleanup

## Sync/Network Issues

### Issue: "repo sync" hangs or times out
**Solution:**
- Press `Ctrl+C` to stop
- Re-run the cell - repo will resume
- If rate-limited, edit cell 9: `repo sync -j 4 --current-branch`

### Issue: "git: unable to access repository"
**Solution:**
- Check internet connection (Colab should have it)
- Try again (transient network error)
- Restart runtime: Runtime → Restart runtime

### Issue: Large files fail to download (git-lfs)
**Solution:**
- git-lfs should be auto-installed in cell 3
- Verify: `which git-lfs` (should print path)
- If not: `apt-get install -y git-lfs && git lfs install`

## Build Issues

### Issue: Build fails with "cc1plus: out of memory"
**Symptom:** Error like "virtual memory exhausted" or "Cannot allocate memory"

**Solution:**
1. Reduce JOBS in cell 11 from 20 to 16:
 ```python
 JOBS = 16 # Use fewer parallel jobs
 ```

2. Or increase swap:
 ```python
 !fallocate -l 20G /swapfile
 !chmod 600 /swapfile
 !mkswap /swapfile
 !swapon /swapfile
 ```

3. Clear ccache if still failing:
 ```python
 !rm -rf /root/aosp/.ccache
 ```

### Issue: "make: *** No targets specified"
**Solution:**
- Make sure lunch succeeded in cell 11
- Verify: `echo $TARGET_PRODUCT` should not be empty
- Try again: sometimes transient

### Issue: Build fails with "source is read-only"
**Solution:**
- Check permissions: `ls -ld /root/aosp/source`
- Fix: `chmod -R u+w /root/aosp/source`

### Issue: "undefined reference to..." linker error
**Solution:**
- Full rebuild needed, ccache might be stale
- Clear and rebuild:
 ```python
 !rm -rf /root/aosp/.ccache
 # Re-run cell 11 (build)
 ```

## Upload Issues

### Issue: "out.tar.gz is too large, Drive quota exceeded"
**Solution:**
1. Free space on Drive:
 - Delete old `out_*.tar.gz` files (keep newest 2)
 - Keep `ccache.tar.gz` (essential)

2. Or compress better:
 ```python
 # Instead of tar.gz, try xz compression
 !tar -cJf out.tar.xz -C /root/aosp out/ 2>&1 | tail -1
 ```

3. Or split into parts:
 ```python
 !tar -czf - -C /root/aosp out/ | split -b 40G - out_part_
 # Upload parts individually
 ```

### Issue: Upload hangs or times out
**Solution:**
- Colab → Runtime → Interrupt execution
- Try in a new Colab session
- Or manually upload from local machine after downloading

### Issue: "drive.mount() doesn't find my files"
**Solution:**
1. Verify path exists:
 ```python
 !ls -l /root/gdrive/MyDrive/
 ```

2. Create AOSP folder if missing:
 ```python
 !mkdir -p /root/gdrive/MyDrive/AOSP
 ```

3. Check in Google Drive web:
 - Open https://drive.google.com
 - Verify AOSP folder exists at root level

## State & Checkpoint Issues

### Issue: "build_state.json not found" on resume
**Solution:**
- First build never had state
- This is normal, just build again
- Next session will have state

### Issue: Can't resume build (want to restart from scratch)
**Solution:**
```python
# Delete state to start fresh
!rm -f /root/gdrive/MyDrive/AOSP/build_state.json
!rm -f /root/aosp/checkpoint.json

# Next build will be from scratch
```

### Issue: Build status shows "failed" but I want to retry
**Solution:**
```python
# Clear error state
state['build_status'] = 'in_progress'
state['retry_count'] = 0
manager.save_state(state)

# Re-run cell 11 (build)
```

## Debug Commands

Run these in notebook cells to investigate:

```python
# Check storage
!df -h /root
!du -sh /root/aosp/*

# Check build environment
!source build/envsetup.sh > /dev/null && printenv | grep -i android

# Check ccache stats
!ccache -s

# View build log
!tail -100 /root/aosp/build.log

# List available lunch targets
!cd /root/aosp/source && source build/envsetup.sh > /dev/null && lunch

# Find build errors
!grep -i "error\|failed\|undefined reference" /root/aosp/build.log | head -20

# Check if build succeeded
!ls -lh /root/aosp/out/target/product/cheetah/*.zip 2>/dev/null || echo "ROM not found"
```

## Recovery Procedures

### Stuck build - want to restart
```python
# Kill build process
!pkill -f "make -j"

# Clear /out to save space
!rm -rf /root/aosp/out

# Re-run cell 11
```

### Corrupted source - want fresh sync
```python
# Backup current source (if you want to keep it)
!tar -czf /root/gdrive/MyDrive/AOSP/source_backup.tar.gz -C /root/aosp source/

# Remove source
!rm -rf /root/aosp/source

# Re-run cell 9 (repo sync)
```

### Drive mount not working - restart
```python
from google.colab import drive
drive.flush_and_unmount() # Unmount

# Then run cell 1 again
```

## Performance Tuning

### Build is too slow
1. Increase JOBS (if memory allows):
 ```python
 JOBS = 24 # Use all Colab Pro cores
 ```

2. Check ccache is working:
 ```python
 !ccache -s # Should show high hit rate after second build
 ```

3. Ensure USE_CCACHE is set:
 ```python
 !echo $USE_CCACHE # Should print 1
 ```

### Build is too fast but incomplete
- You might be hitting a cache issue
- Clear ccache and rebuild to ensure correctness

## Still Stuck?

1. **Check build logs:**
 ```python
 !tail -50 /root/aosp/build.log
 ```

2. **Search error online:**
 - Copy error message
 - Search: `"error message" AOSP Android build`

3. **PixelOS GitHub Issues:**
 - https://github.com/PixelOS-AOSP/android_manifest/issues

4. **AOSP Build Docs:**
 - https://source.android.com/docs/setup/build/building

## Pro Tips

- **Always backup ccache** before clearing it (run cell 12)
- **Monitor space** (run cell 7 between cells)
- **Use smaller JOBS if unsure** (16 is safer than 20)
- **Build at off-peak** if possible (fewer network issues)
- **Keep build logs** for debugging future builds
