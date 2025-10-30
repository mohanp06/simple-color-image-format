# SCIF tools and reference implementation

this document provides a simple python reference implementation and usage guide.

## 1. files
- `scif_tools.py` — python tool for encoding/decoding/viewing scif files  
- `examples/` — folder for sample `.scif` files  

## 2. python reference tool

```python
#!/usr/bin/env python3
import sys
from PIL import Image

# --- encoder ---

def save_solid(path, width, height, r, g, b):
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([1, r, g, b]))

def save_vertical_gradient(path, width, height, r1, g1, b1, r2, g2, b2):
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([2, r1, g1, b1, r2, g2, b2]))

def save_horizontal_gradient(path, width, height, r1, g1, b1, r2, g2, b2):
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([3, r1, g1, b1, r2, g2, b2]))

def save_checkerboard(path, width, height, r1, g1, b1, r2, g2, b2):
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([4, r1, g1, b1, r2, g2, b2]))

# --- decoder ---

def read_scif(path):
    with open(path, 'rb') as f:
        data = f.read()
    if len(data) < 5:
        raise ValueError('too short')
    w, h, mode = int.from_bytes(data[0:2], 'big'), int.from_bytes(data[2:4], 'big'), data[4]
    payload = data[5:]

    if mode == 1:
        r, g, b = payload[:3]
        return Image.new('RGB', (w, h), (r, g, b))

    elif mode in (2, 3):
        r1, g1, b1, r2, g2, b2 = payload[:6]
        img = Image.new('RGB', (w, h))
        px = img.load()
        for y in range(h):
            for x in range(w):
                t = (y / (h-1)) if mode == 2 else (x / (w-1))
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                px[x, y] = (r, g, b)
        return img

    elif mode == 4:
        r1, g1, b1, r2, g2, b2 = payload[:6]
        img = Image.new('RGB', (w, h))
        px = img.load()
        for y in range(h):
            for x in range(w):
                color = (r1, g1, b1) if ((x//8 + y//8) % 2 == 0) else (r2, g2, b2)
                px[x, y] = color
        return img

    else:
        raise ValueError('unknown mode')

# --- cli ---

def main():
    args = sys.argv[1:]
    if not args:
        print('usage:')
        print('  save_solid out.scif w h r g b')
        print('  save_vgrad out.scif w h r1 g1 b1 r2 g2 b2')
        print('  save_hgrad out.scif w h r1 g1 b1 r2 g2 b2')
        print('  save_checker out.scif w h r1 g1 b1 r2 g2 b2')
        print('  view file.scif')
        print('  topng file.scif out.png')
        return

    cmd = args[0]
    if cmd == 'view':
        img = read_scif(args[1])
        img.show()
    elif cmd == 'topng':
        img = read_scif(args[1])
        img.save(args[2])
    elif cmd.startswith('save_'):
        eval(cmd)(*args[1:])
    else:
        print('unknown command')

if __name__ == '__main__':
    main()

## 3. requirements

python ≥ 3.8
pillow (pip install pillow)

##4. build windows exe
pip install pyinstaller
pyinstaller --onefile scif_tools.py

output will be in dist/scif_tools.exe.

---
