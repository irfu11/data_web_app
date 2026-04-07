
import signal
import sys
import os

# Add script directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import DataLensApp


def _handle_sigint(signum, frame):
    try:
        app.destroy()
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    app = DataLensApp()
    signal.signal(signal.SIGINT, _handle_sigint)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        try:
            app.destroy()
        except Exception:
            pass
        sys.exit(0)