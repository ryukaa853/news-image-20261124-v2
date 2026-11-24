"""News front page for Tuesday 24 November 2026.

Draws a 1024x1024 newspaper front page summing up the day's world
news and writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Pure Python 3.13 standard library: no PIL, no network, no clock, no
randomness. Running the program twice writes byte-identical PNGs.

Every story below was checked against a named news source on
24 November 2026 (see README.md for the source list). Figures are
quoted exactly as reported; where an event happened on an earlier
day, the page says so (COP31 ended on Sunday 22 November; the
Nvidia chief executive was reinstated on Monday 23 November).
"""

import os
import struct
import zlib

W, H = 1024, 1024

INK = (18, 18, 18)
PAPER = (255, 253, 246)
RED = (158, 22, 22)
NAVY = (27, 42, 107)
TEAL = (14, 110, 110)
GOLD = (176, 124, 0)
GREY = (96, 96, 96)
LIGHT = (238, 236, 228)
GREEN = (16, 120, 48)
SKY = (196, 220, 235)

# 5x7 bitmap font, uppercase only (classic front-page caps).
# Each glyph is 7 rows of 5 pixels, "1" = ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def text_w(text, scale):
    """Pixel width of text at the given scale."""
    return len(text) * 6 * scale - scale


class Canvas:
    """An RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(0, len(self.px), 3):
            self.px[i] = bg[0]
            self.px[i + 1] = bg[1]
            self.px[i + 2] = bg[2]

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line, with a square brush of `thick` pixels."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            for a in range(-half, half + 1):
                for b in range(-half, half + 1):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, points, color, thick=1):
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            self.line(x0, y0, x1, y1, color, thick)

    def disc(self, cx, cy, r, color):
        """Filled circle, integer scanlines (deterministic)."""
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            half = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - half, cx + half + 1):
                self.set(xx, yy, color)

    def text(self, x, y, s, scale, color):
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(
                            x + col * scale, y + row * scale, scale, scale, color
                        )
            x += 6 * scale

    def centered(self, y, s, scale, color):
        self.text((W - text_w(s, scale)) // 2, y, s, scale, color)


def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    """Write the canvas as a PNG with filter 0 on every scanline."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += png_chunk(b"IHDR", ihdr)
    blob += png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    blob += png_chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(blob)

MX = 28
RX = 996


def build_page():
    c = Canvas(W, H, PAPER)

    # ---- Masthead ----
    c.hline(MX, 8, RX - MX, INK, 2)
    c.centered(20, "THE WORLD TODAY", 6, INK)
    c.centered(70, "TUESDAY 24 NOVEMBER 2026", 2, INK)
    c.centered(90, "NINE STORIES FROM ONE DAY - ALL FACTS CHECKED", 2, GREY)
    c.hline(MX, 112, RX - MX, INK, 4)
    c.hline(MX, 120, RX - MX, RED, 2)

    # ---- Lead story: Nvidia ----
    c.text(MX, 134, "MARKETS - NEW YORK - TUESDAY", 2, RED)
    c.text(MX, 162, "NVIDIA SLIDES 6%", 5, INK)
    c.text(MX, 202, "AFTER MONDAY'S", 5, INK)
    c.text(MX, 242, "31% COMEBACK", 5, INK)
    c.text(MX, 288, "HUANG'S RETURN AS CHIEF EXECUTIVE", 2, INK)
    c.text(MX, 306, "SENT SHARES UP 31% ON MONDAY.", 2, INK)
    c.text(MX, 324, "THE RALLY FADED FAST ON TUESDAY.", 2, INK)

    # Divider between the headline column and the numeral panel.
    c.vline(536, 134, 204, GREY, 1)

    # Big numeral panel: Tuesday's fall, Monday's surge, the wider market.
    c.text(684, 148, "-6%", 11, RED)
    c.text(690, 236, "ON TUESDAY", 3, INK)
    c.text(680, 268, "MONDAY +31%", 3, GREEN)
    c.text(605, 304, "NASDAQ -1.5% - S&P 500 -0.5%", 2, GREY)
    c.text(725, 322, "DOW +0.9%", 2, GREY)

    # Share-price chart: Monday's spike, then Tuesday's slide.
    c.hline(MX, 388, RX - MX, GREY, 1)
    c.polyline([(40, 382), (200, 380), (360, 378), (520, 352)], GREEN, 3)
    c.polyline([(520, 352), (680, 362), (840, 372), (970, 374)], RED, 3)

    c.hline(MX, 404, RX - MX, INK, 4)
    c.hline(MX, 410, RX - MX, RED, 2)

    # ---- Row 2: Sanofi (left) and Gaza (right) ----
    c.text(MX, 424, "BUSINESS - PARIS", 2, RED)
    # Pill capsule illustration: one solid capsule, no band.
    c.fill_rect(414, 434, 64, 22, RED)
    c.disc(414, 445, 11, RED)
    c.disc(478, 445, 11, RED)
    c.text(MX, 452, "SANOFI BUYS INSMED", 3, INK)
    c.text(MX, 478, "FOR $41 BILLION", 3, INK)
    c.text(MX, 514, "$175 A SHARE IN CASH, THE", 2, INK)
    c.text(MX, 532, "YEAR'S BIGGEST PHARMA DEAL.", 2, INK)
    c.text(MX, 550, "CLOSES IN FIRST HALF OF 2027.", 2, INK)
    c.text(MX, 580, "SOURCE: SANOFI, WSJ", 2, GREY)

    c.vline(512, 418, 208, GREY, 1)

    c.text(526, 424, "MIDDLE EAST - GAZA", 2, RED)
    # Target illustration.
    c.disc(940, 445, 18, NAVY)
    c.disc(940, 445, 11, PAPER)
    c.disc(940, 445, 5, RED)
    c.text(526, 452, "ISRAELI STRIKES KILL", 3, INK)
    c.text(526, 478, "HAMAS SECURITY CHIEF", 3, INK)
    c.text(526, 504, "NAEEM ABU NAHEL", 3, INK)
    c.text(526, 540, "SIX OTHERS DIED WITH HIM,", 2, INK)
    c.text(526, 558, "INCLUDING TWO POLICE OFFICERS,", 2, INK)
    c.text(526, 576, "MEDICS AND POLICE SAID. - REUTERS", 2, INK)

    c.hline(MX, 634, RX - MX, INK, 4)
    c.hline(MX, 640, RX - MX, RED, 2)

    # ---- Row 3: Ukraine (left) and COP31 (right) ----
    c.text(MX, 656, "WAR IN UKRAINE", 2, RED)
    # City skyline illustration.
    c.fill_rect(404, 668, 18, 30, GREY)
    c.fill_rect(428, 660, 18, 38, GREY)
    c.fill_rect(452, 672, 18, 26, GREY)
    c.fill_rect(476, 664, 14, 34, GREY)
    c.hline(400, 698, 94, GREY, 1)
    c.text(MX, 684, "RUSSIAN STRIKE HITS", 3, INK)
    c.text(MX, 710, "APARTMENT BLOCK", 3, INK)
    c.text(MX, 736, "2 DEAD, 40 WOUNDED", 3, INK)
    c.text(MX, 772, "FOUR OF THE WOUNDED ARE", 2, INK)
    c.text(MX, 790, "CHILDREN, THE GOVERNOR SAID.", 2, INK)
    c.text(MX, 808, "THE ATTACK STRUCK OVERNIGHT. - AP", 2, INK)

    c.vline(512, 648, 208, GREY, 1)

    c.text(526, 656, "CLIMATE - ANTALYA, TURKIYE", 2, RED)
    # Sun illustration.
    c.disc(940, 676, 20, GOLD)
    c.line(940, 648, 940, 642, GOLD, 2)
    c.line(940, 704, 940, 710, GOLD, 2)
    c.line(912, 676, 906, 676, GOLD, 2)
    c.line(968, 676, 974, 676, GOLD, 2)
    c.text(526, 684, "COP31 ENDS WITH", 3, INK)
    c.text(526, 710, "NO DEAL AT ALL", 3, INK)
    c.text(526, 736, "FIRST SINCE 2009", 3, INK)
    c.text(526, 772, "TALKS ENDED ON SUNDAY AFTER", 2, INK)
    c.text(526, 790, "THE EU REJECTED A TEXT WITH", 2, INK)
    c.text(526, 808, "NO MENTION OF FOSSIL FUELS. - REUTERS", 2, INK)

    c.hline(MX, 864, RX - MX, INK, 4)
    c.hline(MX, 870, RX - MX, RED, 2)

    # ---- Bottom strip: four short items, one big number each ----
    for dx in (260, 504, 748):
        c.vline(dx, 878, 120, GREY, 1)

    c.text(MX, 880, "US ECONOMY", 2, RED)
    c.text(MX, 900, "103.3", 4, INK)
    c.text(MX, 934, "CONSUMER", 2, INK)
    c.text(MX, 951, "CONFIDENCE", 2, INK)
    c.text(MX, 968, "HIGHEST SINCE", 2, INK)
    c.text(MX, 985, "JAN 2025", 2, INK)

    c.text(272, 880, "TRADE - WASHINGTON", 2, RED)
    c.text(272, 900, "16", 4, INK)
    c.text(272, 934, "NEW TARIFFS", 2, INK)
    c.text(272, 951, "EXPECTED AS", 2, INK)
    c.text(272, 968, "SECTION 301", 2, INK)
    c.text(272, 985, "PROBE REPORTS", 2, INK)

    c.text(516, 880, "MIGRATION - SENEGAL", 2, RED)
    c.text(516, 900, "175", 4, INK)
    c.text(516, 934, "MIGRANTS", 2, INK)
    c.text(516, 951, "MISSING AFTER", 2, INK)
    c.text(516, 968, "DAKAR BOAT", 2, INK)
    c.text(516, 985, "LOSES CONTACT", 2, INK)

    c.text(760, 880, "HEALTH - CONGO", 2, RED)
    c.text(760, 900, "24H", 4, INK)
    c.text(760, 934, "EBOLA TEAMS", 2, INK)
    c.text(760, 951, "TRAPPED BY", 2, INK)
    c.text(760, 968, "FIGHTING IN", 2, INK)
    c.text(760, 985, "ITURI - WHO", 2, INK)

    # ---- Footer: sources ----
    c.centered(1006, "SOURCES: REUTERS - AP - SANOFI - CONFERENCE BOARD - UN NEWS - WHO", 2, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), build_page())


if __name__ == "__main__":
    main()
