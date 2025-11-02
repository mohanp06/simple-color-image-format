# Simple Color Image Format (SCIF)

## overview
**SCIF** (Simple Color Image Format) is a minimal binary image format for ultra-lightweight color storage.  
it’s built for simplicity, tiny size, and instant decoding — perfect for embedded systems, procedural art, and learning how image formats work. 

It can also act as an abstract framework to create other fixed image/audio/text or other file formats out of it, useful for specific cases as defined by the developer of those formats.

---

## features
- stores solid colors, gradients, and simple patterns  
- readable with just a few lines of code  
- cross-platform and open  
- designed to be extended easily  

---

## file structure (version 1)

| bytes | field   | description                     | type / range     |
|--------|----------|----------------------------------|------------------|
| 0–1    | width    | image width in pixels           | uint16 (0–65535) |
| 2–3    | height   | image height in pixels          | uint16 (0–65535) |
| 4      | mode     | rendering mode (see below)      | uint8            |
| 5–...  | data     | color / pattern data            | variable         |

---

## modes

| mode | name               | description                                  | data bytes |
|------|--------------------|----------------------------------------------|-------------|
| 0x01 | solid color        | one rgb color for entire image               | 3 bytes (r,g,b) |
| 0x02 | vertical gradient  | top → bottom gradient                        | 6 bytes (r1,g1,b1,r2,g2,b2) |
| 0x03 | horizontal gradient| left → right gradient                        | 6 bytes (r1,g1,b1,r2,g2,b2) |
| 0x04 | checkerboard       | alternating two colors (8×8 pattern default) | 6 bytes (r1,g1,b1,r2,g2,b2) |

---

## example (solid red)
a 100×50 solid red image:

00 64 00 32 01 FF 00 00

│width│ │height│ │mode│ │R G B│

