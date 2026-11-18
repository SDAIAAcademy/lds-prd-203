"""Figures quoted on the slides that do not come from a lab file.

Run:  uv run labs/_tools/slide_figures.py
Prints the contrast ratios, the Wilson intervals and the problem-discovery shares used in
slides/day3.html and slides/capstone.html, so every number on a slide has a calculation behind it.
Standard library only.
"""
import math


def luminance(hex_colour):
    out = []
    for i in (1, 3, 5):
        v = int(hex_colour[i:i + 2], 16) / 255
        out.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    r, g, b = out
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


def found(share_per_user, users):
    """Nielsen (2000): share of problems found by n users = 1 - (1 - L)^n."""
    return 100 * (1 - (1 - share_per_user) ** users)


if __name__ == '__main__':
    # Day 3, session 1: parallel example (the contractor portal), not the Sayyib prototype
    for colour in ('#999999', '#767676'):
        print(f'contrast {colour} on #ffffff: {contrast(colour, "#ffffff"):.2f}:1')
    # Day 3, session 4: parallel example, 6 successes in 10 attempts
    lo, hi = wilson(6, 10)
    print(f'Wilson 95% for 6/10: {lo:.0f}% to {hi:.0f}%')
    # Nielsen's figure: L = 31%
    for n in (1, 5, 15):
        print(f'problems found by {n} users at L=0.31: {found(0.31, n):.1f}%')
