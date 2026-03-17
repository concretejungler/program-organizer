"""
Build script for Program Organizer.
Creates a standalone executable using PyInstaller.
"""
import PyInstaller.__main__
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
BUILD_DIR = os.path.join(BASE_DIR, "build")

def clean():
    """Remove previous build artifacts."""
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
    for f in os.listdir(BASE_DIR):
        if f.endswith(".spec"):
            os.remove(os.path.join(BASE_DIR, f))

def build():
    """Run PyInstaller to create the executable."""
    clean()

    # Create icon if it doesn't exist
    icon_path = os.path.join(BASE_DIR, "icon.ico")
    if not os.path.exists(icon_path):
        create_icon(icon_path)

    PyInstaller.__main__.run([
        "app.py",
        "--name=ProgramOrganizer",
        "--onedir",
        "--windowed",
        f"--icon={icon_path}",
        f"--add-data=static{os.pathsep}static",
        "--hidden-import=pystray._win32",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "--exclude-module=tkinter",
        "--exclude-module=IPython",
        "--exclude-module=notebook",
        "--exclude-module=pytest",
        "--noconfirm",
        "--clean",
    ])

    # Create programs folder in dist
    programs_dir = os.path.join(DIST_DIR, "ProgramOrganizer", "programs")
    os.makedirs(programs_dir, exist_ok=True)

    print("\n" + "=" * 50)
    print("Build complete!")
    print(f"Output: {os.path.join(DIST_DIR, 'ProgramOrganizer')}")
    print("=" * 50)

def create_icon(path):
    """Generate a simple .ico file."""
    from PIL import Image, ImageDraw

    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []

    for size in sizes:
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        margin = max(2, size[0] // 16)
        # Blue circle
        draw.ellipse(
            [margin, margin, size[0] - margin, size[1] - margin],
            fill=(15, 52, 96),
        )
        # Play triangle
        cx, cy = size[0] // 2, size[1] // 2
        s = size[0] // 4
        draw.polygon(
            [(cx - s // 2, cy - s), (cx - s // 2, cy + s), (cx + s, cy)],
            fill=(233, 69, 96),
        )
        images.append(img)

    images[0].save(path, format="ICO", sizes=[(s[0], s[1]) for s in sizes], append_images=images[1:])
    print(f"Icon created: {path}")

if __name__ == "__main__":
    build()
