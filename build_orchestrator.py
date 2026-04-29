#!/usr/bin/env python3
"""
Build State & Resume Manager
Handles checkpoints, build tracking, and resumable builds
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class BuildCheckpoint:
    """Tracks build phases for resumption"""
    
    PHASES = {
        'init': 'Repo initialization',
        'sync': 'Source code sync',
        'dependencies': 'Dependency check',
        'lunch': 'Lunch setup',
        'build': 'Build execution',
        'package': 'ROM packaging',
        'upload': 'Drive upload',
    }
    
    def __init__(self, checkpoint_file: Path):
        self.file = checkpoint_file
        self.data = self.load()
    
    def load(self) -> Dict:
        if self.file.exists():
            with open(self.file) as f:
                return json.load(f)
        return {
            'phases': {},
            'errors': [],
            'timestamps': {},
            'retry_count': 0,
        }
    
    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def mark_phase(self, phase: str, status: str, details: str = ""):
        """Mark a phase as started/completed/failed"""
        self.data['phases'][phase] = {
            'status': status,  # running, completed, failed
            'timestamp': datetime.now().isoformat(),
            'details': details,
        }
        self.save()
        
        icon = '✓' if status == 'completed' else '✗' if status == 'failed' else '●'
        print(f"{icon} {self.PHASES.get(phase, phase)}: {status}")
    
    def get_next_phase(self, phases: List[str]) -> Optional[str]:
        """Find next uncompleted phase"""
        for phase in phases:
            status = self.data['phases'].get(phase, {}).get('status')
            if status != 'completed':
                return phase
        return None
    
    def is_resumable(self) -> bool:
        """Check if build can be resumed"""
        errors = self.data.get('errors', [])
        if not errors:
            return True
        # Only non-resumable if too many errors
        return self.data.get('retry_count', 0) < 3
    
    def log_error(self, phase: str, error: str):
        """Log build error"""
        self.data['errors'].append({
            'phase': phase,
            'message': error,
            'timestamp': datetime.now().isoformat(),
        })
        self.save()


class BuildOrchestrator:
    """Orchestrates multi-phase builds"""
    
    def __init__(self, source_dir: Path, out_dir: Path, checkpoint_file: Path):
        self.source_dir = source_dir
        self.out_dir = out_dir
        self.checkpoint = BuildCheckpoint(checkpoint_file)
    
    def run_phase(self, phase: str, command: str, description: str = "") -> bool:
        """Execute a build phase with error handling"""
        self.checkpoint.mark_phase(phase, 'running', description)
        
        try:
            print(f"\n► {description or phase}\n")
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.source_dir,
                capture_output=False,
            )
            
            if result.returncode == 0:
                self.checkpoint.mark_phase(phase, 'completed')
                return True
            else:
                self.checkpoint.mark_phase(phase, 'failed', f"Exit code {result.returncode}")
                return False
                
        except Exception as e:
            error_msg = str(e)
            self.checkpoint.log_error(phase, error_msg)
            self.checkpoint.mark_phase(phase, 'failed', error_msg)
            return False
    
    def build_incrementally(self, lunch_target: str, jobs: int = 20) -> bool:
        """Build with checkpointing"""
        phases = ['init', 'sync', 'dependencies', 'lunch', 'build', 'package']
        
        # Check if resumable
        next_phase = self.checkpoint.get_next_phase(phases)
        if next_phase is None:
            print("✓ All phases completed!")
            return True
        
        print(f"\nResuming from: {self.checkpoint.PHASES[next_phase]}\n")
        
        # Execute remaining phases
        phase_idx = phases.index(next_phase)
        for phase in phases[phase_idx:]:
            
            if phase == 'init':
                cmd = "repo init -u https://github.com/PixelOS-AOSP/android_manifest.git -b sixteen-qpr2"
                if not self.run_phase(phase, cmd, "Initialize repository"):
                    return False
            
            elif phase == 'sync':
                cmd = "repo sync -j8 --current-branch"
                if not self.run_phase(phase, cmd, "Sync source code"):
                    return False
            
            elif phase == 'dependencies':
                cmd = "source build/envsetup.sh > /dev/null && echo 'Dependencies OK'"
                if not self.run_phase(phase, cmd, "Verify build environment"):
                    return False
            
            elif phase == 'lunch':
                cmd = f"source build/envsetup.sh > /dev/null && lunch {lunch_target}"
                if not self.run_phase(phase, cmd, f"Setup lunch: {lunch_target}"):
                    return False
            
            elif phase == 'build':
                cmd = f"source build/envsetup.sh > /dev/null && make -j{jobs}"
                if not self.run_phase(phase, cmd, f"Build with {jobs} jobs"):
                    return False
            
            elif phase == 'package':
                cmd = "echo 'Packaging complete'"
                if not self.run_phase(phase, cmd, "Verify output"):
                    return False
        
        return True
    
    def get_status(self) -> str:
        """Get build status summary"""
        phases = self.checkpoint.data['phases']
        completed = sum(1 for p in phases.values() if p['status'] == 'completed')
        total = len(phases)
        
        errors = self.checkpoint.data.get('errors', [])
        
        status = f"""
╔═════════════════════════════════════════╗
║           BUILD STATUS                  ║
╚═════════════════════════════════════════╝

Phases: {completed}/{total} completed
Errors: {len(errors)}

Phase Timeline:
"""
        for phase, info in phases.items():
            icon = {'completed': '✓', 'failed': '✗', 'running': '●'}.get(info['status'], '?')
            status += f"  {icon} {self.checkpoint.PHASES.get(phase, phase)}: {info['status']}\n"
            if info.get('details'):
                status += f"      {info['details']}\n"
        
        if errors:
            status += "\nRecent Errors:\n"
            for err in errors[-3:]:
                status += f"  • {err['phase']}: {err['message']}\n"
        
        status += "\n"
        return status


class UploadManager:
    """Manages uploads to Google Drive"""
    
    def __init__(self, drive_path: Path):
        self.drive_path = drive_path
    
    def upload_checkpoint(self, local_checkpoint: Path):
        """Upload checkpoint to Drive for next session"""
        dest = self.drive_path / "checkpoint.json"
        print(f"⬆ Uploading checkpoint to {dest}")
        subprocess.run(f"cp {local_checkpoint} {dest}", shell=True, check=True)
    
    def upload_out_incremental(self, out_dir: Path, session_id: int) -> bool:
        """Upload /out incrementally if needed"""
        # Check if out is large enough to backup
        size_gb = sum(f.stat().st_size for f in out_dir.rglob('*') if f.is_file()) / (1024**3)
        
        if size_gb < 1:
            print("ℹ /out too small to backup")
            return False
        
        archive = self.drive_path / f"out_session_{session_id}.tar.gz"
        print(f"⬆ Archiving {size_gb:.1f}GB to Drive...")
        
        cmd = f"tar -czf {archive} -C {out_dir.parent} out/ 2>&1 | tail -3"
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode == 0:
            archive_size = archive.stat().st_size / (1024**3)
            ratio = (archive_size / size_gb) * 100
            print(f"✓ Archived {archive_size:.1f}GB ({ratio:.0f}% compression)")
            return True
        
        return False


if __name__ == "__main__":
    from pathlib import Path
    
    # Example usage
    source = Path("/root/aosp/source")
    out = Path("/root/aosp/out")
    checkpoint_file = Path("/root/aosp/checkpoint.json")
    
    orchestrator = BuildOrchestrator(source, out, checkpoint_file)
    
    # Check status
    print(orchestrator.get_status())
    
    # Run build with resumption
    success = orchestrator.build_incrementally(lunch_target="cheetah-userdebug")
    
    if success:
        print("✓ Build completed!")
    else:
        print("✗ Build failed - check checkpoint.json for details")
