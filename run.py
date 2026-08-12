"""
Enterprise Document Intelligence Platform — Single Command Launcher.
Starts both FastAPI backend (port 8000) and Streamlit UI (port 8501) together.

Usage:
    python run.py
"""
import sys
import os
import time
import subprocess

# Force UTF-8 encoding for Windows standard output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("\n" + "=" * 60)
    print("  Enterprise Document Intelligence Platform")
    print("=" * 60)
    print(f"  Starting FastAPI API   ->  http://localhost:8000")
    print(f"  Starting Streamlit UI  ->  http://localhost:8501")
    print(f"  Swagger API Docs       ->  http://localhost:8000/docs")
    print(f"\n  Press Ctrl+C to stop all services.")
    print("=" * 60 + "\n")

    processes = []

    try:
        # 1. Start FastAPI backend
        api_proc = subprocess.Popen(
            [PYTHON, "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            cwd=BASE_DIR,
        )
        processes.append(api_proc)

        time.sleep(2)

        # 2. Start Streamlit frontend
        ui_proc = subprocess.Popen(
            [PYTHON, "-m", "streamlit", "run", "streamlit_app.py", "--server.headless", "true"],
            cwd=BASE_DIR,
        )
        processes.append(ui_proc)

        # Wait for processes
        for proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        print("\n\nShutting down all services...")
        for proc in processes:
            proc.terminate()
        for proc in processes:
            proc.wait()
        print("All services stopped successfully.\n")


if __name__ == "__main__":
    main()
