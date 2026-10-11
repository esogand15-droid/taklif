"""Configuration for the handwritten assignment pages."""
import os

# Paths
BASE_DIR = '/home/user/taklif'
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
FONT_PATH = os.path.join(FONTS_DIR, 'Vazirmatn-Medium.ttf')
FONT_BOLD_PATH = os.path.join(FONTS_DIR, 'Vazirmatn-Bold.ttf')

# A4 dimensions at 300 DPI
A4_WIDTH = 2480   # pixels
A4_HEIGHT = 3508  # pixels

# Margins (in pixels)
MARGIN_RIGHT = 200
MARGIN_LEFT = 200
MARGIN_TOP = 180
MARGIN_BOTTOM = 180

# Text area
TEXT_WIDTH = A4_WIDTH - MARGIN_RIGHT - MARGIN_LEFT
TEXT_HEIGHT = A4_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

# Font sizes
FONT_SIZE_BODY = 44
FONT_SIZE_TITLE = 56
FONT_SIZE_SUBTITLE = 48
FONT_SIZE_HEADER = 52

# Line spacing
LINE_SPACING = 1.75

# Blue ink color (natural ballpoint pen blue)
INK_COLOR = (10, 40, 160)  # Deep blue
INK_COLOR_LIGHT = (30, 60, 170)  # Slightly lighter for variation

# Paper color
PAPER_COLOR = (252, 250, 245)  # Warm white

# Output file names
PAGE_FILES = [
    'page_01.png',
    'page_02.png',
    'page_03.png',
    'page_04.png',
]