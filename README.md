<div align="center">

# 🔐 File Integrity Monitor

**A lightweight, dependency-free Python tool that hashes files, stores baseline checksums, and detects additions, modifications, and deletions.**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](#-installation)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey.svg)](#-installation)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Perfect for security monitoring, CI/CD pipelines, and file tamper detection.

[Features](#-features) · [Installation](#-installation) · [Quick Start](#-quick-start) · [Usage](#-usage) · [CI/CD](#-cicd-integration) · [Roadmap](#-roadmap)

</div>

---

## 📖 Table of Contents

- [Why FIM?](#-why-fim)
- [Features](#-features)
- [Demo](#-demo)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [Create a Baseline](#1️⃣-create-a-baseline)
  - [Check for Changes](#2️⃣-check-for-changes)
  - [Update the Baseline](#3️⃣-update-the-baseline)
- [CLI Reference](#-cli-reference)
- [How It Works](#-how-it-works)
- [Baseline Format](#-baseline-format)
- [CI/CD Integration](#-cicd-integration)
- [Use Cases](#-use-cases)
- [Security Notes](#-security-notes)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Why FIM?

Ever wondered if a config file, script, or critical directory was silently modified? **File Integrity Monitor** gives you a simple, deterministic answer:

- 🔐 **Tamper detection** — know instantly when files change
- 🚀 **Zero dependencies** — pure Python 3.8+ standard library
- 🧩 **CI/CD ready** — non-zero exit code on change detection
- 📦 **Portable** — one file, one baseline, works everywhere

Whether you're monitoring server configs, source code, or sensitive directories, FIM is a lightweight watchdog you can drop anywhere.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔒 **Multiple hash algorithms** | MD5, SHA-1, SHA-256 (default), SHA-512 |
| 📂 **Recursive scanning** | Point at a directory — it walks everything |
| 🚫 **Smart exclusions** | Skip `.git`, `__pycache__`, `.log`, `.tmp` by default |
| 📝 **JSON baseline** | Human-readable, version-controllable, diff-friendly |
| 🔍 **Three-way diff** | Detects **added**, **modified**, and **deleted** files |
| ⚡ **Chunked hashing** | Streams 64 KB chunks — handles large files |
| ✅ **Exit codes** | `0` = clean, `2` = changes detected |
| 🐍 **Pure stdlib** | No `pip install` needed |

---

## 🎬 Demo

```bash
$ mkdir demo && echo "hello" > demo/a.txt && echo "world" > demo/b.txt

$ python fim.py init demo
[+] Baseline created: baseline.json
[+] 2 file(s) hashed with sha256

# ...time passes, files change...

$ echo "modified" > demo/a.txt
$ echo "new" > demo/c.txt
$ rm demo/b.txt

$ python fim.py check -v
============================================================
  File Integrity Report - 2025-01-15T10:45:00
============================================================
  Baseline created : 2025-01-15T10:30:00
  Algorithm        : sha256
  Files checked    : 2
------------------------------------------------------------

[+] ADDED (1):
    + /home/user/demo/c.txt

[~] MODIFIED (1):
    ~ /home/user/demo/a.txt
        old: a1b2c3d4e5f6...
        new: 9f8e7d6c5b4a...

[-] DELETED (1):
    - /home/user/demo/b.txt

============================================================
```

---

## 📦 Installation

### Option 1: Clone the repo

```bash
git clone https://github.com/mohitsharma099999-tech/file-integrity-monitor.git
cd file-integrity-monitor
```

### Option 2: Download single file

Just grab [`fim.py`](./fim.py) — that's the whole tool.

### Requirements

- Python **3.8+** (uses the walrus operator `:=`)
- No external packages

Verify your Python version:

```bash
python --version
```

### Optional — install as a command

```bash
chmod +x fim.py
ln -s "$(pwd)/fim.py" /usr/local/bin/fim

# now use it anywhere
fim init /etc/nginx
fim check -v
```

---

## 🚀 Quick Start

Three commands, sixty seconds:

```bash
# 1️⃣ Create a baseline of what you want to monitor
python fim.py init /path/to/monitor

# 2️⃣ ...later, check what changed
python fim.py check -v

# 3️⃣ Accept intentional changes and update the baseline
python fim.py update /path/to/monitor
```

That's it. No config files, no daemons, no fuss.

---

## 📚 Usage

### 1️⃣ Create a Baseline

Hashes every file under the given paths and writes a baseline JSON.

```bash
python fim.py init <path1> <path2> ...
```

**Example:**

```bash
python fim.py -a sha512 -b prod_baseline.json init /etc/nginx /etc/ssh
```

### 2️⃣ Check for Changes

Compare current state against the baseline.

```bash
python fim.py check [paths...] [-v]
```

- **No paths** → checks all files listed in the baseline
- **With paths** → checks only those directories/files

**Example:**

```bash
python fim.py -b prod_baseline.json check -v
```

Verbose mode (`-v`) shows old vs. new hash prefixes for modified files.

### 3️⃣ Update the Baseline

Accept the current state as the new "known good".

```bash
python fim.py update <path1> <path2> ...
```

Automatically removes entries for files that no longer exist.

**Example:**

```bash
python fim.py -b prod_baseline.json update /etc/nginx
```

---

## 🛠 CLI Reference

### Global Options

| Flag | Description | Default |
|------|-------------|---------|
| `-b, --baseline PATH` | Path to baseline JSON file | `baseline.json` |
| `-a, --algorithm NAME` | `md5` \| `sha1` \| `sha256` \| `sha512` | `sha256` |
| `-e, --exclude PATTERN` | Exclude pattern (repeatable) | `.git`, `__pycache__`, ... |
| `-v, --verbose` | Verbose output | off |
| `--version` | Show version and exit | — |

### Subcommands

| Command | Arguments | Description |
|---------|-----------|-------------|
| `init` | `paths...` | Create a new baseline |
| `check` | `[paths...]` | Verify files against baseline |
| `update` | `paths...` | Update baseline with current state |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success / no changes detected |
| `1` | Error (missing baseline, corrupted file, etc.) |
| `2` | Changes detected during `check` |

---

## 🔬 How It Works

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   init      │ ──► │  baseline    │ ◄── │   update     │
│  (hashing)  │     │    .json     │     │  (re-hash)   │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    check     │
                    │ (compare)    │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           ADDED       MODIFIED      DELETED
```

1. **`init`** — Recursively walks each path, hashes files in 64 KB chunks, records `{path: {hash, size}}` in JSON.
2. **`check`** — Re-hashes each file and classifies:
   - **Added** → present now, absent in baseline
   - **Modified** → present in both, hash differs
   - **Deleted** → in baseline, missing now
3. **`update`** — Refreshes hashes and prunes stale entries.

---

## 📄 Baseline Format

The baseline is plain JSON — easy to read, diff, and store in version control:

```json
{
  "created": "2025-01-15T10:30:00.000000",
  "algorithm": "sha256",
  "files": {
    "/abs/path/to/file.txt": {
      "hash": "3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b",
      "size": 1024
    },
    "/abs/path/to/config.yaml": {
      "hash": "f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2",
      "size": 512
    }
  }
}
```

> 💡 **Tip:** Use absolute paths in baselines to avoid ambiguity when running `check` from different working directories.

---

## 🔁 CI/CD Integration

FIM's exit codes make it perfect as a pipeline gate.

### GitHub Actions

```yaml
name: File Integrity Check

on: [push, pull_request]

jobs:
  fim:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run FIM check
        run: python fim.py -b .fim/baseline.json check -v
```

### GitLab CI

```yaml
fim-check:
  image: python:3.11-slim
  script:
    - python fim.py -b .fim/baseline.json check -v
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit
python fim.py -b .fim/baseline.json check || {
  echo "❌ File integrity check failed. Run 'python fim.py update .' if changes are intentional."
  exit 1
}
```

Make it executable:

```bash
chmod +x .git/hooks/pre-commit
```

### Shell one-liners

```bash
python fim.py check || echo "⚠️  Files changed!"
python fim.py check && echo "✅  All good"
```

---

## 💡 Use Cases

- 🖥️ **Server hardening** — monitor `/etc`, `/usr/local/bin`, web roots
- 📦 **Release verification** — ensure shipped artifacts weren't tampered with
- 🔧 **Config drift detection** — catch unauthorized config edits
- 🧪 **Test fixtures** — verify golden files haven't changed
- 🎯 **Incident response** — snapshot a compromised system, detect further changes
- 🔐 **Compliance** — evidence of file integrity for audits (PCI-DSS, HIPAA, SOC 2)

---

## 🔒 Security Notes

- ✅ **SHA-256 by default.** MD5/SHA-1 are available for compatibility only — do **not** use them for security-critical monitoring.
- ✅ **Protect your baseline.** Anyone who can edit `baseline.json` can defeat detection.
  ```bash
  chmod 600 baseline.json
  ```
- ✅ **Baselines are not signed.** For tamper-proof baselines, add HMAC signing (see [Roadmap](#-roadmap)).
- ✅ **Detection, not prevention.** FIM tells you *that* files changed — it doesn't stop the change. Pair with proper access controls (SELinux, AppArmor, file permissions).
- ✅ **Store baselines off-host.** Keep a copy on a read-only medium or remote system for true integrity guarantees.

---

## 🗺 Roadmap

- [ ] **Watch mode** — real-time monitoring via `watchdog`
- [ ] **HMAC-signed baselines** — tamper-proof JSON
- [ ] **Alerting** — email, Slack, webhook notifications
- [ ] **SQLite backend** — for millions of files
- [ ] **Parallel hashing** — `concurrent.futures` speedup
- [ ] **Merkle tree mode** — efficient large-scale verification
- [ ] **Docker image** — `docker run fim check /data`
- [ ] **PyPI package** — `pip install file-integrity-monitor`

Have an idea? [Open an issue](https://github.com/mohitsharma099999-tech/file-integrity-monitor/issues) 🚀

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development

```bash
# Clone
git clone https://github.com/mohitsharma099999-tech/file-integrity-monitor.git
cd file-integrity-monitor

# Run tests (coming soon)
python -m unittest discover tests/
```

Please make sure to update tests as appropriate and follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 mohit sharma

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## ⭐ Show Your Support

If this project helped you, please consider:

- ⭐ **Starring** the repo
- 🐛 **Reporting bugs** via [issues](https://github.com/mohitsharma099999-tech/file-integrity-monitor/issues)
- 💬 **Sharing** it with others who might find it useful
- ☕ **Buying me a coffee** (optional)

---

<div align="center">

**Built with 🐍 Python · Zero dependencies · MIT Licensed**

[⬆ Back to Top](#-file-integrity-monitor)

</div>
