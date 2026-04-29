#!/usr/bin/env python3
"""
AOSP Build Manager for Colab
Handles Drive sync, caching, and build orchestration
"""

import os
import json
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class AOSPBuildManager:
    def __init__(self, drive_path: str, work_path: str = "/root/aosp"):
        self.drive_path = Path(drive_path)
        self.work_path = Path(work_path)
        self.state_file = self.drive_path / "build_state.json"
        self.source_path = self.work_path / "source"
        self.out_path = self.work_path / "out"
        self.ccache_path = self.work_path / ".ccache"
        
    def load_state(self) -> Dict:
        """Load build state from previous session"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "last_build": None,
            "last_sync": None,
            "session_count": 0,
            "build_status": "init",
            "ccache_hits": 0,
        }
    
    def save_state(self, state: Dict):
        """Save build state for next session"""
        state["last_sync"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"✓ State saved to {self.state_file}")
    
    def setup_directories(self):
        """Create and verify directory structure"""
        self.source_path.mkdir(parents=True, exist_ok=True)
        self.out_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directories ready: {self.work_path}")
    
    def check_space(self) -> Dict:
        """Check available storage"""
        stat = shutil.disk_usage(self.work_path)
        total_gb = stat.total / (1024**3)
        free_gb = stat.free / (1024**3)
        used_gb = stat.used / (1024**3)
        
        info = {
            "total_gb": round(total_gb, 1),
            "used_gb": round(used_gb, 1),
            "free_gb": round(free_gb, 1),
            "usage_percent": round((used_gb / total_gb) * 100, 1)
        }
        
        print(f"""
Storage Status:
  Total: {info['total_gb']}GB
  Used:  {info['used_gb']}GB
  Free:  {info['free_gb']}GB ({info['usage_percent']}%)
        """)
        return info
    
    def download_from_drive(self, filename: str, destination: Path):
        """Download file from Drive"""
        source = self.drive_path / filename
        if not source.exists():
            print(f"⚠ {filename} not found on Drive")
            return False
        
        print(f"⬇ Downloading {filename}...")
        shutil.copy2(source, destination)
        size_gb = destination.stat().st_size / (1024**3)
        print(f"✓ Downloaded {filename} ({size_gb:.1f}GB)")
        return True
    
    def upload_to_drive(self, source: Path, filename: str):
        """Upload file to Drive"""
        if not source.exists():
            print(f"⚠ {source} not found")
            return False
        
        dest = self.drive_path / filename
        print(f"⬆ Uploading {filename}...")
        
        if source.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
        else:
            shutil.copy2(source, dest)
        
        size_gb = self._get_size_gb(dest)
        print(f"✓ Uploaded to Drive ({size_gb:.1f}GB)")
        return True
    
    def restore_ccache(self) -> bool:
        """Restore ccache from Drive"""
        ccache_tar = self.drive_path / "ccache.tar.gz"
        if not ccache_tar.exists():
            print("ℹ No ccache on Drive (first build)")
            return False
        
        print("⬇ Restoring ccache...")
        subprocess.run(
            f"cd {self.work_path} && tar -xzf {ccache_tar}",
            shell=True,
            check=True
        )
        size_gb = self._get_size_gb(self.ccache_path)
        print(f"✓ Restored ccache ({size_gb:.1f}GB)")
        return True
    
    def backup_ccache(self) -> bool:
        """Compress and backup ccache to Drive"""
        if not self.ccache_path.exists():
            print("ℹ No ccache to backup")
            return False
        
        print("⬆ Backing up ccache...")
        ccache_tar = self.drive_path / "ccache.tar.gz"
        subprocess.run(
            f"cd {self.work_path} && tar -czf {ccache_tar} .ccache/",
            shell=True,
            check=True
        )
        size_gb = ccache_tar.stat().st_size / (1024**3)
        print(f"✓ ccache backed up ({size_gb:.1f}GB)")
        return True
    
    def repo_init(self, manifest_url: str, branch: str) -> bool:
        """Initialize repo with manifest"""
        os.chdir(self.source_path)
        print(f"📦 Initializing repo from {manifest_url}...")
        
        cmd = f"repo init -u {manifest_url} -b {branch} --git-lfs"
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode != 0:
            print("✗ Repo init failed")
            return False
        
        print("✓ Repo initialized")
        return True
    
    def repo_sync(self, jobs: int = 8) -> bool:
        """Sync repo sources"""
        os.chdir(self.source_path)
        print(f"📥 Syncing repo ({jobs} jobs)...")
        
        cmd = f"repo sync -j {jobs} --current-branch"
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode != 0:
            print("✗ Repo sync failed")
            return False
        
        size_gb = self._get_size_gb(self.source_path)
        print(f"✓ Repo synced ({size_gb:.1f}GB)")
        return True
    
    def build_aosp(self, lunch_target: str, jobs: Optional[int] = None) -> bool:
        """Build AOSP"""
        if jobs is None:
            jobs = os.cpu_count() or 8
        
        os.chdir(self.source_path)
        print(f"🔨 Building {lunch_target} ({jobs} jobs)...")
        
        # Setup environment
        subprocess.run("source build/envsetup.sh", shell=True)
        
        # Lunch and build
        cmd = f"""
        set -e
        source build/envsetup.sh > /dev/null
        lunch {lunch_target}
        export USE_CCACHE=1
        export CCACHE_DIR=/root/aosp/.ccache
        make -j {jobs} 2>&1 | tee /root/aosp/build.log
        """
        
        result = subprocess.run(cmd, shell=True, executable="/bin/bash")
        
        if result.returncode != 0:
            print("✗ Build failed (check build.log)")
            return False
        
        print("✓ Build completed successfully!")
        return True
    
    def compress_out(self) -> Optional[Path]:
        """Compress /out folder"""
        if not self.out_path.exists():
            print("⚠ No /out folder found")
            return None
        
        size_gb = self._get_size_gb(self.out_path)
        print(f"📦 Compressing /out ({size_gb:.1f}GB)...")
        
        tar_path = self.drive_path / "out.tar.gz"
        cmd = f"tar -czf {tar_path} -C {self.work_path} out/ 2>&1 | tail -1"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        compressed_size = tar_path.stat().st_size / (1024**3)
        ratio = (compressed_size / size_gb) * 100
        
        print(f"✓ Compressed to {compressed_size:.1f}GB ({ratio:.0f}% ratio)")
        return tar_path
    
    def print_summary(self, state: Dict):
        """Print build session summary"""
        print(f"""
╔════════════════════════════════════════╗
║        Build Session Summary            ║
╚════════════════════════════════════════╝
Session: #{state.get('session_count', 0)}
Status: {state.get('build_status', 'unknown')}
Source: {self._get_size_gb(self.source_path):.1f}GB
Output: {self._get_size_gb(self.out_path):.1f}GB
Cache: {self._get_size_gb(self.ccache_path):.1f}GB
        """)
    
    @staticmethod
    def _get_size_gb(path: Path) -> float:
        """Get directory/file size in GB"""
        if not path.exists():
            return 0
        
        if path.is_file():
            return path.stat().st_size / (1024**3)
        
        total = sum(
            f.stat().st_size
            for f in path.rglob("*")
            if f.is_file()
        )
        return total / (1024**3)


if __name__ == "__main__":
    # Example usage
    manager = AOSPBuildManager("/root/gdrive/MyDrive/AOSP")
    manager.setup_directories()
    manager.check_space()
    state = manager.load_state()
    print(json.dumps(state, indent=2))
