'''
# scif_spec_v1.md

# SCIF specification — version 1.0

## 1. overview

The Simple Color Image Format (SCIF) is a tiny binary format that describes images that can be generated procedurally from a few bytes. It targets extremely simple visuals (solid fills, gradients, checkerboards) for embedded devices, demos, and education.

## 2. file layout (bytes)

| offset | size | name   | description            | type              |
| ------ | ---- | ------ | ---------------------- | ----------------- |
| 0x00   | 2    | width  | image width in pixels  | uint16 big-endian |
| 0x02   | 2    | height | image height in pixels | uint16 big-endian |
| 0x04   | 1    | mode   | rendering mode         | uint8             |
| 0x05   | var  | data   | mode-specific payload  | variable          |

notes: total file size = 5 + data length.

## 3. color values

all color components are 8-bit (0–255). color triplets are ordered r,g,b.

## 4. modes

### mode 0x01 — solid color

payload: `R G B` (3 bytes)

interpretation: every pixel = (R,G,B).

### mode 0x02 — vertical gradient

payload: `R1 G1 B1 R2 G2 B2` (6 bytes)

interpretation: interpolate top (R1,G1,B1) to bottom (R2,G2,B2). interpolation is linear per channel. for pixel at vertical position y (0..height-1), t = y / (height - 1).

### mode 0x03 — horizontal gradient

payload: `R1 G1 B1 R2 G2 B2` (6 bytes)

interpretation: interpolate left (R1,G1,B1) to right (R2,G2,B2). for pixel at horizontal position x (0..width-1), t = x / (width - 1).

### mode 0x04 — checkerboard

payload: `R1 G1 B1 R2 G2 B2` (6 bytes)

interpretation: alternating squares of two colors. default square size = 8 pixels. color at pixel (x,y) = color1 if ((x // 8) + (y // 8)) % 2 == 0 else color2.

## 5. decoding rules

* read width (uint16 big-endian), height (uint16 big-endian), mode (uint8), then mode payload.
* if width or height is zero, treat as empty image (no output). implementations may reject zero dimensions.
* for gradients, if dimension is 1 (width or height), treat interpolation as constant color equal to start color.
* clamp all computed channel values to 0..255 and round to nearest integer.

## 6. extensibility

* add a version byte or flags field in front of mode in future revisions.
* future modes can include alpha, variable tile size, shapes (circle, stripe), or simple run-length compression.
* maintain backward compatibility by reserving mode values and including spec version in repo.

## 7. implementation notes

* choose big-endian for byte order to keep the header compact and predictable across platforms.
* reference implementations should be tiny and language-agnostic.
* do not include metadata or compression in v1; keep format minimal.

## 8. examples

* 100×50 solid red (7 bytes):

```
00 64 00 32 01 FF 00 00
```

* 4×4 horizontal gradient from black to white (11 bytes):

```
00 04 00 04 03 00 00 00 FF FF FF
```

---

# scif_tools.md

# scif tools and reference implementation

this document contains a small reference CLI tool, usage examples, and steps to produce a runnable windows executable.

## files

* `scif_tools.py` — reference python script: save and load scif files, convert to png, and show images.
* `examples/` — sample scif files (solid, gradients, checkerboards).

## python reference tool (`scif_tools.py`)

'''

#!/usr/bin/env python3
import sys
from PIL import Image

# --- encoder ---

def save_solid(path, width, height, r, g, b):
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([1]))
        f.write(bytes([r, g, b]))

def save_vertical_gradient(path, width, height, r1, g1, b1, r2, g2, b2):
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([2]))
        f.write(bytes([r1, g1, b1, r2, g2, b2]))

def save_horizontal_gradient(path, width, height, r1, g1, b1, r2, g2, b2):
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([3]))
        f.write(bytes([r1, g1, b1, r2, g2, b2]))

def save_checkerboard(path, width, height, r1, g1, b1, r2, g2, b2, square=8):
    # v1 payload ignores square size; keep square param for convenience when creating the png output
    with open(path, 'wb') as f:
        f.write(width.to_bytes(2, 'big'))
        f.write(height.to_bytes(2, 'big'))
        f.write(bytes([4]))
        f.write(bytes([r1, g1, b1, r2, g2, b2]))

# --- decoder ---

def read_scif(path):
    with open(path, 'rb') as f:
        header = f.read(5)
        if len(header) < 5:
            raise ValueError('file too small')
        width = int.from_bytes(header[0:2], 'big')
        height = int.from_bytes(header[2:4], 'big')
        mode = header[4]
        data = f.read()

    if mode == 1:
        if len(data) < 3:
            raise ValueError('payload too small for solid color')
        r, g, b = data[0], data[1], data[2]
        return Image.new('RGB', (width, height), (r, g, b))

    elif mode in (2, 3):
        if len(data) < 6:
            raise ValueError('payload too small for gradient')
        r1, g1, b1, r2, g2, b2 = data[0:6]
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        for y in range(height):
            for x in range(width):
                t = (y / (height - 1)) if mode == 2 and height > 1 else (x / (width - 1)) if mode == 3 and width > 1 else 0.0
                r = int(round(r1 + (r2 - r1) * t))
                g = int(round(g1 + (g2 - g1) * t))
                b = int(round(b1 + (b2 - b1) * t))
                pixels[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        return img

    elif mode == 4:
        if len(data) < 6:
            raise ValueError('payload too small for checkerboard')
        r1, g1, b1, r2, g2, b2 = data[0:6]
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        for y in range(height):
            for x in range(width):
                color = (r1, g1, b1) if ((x // 8 + y // 8) % 2 == 0) else (r2, g2, b2)
                pixels[x, y] = color
        return img

    else:
        raise ValueError('unknown mode')

# --- CLI ---

def print_usage():
    print('usage:')
    print('  scif_tools.py save_solid out.scif width height r g b')
    print('  scif_tools.py save_vgrad out.scif width height r1 g1 b1 r2 g2 b2')
    print('  scif_tools.py save_hgrad out.scif width height r1 g1 b1 r2 g2 b2')
    print('  scif_tools.py save_checker out.scif width height r1 g1 b1 r2 g2 b2')
    print('  scif_tools.py view file.scif')
    print('  scif_tools.py topng file.scif out.png')

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print_usage(); sys.exit(1)

    cmd = args[0]

    try:
        if cmd == 'save_solid' and len(args) == 7:
            _, out, w, h, r, g, b = args
            save_solid(out, int(w), int(h), int(r), int(g), int(b))
            print('saved', out)

        elif cmd == 'save_vgrad' and len(args) == 10:
            _, out, w, h, r1, g1, b1, r2, g2, b2 = args
            save_vertical_gradient(out, int(w), int(h), *map(int, (r1, g1, b1, r2, g2, b2)))
            print('saved', out)

        elif cmd == 'save_hgrad' and len(args) == 10:
            _, out, w, h, r1, g1, b1, r2, g2, b2 = args
            save_horizontal_gradient(out, int(w), int(h), *map(int, (r1, g1, b1, r2, g2, b2)))
            print('saved', out)

        elif cmd == 'save_checker' and len(args) == 10:
            _, out, w, h, r1, g1, b1, r2, g2, b2 = args
            save_checkerboard(out, int(w), int(h), *map(int, (r1, g1, b1, r2, g2, b2)))
            print('saved', out)

        elif cmd == 'view' and len(args) == 2:
            _, path = args
            img = read_scif(path)
            img.show()

        elif cmd == 'topng' and len(args) == 3:
            _, path, outpng = args
            img = read_scif(path)
            img.save(outpng)
            print('wrote', outpng)

        else:
            print_usage()

    except Exception as e:
        print('error:', e)
'''

## requirements

* python 3.8+
* pillow (`pip install pillow`)

## make a windows exe

1. install pyinstaller: `pip install pyinstaller`
2. build single exe: `pyinstaller --onefile scif_tools.py`
3. find the executable in `dist/scif_tools.exe`.

notes:

* include additional files (examples) by adding `--add-data` to pyinstaller command.
* test the exe on a clean machine or VM to ensure dependencies are bundled correctly.

## recommended repo layout

```
simple-color-image-format/
├── README.md
├── scif_spec_v1.md
├── scif_tools.py
├── examples/
│   ├── red.scif
│   ├── gradient.scif
│   └── checker.scif
└── LICENSE
```

## next steps

* add unit tests for encoder/decoder
* add small web demo (js decoder)
* document versioning plan and contribution guide
'''