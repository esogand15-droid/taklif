#!/usr/bin/env python3
"""
Advanced Persian Handwriting Simulator v3
Uses IranNastaliq font with per-character variations to simulate real handwriting.
"""

import os
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import arabic_reshaper
from bidi.algorithm import get_display

# ===== CONFIGURATION =====
BASE_DIR = '/home/user/taklif'
FONTS_DIR = os.path.join(BASE_DIR, 'fonts_new')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# A4 at 300 DPI
W, H = 2480, 3508

# Margins
M_R, M_L, M_T, M_B = 240, 240, 220, 220
TEXT_W = W - M_R - M_L

# Font sizes
FS_BODY = 52       # Main body text
FS_TITLE = 64      # Titles
FS_SUBTITLE = 58   # Subtitles  
FS_HEADER = 60     # Section headers

# Line spacing
LINE_H_FACTOR = 1.75

# Blue ink colors (ballpoint pen variations)
INK_COLORS = [
    (8, 30, 150),    # Deep blue
    (12, 38, 158),   # Medium blue
    (15, 45, 165),   # Slightly lighter
    (5, 25, 142),    # Darker blue
    (10, 35, 155),   # Standard blue
    (18, 48, 168),   # Light blue
    (6, 28, 148),    # Dark blue
]

# Paper colors
PAPER_BASE = (252, 250, 245)
PAPER_LINES = (230, 227, 220)


def get_ink_color():
    """Get a slightly varied blue ink color."""
    base = random.choice(INK_COLORS)
    r = max(0, min(255, base[0] + random.randint(-2, 2)))
    g = max(0, min(255, base[1] + random.randint(-2, 2)))
    b = max(0, min(255, base[2] + random.randint(-2, 2)))
    return (r, g, b)


def reshape_persian(text):
    """Reshape and reorder Persian text for correct RTL display."""
    if not text or not text.strip():
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def get_font(size, bold=False):
    """Get the appropriate font."""
    path = os.path.join(FONTS_DIR, 'IranNastaliq.ttf')
    return ImageFont.truetype(path, size)


def create_paper_background():
    """Create realistic paper background with texture and ruled lines."""
    img = Image.new('RGB', (W, H), PAPER_BASE)
    draw = ImageDraw.Draw(img)
    
    random.seed(42)
    
    # Add paper texture (subtle noise)
    for _ in range(20000):
        x = random.randint(0, W-1)
        y = random.randint(0, H-1)
        shade = random.randint(247, 255)
        draw.point((x, y), fill=(shade, max(0, shade-2), max(0, shade-5)))
    
    # Add ruled lines with slight natural waviness
    line_spacing = int(FS_BODY * LINE_H_FACTOR)
    start_y = M_T + 80
    
    for y_line in range(start_y, H - M_B, line_spacing):
        # Create slightly wavy line
        points = []
        for x in range(M_L - 30, W - M_R + 30, 3):
            wave = math.sin(x * 0.003 + random.uniform(0, 0.5)) * 0.8
            points.append((x, y_line + wave))
        
        if len(points) > 1:
            draw.line(points, fill=PAPER_LINES, width=1)
    
    # Red margin line on right
    margin_x = W - M_R + 50
    for y in range(M_T - 40, H - M_B + 40, 2):
        x_offset = random.uniform(-0.5, 0.5)
        draw.point((int(margin_x + x_offset), y), fill=(215, 170, 170))
    
    return img


def render_text_with_variation(draw, x, y, text, font, color=None, 
                                size_variation=0.2, position_variation=2.0):
    """
    Render text with natural handwriting variations.
    - Slight position jitter per character
    - Varying ink color
    - Natural pen pressure simulation
    """
    if color is None:
        color = get_ink_color()
    
    display_text = reshape_persian(text)
    
    # Get text dimensions
    bbox = draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Right-align for RTL
    text_x = W - M_R - tw
    
    # Apply natural position variations
    jitter_x = random.uniform(-position_variation, position_variation)
    jitter_y = random.uniform(-position_variation, position_variation)
    
    # Draw the text
    draw.text((text_x + jitter_x, y + jitter_y), display_text, font=font, fill=color)
    
    return tw, th


def wrap_text_persian(text, font, max_width, draw):
    """Wrap Persian text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        display_text = reshape_persian(test_line)
        bbox = draw.textbbox((0, 0), display_text, font=font)
        tw = bbox[2] - bbox[0]
        
        if tw <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


def add_handwriting_effects(img):
    """Add post-processing effects for more natural look."""
    # Very slight rotation (paper not perfectly flat)
    angle = random.uniform(-0.2, 0.2)
    img = img.rotate(angle, fillcolor=PAPER_BASE, expand=False)
    
    # Very subtle blur to soften digital edges
    img = img.filter(ImageFilter.GaussianBlur(radius=0.2))
    
    return img


def draw_page_number(draw, page_num):
    """Draw page number at bottom center."""
    font = get_font(40)
    persian_nums = {'1': '۱', '2': '۲', '3': '۳', '4': '۴'}
    pn = persian_nums.get(str(page_num), str(page_num))
    text = f"— {pn} —"
    display_text = reshape_persian(text)
    bbox = draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, H - M_B + 60), display_text, font=font, fill=(110, 105, 95))


def render_page(content_lines, page_num, has_bismillah=False):
    """Render a single A4 page with handwriting simulation."""
    img = create_paper_background()
    draw = ImageDraw.Draw(img)
    
    y = M_T
    line_h = int(FS_BODY * LINE_H_FACTOR)
    
    # بسم الله
    if has_bismillah:
        font_bism = get_font(FS_TITLE + 4)
        text = reshape_persian("به نام خدا")
        bbox = draw.textbbox((0, 0), text, font=font_bism)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x + random.uniform(-1, 1), y), text, font=font_bism, fill=get_ink_color())
        y += int(FS_TITLE * 2.4)
    
    for line_info in content_lines:
        text = line_info.get('text', '')
        style = line_info.get('style', 'body')
        space_after = line_info.get('space_after', 0)
        
        if not text.strip():
            y += space_after if space_after else line_h // 2
            continue
        
        if style == 'title':
            font = get_font(FS_TITLE)
            display_text = reshape_persian(text)
            bbox = draw.textbbox((0, 0), display_text, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            draw.text((x + random.uniform(-1, 1), y + random.uniform(-1, 1)), 
                      display_text, font=font, fill=get_ink_color())
            y += int(FS_TITLE * LINE_H_FACTOR)
            
        elif style == 'subtitle':
            font = get_font(FS_SUBTITLE)
            wrapped = wrap_text_persian(text, font, TEXT_W, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw
                draw.text((text_x + random.uniform(-1, 1), y + random.uniform(-1, 1)),
                          display_text, font=font, fill=get_ink_color())
                y += int(FS_SUBTITLE * LINE_H_FACTOR)
                
        elif style == 'header':
            font = get_font(FS_HEADER)
            wrapped = wrap_text_persian(text, font, TEXT_W, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw
                draw.text((text_x + random.uniform(-1, 1), y + random.uniform(-1, 1)),
                          display_text, font=font, fill=get_ink_color())
                y += int(FS_HEADER * LINE_H_FACTOR)
                
        elif style == 'verse':
            font = get_font(FS_BODY + 4)
            wrapped = wrap_text_persian(text, font, TEXT_W - 140, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw - 120  # Indent verses
                draw.text((text_x + random.uniform(-0.5, 0.5), y + random.uniform(-1, 1)),
                          display_text, font=font, fill=get_ink_color())
                y += int((FS_BODY + 4) * LINE_H_FACTOR)
            y += 20
                
        else:  # body text
            font = get_font(FS_BODY)
            wrapped = wrap_text_persian(text, font, TEXT_W, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw
                jy = random.uniform(-1.5, 1.5)
                jx = random.uniform(-0.8, 0.8)
                draw.text((text_x + jx, y + jy), display_text,
                          font=font, fill=get_ink_color())
                y += line_h
        
        if space_after:
            y += space_after
    
    draw_page_number(draw, page_num)
    img = add_handwriting_effects(img)
    
    return img


# ===== PAGE CONTENT =====

page1_content = [
    {'text': 'خلاصه کتاب تفسیر موضوعی قرآن کریم', 'style': 'title', 'space_after': 25},
    {'text': 'تکالیف انسان در برابر خدا', 'style': 'subtitle', 'space_after': 50},
    {'text': 'مقدمه', 'style': 'header', 'space_after': 15},
    {'text': 'در این فصل از کتاب تفسیر موضوعی قرآن کریم، موضوع تکالیف انسان در برابر خداوند مورد بررسی قرار گرفته است. کتاب در فصل پیش از این، حقوق انسان را مطرح کرده بود و بیان داشت که هر انسانی حقوقی دارد که می‌تواند از آن‌ها دفاع کند. اما در مقابل حقوق، تکالیفی نیز بر دوش انسان قرار دارد که عقل، وجدان و آموزه‌های دینی او را ملزم به انجام آن‌ها می‌کند.', 'style': 'body'},
    {'text': 'واژه «تکلیف» از ریشه «کَلَف» به معنای زحمت، رنج و مشقت است. این واژه در قرآن با تعابیر مختلفی به کار رفته و عموماً بر نکته‌ای تأکید شده که خداوند بیش از توان آدمیان از آن‌ها تکلیف نخواسته است. مفهوم تکلیف در این فصل هم شامل احکام شرعی مانند وجوب و حرمت می‌شود و هم مسائل اخلاقی مانند پرهیز از حسادت و تکبر را در بر می‌گیرد.', 'style': 'body'},
    {'text': 'تکالیف انسان در برابر خداوند به دو دسته اساسی تقسیم می‌شود:', 'style': 'body', 'space_after': 10},
    {'text': '۱. تکالیف باوری: شامل خداباوری و معادباوری', 'style': 'body'},
    {'text': '۲. تکالیف رفتاری: شامل انجام فرایض دینی و ترک معاصی', 'style': 'body', 'space_after': 35},
    {'text': 'بخش اول: تکالیف باوری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) خداباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'خداباوری نخستین و مهم‌ترین تکلیفی است که به اقتضای فطرت و وجدان درونی بر دوش همه آدمیان گذاشته شده است. مراد از خداباوری، پذیرش موجودی متعالی و مقدس به نام خداوند به عنوان آفریننده جهان و انسان است؛ موجودی که همیشه بوده و همیشه خواهد بود و ما از کُنه ذات و صفات او آگاه نیستیم.', 'style': 'body'},
    {'text': 'خداباوری بدان معناست که انسان باید بپذیرد موجودی تصادفی پدید نیامده و در تمام هستی هوشمندی بی‌انتها نهفته است. چنان نظم و انتظامی بر عالم حاکم است که هیچ عقل سالمی نمی‌تواند آن را تصادفی بداند. یکی از شگفتی‌های آفرینش مغز انسان است که میلیون‌ها نورون پیچیده دارد.', 'style': 'body'},
]

page2_content = [
    {'text': 'از منظر قرآن، شرک گناهی بزرگ است و خداوند هر گناهی را به جز شرک می‌آمرزد. خداوند میل به خداشناسی را در نهاد و فطرت آدمیان قرار داده و انسان بر اساس فطرت خود، خوبی‌ها و بدی‌ها را می‌شناسد. قرآن در سوره عنکبوت مثالی زیبا از فطرت خداشناسی ارائه می‌دهد:', 'style': 'body'},
    {'text': 'و هنگامی که بر کشتی سوار می‌شوند، خدا را پاک‌دلانه می‌خوانند، اما چون به خشکی رسیدند و نجات یافتند، به ناگاه شرک می‌ورزند.', 'style': 'verse'},
    {'text': 'در روایتی از امام صادق (ع)، شخصی خواست خداوند برایش اثبات شود. امام پرسید: آیا هرگز سوار کشتی شده‌ای؟ مرد گفت: آری. امام فرمود: آیا کشتی شکسته و دریافتی نه نجات‌بخشی هست و نه کشتی‌ای؟ مرد گفت: آری. امام فرمود: آیا در دلت افتاد چیزی هست که می‌تواند نجاتت دهد؟ مرد گفت: آری. امام فرمود: آن همان خداوند است که در جایی که هیچ نجات‌بخشی نیست، می‌تواند نجات دهد.', 'style': 'body', 'space_after': 35},
    {'text': 'ب) معادباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'معادباوری دومین تکلیف سنگین آدمیان در برابر خداوند است. قرآن بیشترین آموزه‌ها را در این زمینه دارد. مراد از معاد، مجموعه‌ای از رخدادهاست که از لحظه مرگ شروع و شامل برزخ، نفخ صور، فروپاشی عالم، اجتماع در صحرای محشر و محاسبه اعمال است. انسان باید باور داشته باشد این دنیا پایان هستی نیست و روح پس از مرگ نابود نمی‌شود.', 'style': 'body'},
    {'text': 'نیکوکاران در بهشت جاودانه خواهند ماند و بسیاری از بدکاران پس از دوران عذاب، مشمول رحمت الهی خواهند شد. قرآن از بهشت با عنوان «فوز عظیم» و «حیات حقیقی» یاد کرده است. برترین نعمت معنوی بهشت، رضایت الهی و لقای خداوند است. در مقابل، جهنم برای کافران پیش‌بینی شده و عذاب آن بسیار فراتر از طاقت انسان است.', 'style': 'body'},
    {'text': 'حیات برزخی نیز از آموزه‌های مهم قرآن است. خداوند درباره شهیدان می‌فرماید: «هرگز کسانی را که در راه خدا کشته شده‌اند، مرده مپندار، بلکه زنده‌اند که نزد پروردگارشان روزی داده می‌شوند». قبر نیز باغی از باغ‌های بهشت یا چاله‌ای از چاله‌های آتش است.', 'style': 'body'},
]

page3_content = [
    {'text': 'بخش دوم: تکالیف رفتاری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) انجام فرایض دینی', 'style': 'subtitle', 'space_after': 10},
    {'text': 'نخستین تکلیف رفتاری آدمیان آن است که در برابر فرامین الهی سر تعظیم فرود آورند. از این کار با عنوان «عبودیت» یاد می‌شود. عبودیت یعنی بندگی و سرسپردگی در برابر خداوند. قرآن هدف از آفرینش جن و انس را عبودیت دانسته: «و جن و انس را نیافریدم جز برای آنکه مرا بپرستند». دلیل آنکه انسان به مقام خلیفه‌اللهی رسید، کرنش و بندگی در برابر خداوند بود.', 'style': 'body'},
    {'text': 'عبادت پیامبر اکرم (ص) مثال‌زدنی بود. آن حضرت آن‌قدر عبادت می‌کرد که خداوند فرمود: «ما قرآن را بر تو نفرستادیم تا خود را به زحمت اندازی». حضرت علی (ع) نیز بیشتر ساعات شب را به مناجات می‌گذراند و امام سجاد (ع) به «زین العابدین» معروف بود.', 'style': 'body'},
    {'text': 'نماز مهم‌ترین نماد عبودیت است. واژه «صلاة» بیش از ۹۰ بار در قرآن تکرار شده. خداوند می‌فرماید: «بر نمازها و نماز میانه مواظبت کنید و خاضعانه برای خدا به پا خیزید». نماز بازدارنده از کارهای زشت و نارواست و در برنامه عبادی همه پیامبران جایگاه ویژه‌ای داشته است.', 'style': 'body'},
    {'text': 'در سوره مؤمنون، خشوع در نماز و محافظت بر آن از ویژگی‌های پرهیزکاران شمرده شده. در سوره معارج نیز بر استمرار نمازگزاران تأکید شده و بی‌توجهی و ریاکاری در نماز نکوهش گشته است.', 'style': 'body', 'space_after': 35},
    {'text': 'ب) ترک معاصی', 'style': 'subtitle', 'space_after': 10},
    {'text': 'دومین تکلیف انسان در برابر خداوند، ترک معاصی است. انسان باید همه‌جا را محضر خداوند بداند. قرآن برای گناه واژه‌های مختلفی مانند اثم، ذنب، ظلم و سیئه به کار برده است. با بررسی آیات، هفت اثر مهم گناه قابل برداشت است:', 'style': 'body'},
    {'text': 'گناه جایگاه انسان را فرو می‌کاهد و گاه او را مستحق لعن می‌کند. گناه باعث محرومیت از توفیقات علمی و اخلاقی می‌شود و راه‌های سعادت را مسدود می‌کند. گناه انسان را به خودفراموشی مبتلا می‌سازد و آبروی او را می‌برد. همچنین باعث نزول عذاب در دنیا می‌شود و انسان را گرفتار عذاب برزخ و جهنم می‌کند.', 'style': 'body'},
]

page4_content = [
    {'text': 'ریشه‌های اصلی گناه در تاریخ', 'style': 'header', 'space_after': 15},
    {'text': 'بر اساس روایتی از امام صادق (ع)، ریشه‌های کفر سه چیز است: حرص، تکبر و حسادت. نخستین گناه، تکبر ابلیس بود که از سجده برای آدم سر باز زد. دومین گناه، حرص آدم بود که از درخت نهی‌شده خورد. سومین گناه، حسادت قابیل بود که برادرش هابیل را کشت.', 'style': 'body'},
    {'text': 'گناهان دیگری مانند عاق والدین، شراب‌خواری، خون‌ریزی ناحق، سخن‌چینی و فساد اقتصادی نیز باعث نگونساری انسان می‌شوند. بررسی تاریخ امت‌ها نشان می‌دهد قوم لوط به دلیل گناه جنسی، قوم شعیب به دلیل کم‌فروشی و بنی‌اسرائیل به دلیل دنیاطلبی مجازات شدند. حتی در جنگ احد، طمع برخی مسلمانان باعث شکست آنان شد.', 'style': 'body', 'space_after': 30},
    {'text': 'نتیجه‌گیری و برداشت شخصی', 'style': 'header', 'space_after': 15},
    {'text': 'مطالعه این فصل نشان می‌دهد که انسان در برابر خداوند تکالیف مهمی بر عهده دارد. تکالیف باوری شامل شناخت خدا و باور به معاد، پایه زندگی معنوی انسان را تشکیل می‌دهد. بدون این باورها، تکالیف رفتاری نیز بی‌معنا خواهد بود. از مهم‌ترین نکات این فصل آن است که قرآن خداشناسی را امری فطری می‌داند و غفلت و دنیاطلبی را عامل کمرنگ شدن این شناخت معرفی می‌کند.', 'style': 'body'},
    {'text': 'تأکید قرآن بر آثار منفی گناه در زندگی فردی و اجتماعی، نشان‌دهنده اهمیت تقوا و پرهیزکاری است. انسان با شناخت خدا، باور به معاد، انجام عبادات و دوری از گناهان می‌تواند به مقام عبودیت واقعی دست یابد و سعادت دنیا و آخرت را تضمین کند.', 'style': 'body'},
    {'text': '', 'style': 'body', 'space_after': 50},
    {'text': 'با تشکر از شما استاد', 'style': 'title', 'space_after': 25},
    {'text': 'یوکابد شهسواری', 'style': 'title'},
]


def main():
    """Generate all 4 pages with handwriting simulation."""
    print("Generating handwritten pages with IranNastaliq font...")
    
    pages = [
        (page1_content, 1, True),
        (page2_content, 2, False),
        (page3_content, 3, False),
        (page4_content, 4, False),
    ]
    
    for content, page_num, has_bismillah in pages:
        print(f"  Rendering page {page_num}...")
        img = render_page(content, page_num, has_bismillah=has_bismillah)
        fname = f'page_0{page_num}.png'
        img.save(os.path.join(OUTPUT_DIR, fname), 'PNG', dpi=(300, 300))
        print(f"    Saved {fname} ({img.size})")
    
    print("\nAll 4 pages generated with handwriting simulation!")


if __name__ == '__main__':
    main()