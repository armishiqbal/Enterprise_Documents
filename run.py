"""
Enterprise Document Intelligence Platform — Single Command Launcher.
Starts both FastAPI backend (port 8000) and Streamlit UI (port 8501) together.

Usage:
    python run.py
"""
import socket
import subprocess
import sys
import time
import os

# Force UTF-8 encoding for Windows standard output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

PYTHON = sys.executable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def find_free_port(preferred_port: int) -> int:
    """Finds an available TCP port starting from preferred_port."""
    for port in range(preferred_port, preferred_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return preferred_port


def main():
    api_port = find_free_port(8000)
    ui_port = find_free_port(8501)

    print("\n" + "=" * 60)
    print("  Enterprise Document Intelligence Platform")
    print("=" * 60)
    print(f"  🚀 Starting FastAPI API   ->  http://localhost:{api_port}")
    print(f"  🎨 Starting Streamlit UI  ->  http://localhost:{ui_port}")
    print(f"  📖 Swagger API Docs       ->  http://localhost:{api_port}/docs")
    print(f"\n  Press Ctrl+C to stop all services.")
    print("=" * 60 + "\n")

    processes = []

    try:
        # 1. Start FastAPI backend on 127.0.0.1
        api_proc = subprocess.Popen(
            [PYTHON, "-m", "uvicorn", "src.api:app", "--host", "127.0.0.1", "--port", str(api_port), "--reload"],
            cwd=BASE_DIR,
        )
        processes.append(api_proc)

        time.sleep(2)

        # 2. Start Streamlit frontend on 127.0.0.1
        ui_proc = subprocess.Popen(
            [
                PYTHON,
                "-m",
                "streamlit",
                "run",
                "streamlit_app.py",
                "--server.address",
                "127.0.0.1",
                "--server.port",
                str(ui_port),
                "--server.headless",
                "true",
            ],
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
