#!/usr/bin/env python3
"""Generate the site favicon from The Courier relic art.

The icon is a stylized portrait of the Slay the Spire 2 relic "The Courier":
the mouse flattened to a single dark teal, with its ear, eye and satchel punched
out in accent colours and a dark keyline around each shape, framed in a circle
centred on the head. The source illustration (vendored in icon-src/, fetched
from the Spire Codex API this project already uses for card metadata) is used
only as a mask -- none of its original colouring survives into the icon.

Outputs, all written next to this script:
  favicon-32.png / favicon-180.png  browser + iOS home screen
  favicon.ico                       16-256px, for Safari and older browsers

Run after changing any constant here:  python3 frontend/build_favicon.py
"""
import colorsys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

FRONTEND = Path(__file__).resolve().parent
SOURCE_ART = FRONTEND / "icon-src" / "the_courier.webp"

# --- palette -----------------------------------------------------------------
BODY = "#0f2e33"      # dark teal silhouette
GOLD = "#f2c33d"      # eye and courier satchel
EAR = "#f2a7b8"       # warm rose, echoing the relic's pink ear
BACKDROP = "#cdece4"  # pale mint
KEYLINE = "#08171a"   # near-black, tinted cool to sit with the teal

# --- framing -----------------------------------------------------------------
# The crop is a circle centred on the head rather than the whole animal: at tab
# sizes the full body wastes most of the frame on the tail and haunches. Centre
# and radius are in source-image pixels. The circle deliberately overruns the
# source canvas -- the backdrop fills wherever it does.
HEAD_CENTRE = (94, 106)
HEAD_RADIUS = 130
HEAD_RISE = 28        # shifts the crop up so the head sits centred, not low

# The tail sweeps up the right-hand side and re-enters the circle as a stray
# fragment disconnected from the body, so it is cleared before masking.
TAIL_COLUMN_X = 196
TAIL_COLUMN_BOTTOM = 150

# --- rendering ---------------------------------------------------------------
# Masks are built at WORK resolution so dilation and blur have room to resolve,
# then downsampled; this is what keeps the edges smooth at icon sizes.
WORK = 1024
CANVAS = 512

# The source art is drawn with a soft feathered edge. Below this alpha is
# feather, not mouse -- keeping it leaves a grey halo once the body is flattened
# to one colour.
ALPHA_CUTOFF = 170
BODY_THICKEN = 2      # source pixels; keeps ears and snout alive when downscaled
OUTER_KEYLINE = 10    # WORK-resolution px
ACCENT_KEYLINE = 6

ICO_SIZES = [16, 32, 48, 64, 128, 256]
APPLE_TOUCH_SIZE = 180
STANDARD_PNG_SIZE = 32


def _hsv_mask(art, test):
    """Binary mask of opaque pixels whose HSV satisfies `test`.

    Selecting by hue rather than hand-placed coordinates keeps the accent shapes
    faithful to the illustration.
    """
    px = art.load()
    mask = Image.new("L", art.size, 0)
    mp = mask.load()
    for y in range(art.height):
        for x in range(art.width):
            r, g, b, a = px[x, y]
            if a < ALPHA_CUTOFF:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if test(h, s, v):
                mp[x, y] = 255
    return mask


def _is_eye(h, s, v):
    return 0.13 < h < 0.20 and s > 0.6 and v > 0.6


def _is_satchel(h, s, v):
    return 0.10 < h < 0.19 and 0.25 < s < 0.75 and 0.45 < v < 0.85


def _is_pink(h, s, v):
    return (h < 0.06 or h > 0.92) and s > 0.10 and v > 0.60


def _largest_blob(mask):
    """Keep only the largest connected component of a mask.

    The pink hue range matches the ear, the tail and the nose tip. The ear is
    comfortably the largest of the three, so this isolates it without resorting
    to hand-placed coordinates that would break if the art were replaced.
    """
    width, height = mask.size
    src = mask.load()
    visited = [[False] * height for _ in range(width)]
    best = []
    for y in range(height):
        for x in range(width):
            if visited[x][y] or not src[x, y]:
                continue
            queue = deque([(x, y)])
            visited[x][y] = True
            blob = []
            while queue:
                cx, cy = queue.popleft()
                blob.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                               (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < width and 0 <= ny < height and not visited[nx][ny] and src[nx, ny]:
                        visited[nx][ny] = True
                        queue.append((nx, ny))
            if len(blob) > len(best):
                best = blob
    out = Image.new("L", mask.size, 0)
    op = out.load()
    for point in best:
        op[point] = 255
    return out


def _resolve(mask, blur=1.6):
    """Upscale to WORK, blur, and re-threshold at the midpoint.

    Rounds off the source's pixel-stair edges while keeping the boundary hard --
    blurring without re-thresholding would reintroduce the halo the alpha cutoff
    exists to remove.
    """
    big = mask.resize((WORK, WORK), Image.LANCZOS).filter(ImageFilter.GaussianBlur(blur))
    return big.point(lambda a: 255 if a >= 128 else 0)


def _antialias(mask, blur=1.1):
    """Final feather for smooth edges, applied to an already-clean boundary."""
    return mask.filter(ImageFilter.GaussianBlur(blur))


def _dilate(mask, radius):
    """Grow a mask by `radius` px. MaxFilter caps at radius 5, so step up."""
    remaining = radius
    while remaining > 0:
        step = min(5, remaining)
        mask = mask.filter(ImageFilter.MaxFilter(step * 2 + 1))
        remaining -= step
    return mask


def _fill(mask, colour):
    layer = Image.new("RGBA", (WORK, WORK), colour)
    layer.putalpha(mask)
    return layer


def _frame_head():
    """Re-centre the source art so the head circle fills a square frame."""
    centre_x, centre_y = HEAD_CENTRE
    side = HEAD_RADIUS * 2
    frame = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    frame.alpha_composite(
        Image.open(SOURCE_ART).convert("RGBA"),
        (HEAD_RADIUS - centre_x, HEAD_RADIUS - centre_y + HEAD_RISE),
    )
    return frame, side


def render_icon():
    """Compose the full-resolution icon."""
    frame, side = _frame_head()
    centre_x, centre_y = HEAD_CENTRE

    body = frame.split()[-1].point(lambda a: 255 if a >= ALPHA_CUTOFF else 0)
    tail_x = HEAD_RADIUS - centre_x + TAIL_COLUMN_X
    if 0 <= tail_x < side:
        tail_bottom = HEAD_RADIUS - centre_y + HEAD_RISE + TAIL_COLUMN_BOTTOM
        ImageDraw.Draw(body).rectangle([(tail_x, 0), (side, min(side, tail_bottom))], fill=0)

    body = _resolve(body.filter(ImageFilter.MaxFilter(BODY_THICKEN * 2 + 1)))
    ear = _resolve(_largest_blob(_hsv_mask(frame, _is_pink)), blur=1.2)
    satchel = _resolve(_hsv_mask(frame, _is_satchel), blur=1.2)
    eye = _resolve(_hsv_mask(frame, _is_eye), blur=1.2)

    figure = Image.new("RGBA", (WORK, WORK), (0, 0, 0, 0))
    # Each shape is laid down as a dilated keyline first, then its fill on top,
    # so only the ring shows. Accents sit inside the body silhouette, so their
    # keylines read as internal outlines rather than an outer border.
    for mask, colour, keyline in (
        (body, BODY, OUTER_KEYLINE),
        (ear, EAR, ACCENT_KEYLINE),
        (satchel, GOLD, ACCENT_KEYLINE),
        (eye, GOLD, max(2, ACCENT_KEYLINE // 2)),
    ):
        figure.alpha_composite(_fill(_antialias(_dilate(mask, keyline)), KEYLINE))
        figure.alpha_composite(_fill(_antialias(mask), colour))

    figure = figure.resize((CANVAS, CANVAS), Image.LANCZOS)

    disc = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(disc).ellipse([(0, 0), (CANVAS - 1, CANVAS - 1)], fill=255)

    icon = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    icon.paste(Image.new("RGBA", (CANVAS, CANVAS), BACKDROP), (0, 0), disc)
    icon.alpha_composite(
        Image.composite(figure, Image.new("RGBA", figure.size, (0, 0, 0, 0)), disc)
    )
    return icon


def main():
    icon = render_icon()

    standard = FRONTEND / f"favicon-{STANDARD_PNG_SIZE}.png"
    icon.resize((STANDARD_PNG_SIZE,) * 2, Image.LANCZOS).save(standard)
    print(f"wrote {standard.name}")

    # iOS ignores transparency-friendly formats and composites against black,
    # so the home-screen icon is flattened onto the backdrop colour.
    apple = Image.new("RGB", (APPLE_TOUCH_SIZE,) * 2, BACKDROP)
    scaled = icon.resize((APPLE_TOUCH_SIZE,) * 2, Image.LANCZOS)
    apple.paste(scaled, mask=scaled.split()[-1])
    apple.save(FRONTEND / f"favicon-{APPLE_TOUCH_SIZE}.png")
    print(f"wrote favicon-{APPLE_TOUCH_SIZE}.png")

    ico = FRONTEND / "favicon.ico"
    icon.resize((max(ICO_SIZES),) * 2, Image.LANCZOS).save(
        ico, format="ICO", sizes=[(s, s) for s in ICO_SIZES]
    )
    print(f"wrote {ico.name} at sizes {ICO_SIZES}")


if __name__ == "__main__":
    main()
