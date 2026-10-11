#!/usr/bin/env python3
"""
Ultimate Persian Handwriting Simulator
Uses Mikhak-DS1-FD font with per-line rendering, heavy variations,
and aggressive ink/paper effects for the most realistic look possible.
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
M_R, M_L, M_T, M_B = 260, 260, 240, 240
TEXT_W = W - M_R - M_L

# Base font sizes
FS_BODY = 46
FS_TITLE = 58
FS_SUBTITLE = 52
FS_HEADER = 54

# Line spacing
LINE_H_FACTOR = 1.68

# Ink colors - blue ballpoint pen
INK_BASE = (10, 32, 152)
PAPER_BASE = (252, 250, 245)
PAPER_LINES = (228, 225, 218)


def get_ink_color():
    """Get varied blue ink color."""
    base = INK_BASE
    r = max(0, min(255, base[0] + random.randint(-5, 5)))
    g = max(0, min(255, base[1] + random.randint(-5, 5)))
    b = max(0, min(255, base[2] + random.randint(-6, 6)))
    return (r, g, b)


def reshape_persian(text):
    """Reshape and reorder Persian text."""
    if not text or not text.strip():
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def get_font(size, bold=False):
    """Get Mikhak-DS1-FD font."""
    if bold:
        path = os.path.join(FONTS_DIR, 'Mikhak-DS1-FD-Bold.ttf')
    else:
        path = os.path.join(FONTS_DIR, 'Mikhak-DS1-FD-Medium.ttf')
    return ImageFont.truetype(path, size)


def create_paper_background():
    """Create realistic paper background."""
    img = Image.new('RGB', (W, H), PAPER_BASE)
    draw = ImageDraw.Draw(img)
    
    random.seed(42)
    
    # Paper texture noise
    for _ in range(40000):
        x = random.randint(0, W-1)
        y = random.randint(0, H-1)
        shade = random.randint(246, 255)
        draw.point((x, y), fill=(shade, max(0, shade-2), max(0, shade-5)))
    
    # Ruled lines with natural waviness
    line_spacing = int(FS_BODY * LINE_H_FACTOR)
    start_y = M_T + 80
    
    for y_line in range(start_y, H - M_B, line_spacing):
        points = []
        phase = random.uniform(0, 2 * math.pi)
        amp = random.uniform(0.4, 1.0)
        freq = random.uniform(0.002, 0.005)
        
        for x in range(M_L - 30, W - M_R + 30, 3):
            wave = math.sin(x * freq + phase) * amp
            points.append((x, y_line + wave))
        
        if len(points) > 1:
            draw.line(points, fill=PAPER_LINES, width=1)
    
    # Red margin line
    margin_x = W - M_R + 50
    for y in range(M_T - 40, H - M_B + 40, 2):
        draw.point((int(margin_x + random.uniform(-0.5, 0.5)), y), fill=(215, 170, 170))
    
    return img


def render_line_to_image(text, font, color):
    """Render a single line of text to a transparent image."""
    display_text = reshape_persian(text)
    
    # Get text size
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Create image with padding
    padding = 30
    line_img = Image.new('RGBA', (tw + padding*2, th + padding*2), (0, 0, 0, 0))
    line_draw = ImageDraw.Draw(line_img)
    
    # Draw text
    line_draw.text((padding, padding), display_text, font=font, fill=color + (255,))
    
    return line_img, tw + padding*2, th + padding*2


def apply_line_transformations(line_img, rotation=0, scale=1.0):
    """Apply per-line transformations."""
    # Apply rotation
    if abs(rotation) > 0.01:
        line_img = line_img.rotate(rotation, expand=True, resample=Image.BICUBIC, 
                                    fillcolor=(0, 0, 0, 0))
    
    # Apply scale variation
    if abs(scale - 1.0) > 0.01:
        new_w = max(1, int(line_img.width * scale))
        new_h = max(1, int(line_img.height * scale))
        line_img = line_img.resize((new_w, new_h), Image.LANCZOS)
    
    return line_img


def composite_line_on_paper(paper, line_img, x, y):
    """Composite a rendered line onto the paper image."""
    x = max(0, min(paper.width - line_img.width, int(x)))
    y = max(0, min(paper.height - line_img.height, int(y)))
    
    region = paper.crop((x, y, x + line_img.width, y + line_img.height))
    composite = Image.alpha_composite(region.convert('RGBA'), line_img)
    paper.paste(composite.convert('RGB'), (x, y))
    
    return paper


def add_ink_effects(img):
    """Add ink bleeding and pressure effects."""
    blurred = img.filter(ImageFilter.GaussianBlur(radius=0.4))
    result = Image.blend(img, blurred, 0.12)
    return result


def add_paper_effects(img):
    """Add paper grain and texture."""
    noise = Image.new('RGB', (W, H), (128, 128, 128))
    draw = ImageDraw.Draw(noise)
    
    random.seed(123)
    for _ in range(15000):
        x = random.randint(0, W-1)
        y = random.randint(0, H-1)
        shade = random.randint(118, 138)
        draw.point((x, y), fill=(shade, shade, shade))
    
    noise = noise.filter(ImageFilter.GaussianBlur(radius=0.3))
    result = ImageChops.multiply(img, noise)
    result = ImageEnhance.Brightness(result).enhance(1.02)
    
    return result


def add_final_effects(img):
    """Apply final post-processing effects."""
    # Slight rotation
    angle = random.uniform(-0.12, 0.12)
    img = img.rotate(angle, fillcolor=PAPER_BASE, expand=False)
    
    # Ink effects
    img = add_ink_effects(img)
    
    # Paper texture
    img = add_paper_effects(img)
    
    return img


def draw_page_number(draw, page_num):
    """Draw page number."""
    font = get_font(34)
    persian_nums = {'1': '۱', '2': '۲', '3': '۳', '4': '۴'}
    pn = persian_nums.get(str(page_num), str(page_num))
    text = f"— {pn} —"
    display_text = reshape_persian(text)
    bbox = draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, H - M_B + 60), display_text, font=font, fill=(110, 105, 95))


def wrap_text_persian(text, font, max_width, draw):
    """Wrap Persian text."""
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


def render_page(content_lines, page_num, has_bismillah=False):
    """Render a complete A4 page with handwriting simulation."""
    img = create_paper_background()
    
    y = M_T
    line_h = int(FS_BODY * LINE_H_FACTOR)
    
    # بسم الله
    if has_bismillah:
        font_bism = get_font(FS_TITLE + 4, bold=True)
        text = reshape_persian("به نام خدا")
        temp_draw = ImageDraw.Draw(img)
        bbox = temp_draw.textbbox((0, 0), text, font=font_bism)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        
        # Render with per-line variation
        line_img, _, _ = render_line_to_image("به نام خدا", font_bism, get_ink_color())
        line_img = apply_line_transformations(line_img, 
                                               rotation=random.uniform(-0.3, 0.3),
                                               scale=random.uniform(0.98, 1.02))
        img = composite_line_on_paper(img, line_img, 
                                       x + random.uniform(-2, 2), 
                                       y + random.uniform(-1, 1))
        y += int(FS_TITLE * 2.5)
    
    temp_draw = ImageDraw.Draw(img)
    
    for line_info in content_lines:
        text = line_info.get('text', '')
        style = line_info.get('style', 'body')
        space_after = line_info.get('space_after', 0)
        
        if not text.strip():
            y += space_after if space_after else line_h // 2
            continue
        
        # Determine font and wrapping
        if style == 'title':
            font = get_font(FS_TITLE, bold=True)
            wrapped = [text]
            indent = 0
        elif style == 'subtitle':
            font = get_font(FS_SUBTITLE, bold=True)
            wrapped = wrap_text_persian(text, font, TEXT_W, temp_draw)
            indent = 0
        elif style == 'header':
            font = get_font(FS_HEADER, bold=True)
            wrapped = wrap_text_persian(text, font, TEXT_W, temp_draw)
            indent = 0
        elif style == 'verse':
            font = get_font(FS_BODY + 4)
            wrapped = wrap_text_persian(text, font, TEXT_W - 140, temp_draw)
            indent = 120
        else:  # body
            font = get_font(FS_BODY)
            wrapped = wrap_text_persian(text, font, TEXT_W, temp_draw)
            indent = 0
        
        for wline in wrapped:
            display_text = reshape_persian(wline)
            bbox = temp_draw.textbbox((0, 0), display_text, font=font)
            tw = bbox[2] - bbox[0]
            
            # Calculate x position
            if style == 'title':
                text_x = (W - tw) // 2
            else:
                text_x = W - M_R - tw - indent
            
            # Per-line variations
            rotation = random.uniform(-0.4, 0.4)
            scale = random.uniform(0.97, 1.03)
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-2, 2)
            
            # Render line with transformations
            line_img, _, _ = render_line_to_image(wline, font, get_ink_color())
            line_img = apply_line_transformations(line_img, rotation=rotation, scale=scale)
            
            # Composite onto paper
            img = composite_line_on_paper(img, line_img, 
                                           text_x + offset_x, 
                                           y + offset_y)
            
            # Advance y position
            y += int(font.size * LINE_H_FACTOR) + random.uniform(-1.5, 1.5)
        
        if space_after:
            y += space_after
    
    # Page number
    draw = ImageDraw.Draw(img)
    draw_page_number(draw, page_num)
    
    # Final effects
    img = add_final_effects(img)
    
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
    """Generate all 4 pages."""
    print("Generating handwritten pages with Mikhak-DS1-FD font and per-line rendering...")
    
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
    
    print("\nAll 4 pages generated!")


if __name__ == '__main__':
    main()