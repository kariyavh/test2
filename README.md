# Office Efficiency Toolkit

Streamline everyday office chores with a single desktop-style application. The Office Efficiency Toolkit
runs on [Streamlit](https://streamlit.io/) and bundles three frequently requested helpers:

- **Data merge** – combine CSV and Excel files, clean headers, remove duplicates, and export a tidy dataset.
- **PDF merge** – stitch together multiple PDF files with a single click.
- **Batch rename** – rename every file in a folder using prefixes, suffixes, find-and-replace, and automatic numbering.

The project is designed so non-technical teammates can run it locally with Python or download ready-to-use
binaries from GitHub releases.

## Getting started locally

1. Install Python 3.10 or newer.
2. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/kariyavh/test3.git
   cd test3
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Launch the app:

   ```bash
   streamlit run office_toolkit/app.py
   ```

   Streamlit starts a local server and opens the toolkit in your browser.

### Cloning alternatives

If GitHub Desktop or Git Bash refuse to clone because of `fork: Resource temporarily unavailable`
messages, the issue is almost always caused by security software blocking Git from spawning new
helper processes. Try the following remedies:

1. Close GitHub Desktop, then add the folder `C:\\Users\\<YOU>\\AppData\\Local\\GitHubDesktop\\app-*\\resources\\app\\git`
   to your antivirus allow-list (the path holds Git's `usr\bin` and `mingw64\bin` executables).
2. Re-open GitHub Desktop or Git Bash after a reboot so the allow-list change takes effect.
3. If the problem continues, install the latest [Git for Windows](https://gitforwindows.org/) and run
   `git clone https://github.com/kariyavh/test3.git` from a regular Command Prompt or PowerShell
   window.

When cloning still is not an option, grab the source directly from the repository page via
**Code → Download ZIP** or use the automated release packages that appear on the
[`Releases`](https://github.com/kariyavh/test3/releases) tab.

### Using the toolkit

- **Data merge tab** – upload one or more CSV/Excel files. The toolkit cleans column names, merges rows,
  and lets you choose how duplicates are handled before downloading a CSV or Excel export.
- **PDF merge tab** – drop two or more PDFs and download a single combined file.
- **Batch rename tab** – enter a folder path on your machine to preview how files will be renamed. Configure
  prefix/suffix text, find-and-replace rules, and sequential numbering before committing the changes.

## One-click desktop builds

Standalone executables are created with [PyInstaller](https://pyinstaller.org/). Two helper scripts wrap the
build process and create zip archives with the compiled app:

- `build_windows.bat`
- `build_macos.sh`

Run the script for your platform from the project root. Both scripts install dependencies, invoke PyInstaller,
package the output, and drop a zip file in the repository directory.

> **Tip for macOS users:** the script attempts to create a universal (Intel + Apple Silicon) build when PyInstaller
> on your system supports the `--target-arch` flag. Set the `PYINSTALLER_ARCH` environment variable to `x86_64`,
> `arm64`, or `universal2` to override the default.

## Automated releases

Pushing a tag that starts with `v` (for example `v1.0.0`) triggers the **Build and release binaries** workflow. The
workflow runs on Windows and macOS to produce platform-specific packages and attaches them to a GitHub release for
that tag. Release notes and artifacts are generated automatically—ideal for sharing the toolkit with colleagues
who just want a download link.

To create a tagged release manually:

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions handles the rest.

## Project structure

```
.
├── office_toolkit/          # Streamlit UI and helper modules
├── run_app.py               # PyInstaller-friendly entry point
├── build_windows.bat        # One-click Windows build
├── build_macos.sh           # One-click macOS build
├── requirements.txt         # Python dependencies
└── .github/workflows/       # Release automation
```

## Contributing and support

Issues and pull requests are welcome. If you run into any problems or have feature suggestions, open an issue on
GitHub so we can keep refining the toolkit for office teams everywhere.
