# SCIF specification — version 1.0

## 1. overview
The Simple Color Image Format (SCIF) is a tiny binary format that describes images that can be generated procedurally from a few bytes.  
It targets extremely simple visuals (solid fills, gradients, checkerboards) for embedded devices, demos, and education.

## 2. file layout (bytes)

| offset | size | name   | description                     | type |
|--------|------|--------|----------------------------------|------|
| 0x00   | 2    | width  | image width in pixels           | uint16 big-endian |
| 0x02   | 2    | height | image height in pixels          | uint16 big-endian |
| 0x04   | 1    | mode   | rendering mode                  | uint8 |
| 0x05   | var  | data   | mode-specific payload           | variable |

notes: total file size = 5 + data length.

## 3. color values
all color components are 8-bit (0–255). color triplets are ordered r,g,b.

## 4. modes

### mode 0x01 — solid color
payload: `R G B` (3 bytes)

interpretation: every pixel = (R,G,B).

### mode 0x02 — vertical gradient
payload: `R1 G1 B1 R2 G2 B2` (6 bytes)

interpretation: interpolate top (R1,G1,B1) to bottom (R2,G2,B2). interpolation is linear per channel.  
for pixel at vertical position y (0..height-1), t = y / (height - 1).

### mode 0x03 — horizontal gradient
payload: `R1 G1 B1 R2 G2 B2` (6 bytes)

interpretation: interpolate left (R1,G1,B1) to right (R2,G2,B2).  
for pixel at horizontal position x (0..width-1), t = x / (width - 1).

### mode 0x04 — checkerboard
payload: `R1 G1 B1 R2 G2 B2` (6 bytes)

interpretation: alternating squares of two colors.  
default square size = 8 pixels.  
color at pixel (x,y) = color1 if ((x // 8) + (y // 8)) % 2 == 0 else color2.

## 5. decoding rules
- read width (uint16 big-endian), height (uint16 big-endian), mode (uint8), then mode payload.  
- gradients interpolate per channel and clamp results to 0..255.  
- width or height of 0 means invalid image.  
- for 1-pixel dimensions, interpolation is constant.

## 6. extensibility
- add a version byte or flags field in future revisions.  
- future modes may include alpha, variable tile size, shapes, or compression.  
- maintain backward compatibility by reserving mode values.

## 7. examples
- 100×50 solid red (8 bytes):  
00 64 00 32 01 FF 00 00

- 4×4 horizontal gradient black→white (11 bytes):  
00 04 00 04 03 00 00 00 FF FF FF
---
