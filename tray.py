import threading
import webbrowser
import pystray
from PIL import Image, ImageDraw


def create_default_icon():
    """Create a simple icon programmatically."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Dark blue circle background
    draw.ellipse([4, 4, 60, 60], fill=(15, 52, 96))
    # White play triangle
    draw.polygon([(24, 18), (24, 46), (48, 32)], fill=(233, 69, 96))
    return img


class SystemTray:
    def __init__(self, port, on_quit):
        self.port = port
        self.on_quit = on_quit
        self.icon = None
        self._thread = None

    def _open_ui(self):
        webbrowser.open(f"http://localhost:{self.port}")

    def _build_menu(self):
        items = [
            pystray.MenuItem(
                "Open Program Organizer", lambda: self._open_ui(), default=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", lambda: self._quit()),
        ]
        return pystray.Menu(*items)

    def _quit(self):
        if self.icon:
            self.icon.stop()
        self.on_quit()

    def start(self):
        image = create_default_icon()
        menu = self._build_menu()
        self.icon = pystray.Icon(
            "program_organizer", image, "Program Organizer", menu
        )
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()
