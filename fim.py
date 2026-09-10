#!/usr/bin/env python3
"""
File Integrity Monitor (FIM)
Hashes files, stores baseline checksums, and detects changes.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class FileIntegrityMonitor:
    """Monitor file integrity using cryptographic hashes."""

    DEFAULT_BASELINE = "baseline.json"
    CHUNK_SIZE = 65536  # 64KB chunks for hashing

    def __init__(self, baseline_path: str = DEFAULT_BASELINE,
                 algorithm: str = "sha256",
                 exclude_patterns: List[str] = None):
        self.baseline_path = Path(baseline_path)
        self.algorithm = algorithm
        self.exclude_patterns = exclude_patterns or [
            ".git", "__pycache__", ".pyc", ".log", ".tmp"
        ]

    # ---------- Hashing ----------
    def _hash_file(self, filepath: Path) -> str:
        """Compute hash of a file."""
        h = hashlib.new(self.algorithm)
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(self.CHUNK_SIZE):
                    h.update(chunk)
            return h.hexdigest()
        except (PermissionError, OSError) as e:
            print(f"[!] Cannot read {filepath}: {e}", file=sys.stderr)
            return None

    def _should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded."""
        path_str = str(path)
        return any(pattern in path_str for pattern in self.exclude_patterns)

    def _collect_files(self, target: Path) -> List[Path]:
        """Collect all files from a target path (recursive if dir)."""
        files = []
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            for root, dirs, filenames in os.walk(target):
                # Prune excluded directories
                dirs[:] = [d for d in dirs if not self._should_exclude(Path(root) / d)]
                for name in filenames:
                    fp = Path(root) / name
                    if not self._should_exclude(fp):
                        files.append(fp)
        return sorted(files)

    # ---------- Baseline ----------
    def create_baseline(self, targets: List[str]) -> None:
        """Create a new baseline from given files/directories."""
        baseline = {
            "created": datetime.utcnow().isoformat(),
            "algorithm": self.algorithm,
            "files": {}
        }

        total = 0
        for t in targets:
            target = Path(t).resolve()
            if not target.exists():
                print(f"[!] Path does not exist: {target}", file=sys.stderr)
                continue

            for fp in self._collect_files(target):
                digest = self._hash_file(fp)
                if digest:
                    baseline["files"][str(fp)] = {
                        "hash": digest,
                        "size": fp.stat().st_size
                    }
                    total += 1

        self.baseline_path.write_text(json.dumps(baseline, indent=2))
        print(f"[+] Baseline created: {self.baseline_path}")
        print(f"[+] {total} file(s) hashed with {self.algorithm}")

    def _load_baseline(self) -> Dict:
        """Load baseline file."""
        if not self.baseline_path.exists():
            print(f"[!] Baseline not found: {self.baseline_path}", file=sys.stderr)
            sys.exit(1)
        try:
            return json.loads(self.baseline_path.read_text())
        except json.JSONDecodeError:
            print("[!] Baseline file is corrupted.", file=sys.stderr)
            sys.exit(1)

    # ---------- Verification ----------
    def verify(self, targets: List[str] = None, verbose: bool = False) -> bool:
        """
        Verify current state against baseline.
        Returns True if no changes detected, False otherwise.
        """
        baseline = self._load_baseline()
        old_files: Dict[str, Dict] = baseline.get("files", {})

        # Determine which paths to scan
        if targets:
            current_files = set()
            for t in targets:
                target = Path(t).resolve()
                if target.exists():
                    for fp in self._collect_files(target):
                        current_files.add(str(fp))
        else:
            # Scan all baseline paths
            current_files = set()
            for path_str in old_files:
                p = Path(path_str)
                if p.exists() and p.is_file():
                    current_files.add(path_str)

        added, modified, deleted = [], [], []

        # Detect added & modified
        for path_str in sorted(current_files):
            fp = Path(path_str)
            new_hash = self._hash_file(fp)
            if not new_hash:
                continue

            if path_str not in old_files:
                added.append(path_str)
            elif new_hash != old_files[path_str]["hash"]:
                modified.append(path_str)

        # Detect deleted
        for path_str in old_files:
            if not Path(path_str).exists():
                deleted.append(path_str)

        # Report
        print("\n" + "=" * 60)
        print(f"  File Integrity Report - {datetime.now().isoformat()}")
        print("=" * 60)
        print(f"  Baseline created : {baseline.get('created', 'N/A')}")
        print(f"  Algorithm        : {baseline.get('algorithm', self.algorithm)}")
        print(f"  Files checked    : {len(current_files)}")
        print("-" * 60)

        if added:
            print(f"\n[+] ADDED ({len(added)}):")
            for f in added:
                print(f"    + {f}")

        if modified:
            print(f"\n[~] MODIFIED ({len(modified)}):")
            for f in modified:
                print(f"    ~ {f}")
                if verbose:
                    old_h = old_files[f]["hash"][:16]
                    new_h = self._hash_file(Path(f))[:16]
                    print(f"        old: {old_h}...")
                    print(f"        new: {new_h}...")

        if deleted:
            print(f"\n[-] DELETED ({len(deleted)}):")
            for f in deleted:
                print(f"    - {f}")

        if not (added or modified or deleted):
            print("\n[✓] No changes detected. All files intact.")

        print("\n" + "=" * 60)
        return not (added or modified or deleted)

    # ---------- Update baseline ----------
    def update_baseline(self, targets: List[str]) -> None:
        """Update baseline with current file states (accept changes)."""
        baseline = self._load_baseline()
        files = baseline.get("files", {})

        for t in targets:
            target = Path(t).resolve()
            if target.exists():
                for fp in self._collect_files(target):
                    digest = self._hash_file(fp)
                    if digest:
                        files[str(fp)] = {
                            "hash": digest,
                            "size": fp.stat().st_size
                        }

        # Remove entries whose files no longer exist
        files = {k: v for k, v in files.items() if Path(k).exists()}

        baseline["files"] = files
        baseline["updated"] = datetime.utcnow().isoformat()
        self.baseline_path.write_text(json.dumps(baseline, indent=2))
        print(f"[+] Baseline updated: {self.baseline_path}")


# ---------------- CLI ----------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fim",
        description="File Integrity Monitor - detect file changes via hashing."
    )
    parser.add_argument(
        "-b", "--baseline", default=FileIntegrityMonitor.DEFAULT_BASELINE,
        help="Path to baseline JSON file (default: baseline.json)"
    )
    parser.add_argument(
        "-a", "--algorithm", default="sha256",
        choices=["md5", "sha1", "sha256", "sha512"],
        help="Hash algorithm (default: sha256)"
    )
    parser.add_argument(
        "-e", "--exclude", action="append", default=[],
        help="Patterns to exclude (can be used multiple times)"
    )
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")

    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a new baseline")
    p_init.add_argument("paths", nargs="+", help="Files/directories to monitor")

    p_check = sub.add_parser("check", help="Check files against baseline")
    p_check.add_argument("paths", nargs="*", help="Paths to check (default: all)")

    p_update = sub.add_parser("update", help="Update baseline with current state")
    p_update.add_argument("paths", nargs="+", help="Paths to update")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    fim = FileIntegrityMonitor(
        baseline_path=args.baseline,
        algorithm=args.algorithm,
        exclude_patterns=args.exclude or None
    )

    if args.command == "init":
        fim.create_baseline(args.paths)
    elif args.command == "check":
        ok = fim.verify(args.paths or None, verbose=args.verbose)
        sys.exit(0 if ok else 2)
    elif args.command == "update":
        fim.update_baseline(args.paths)


if __name__ == "__main__":
    main()