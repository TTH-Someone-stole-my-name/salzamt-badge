#!/usr/bin/python3

import sys
from PIL import Image

png=Image.open(sys.argv[1]).convert("RGBA")
print(png.size)
print(max(png.size),max(png.size))
png=png.resize((max(png.size),max(png.size)))
background=Image.new("RGBA", (max(png.size),max(png.size)), (255,255,255))
comp=Image.alpha_composite(background, png)
comp.save("test.png", "PNG")
