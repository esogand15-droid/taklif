#!/usr/bin/env python3
"""
Generate 4 handwritten-looking A4 pages for a Persian university assignment
about 'تفسیر موضوعی قرآن کریم - تکالیف انسان در برابر خدا'
"""

import os
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import arabic_reshaper
from bidi.algorithm import get_display

# ===== CONFIGURATION =====
BASE_DIR = '/home/user/taklif'
FONTS_DIR = os.path.join(BASE_DIR, 'fonts')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

FONT_PATH = os.path.join(FONTS_DIR, 'Vazirmatn-Medium.ttf')
FONT_BOLD_PATH = os.path.join(FONTS_DIR, 'Vazirmatn-Bold.ttf')

# A4 at 300 DPI
W, H = 2480, 3508

# Margins
M_R, M_L, M_T, M_B = 220, 220, 200, 200
TEXT_W = W - M_R - M_L

# Font sizes
FS_BODY = 42
FS_TITLE = 54
FS_SUBTITLE = 46
FS_HEADER = 50

# Line spacing factor
LINE_H_FACTOR = 1.70

# Colors
INK = (8, 35, 155)       # Ballpoint pen blue
INK_LIGHT = (25, 55, 165)
PAPER = (253, 251, 246)  # Warm white paper


def reshape_persian(text):
    """Reshape and reorder Persian text for correct RTL display."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def get_font(size, bold=False):
    """Load font at given size."""
    path = FONT_BOLD_PATH if bold else FONT_PATH
    return ImageFont.truetype(path, size)


def create_paper_bg():
    """Create A4 paper background with subtle texture."""
    img = Image.new('RGB', (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    
    # Add very subtle paper texture
    random.seed(42)
    for _ in range(8000):
        x = random.randint(0, W - 1)
        y = random.randint(0, H - 1)
        shade = random.randint(248, 255)
        draw.point((x, y), fill=(shade, shade - 2, shade - 5))
    
    # Add very faint horizontal line pattern (like notebook paper)
    for y_line in range(M_T + 80, H - M_B, int(FS_BODY * LINE_H_FACTOR)):
        draw.line([(M_L - 20, y_line), (W - M_R + 20, y_line)], 
                  fill=(235, 232, 225), width=1)
    
    # Add a red vertical margin line on the right
    draw.line([(W - M_R + 40, M_T - 30), (W - M_R + 40, H - M_B + 30)], 
              fill=(220, 180, 180), width=2)
    
    return img


def draw_text_line(draw, x, y, text, font, color=None, is_title=False):
    """Draw a single line of Persian text with slight natural variations."""
    if color is None:
        color = INK
    
    display_text = reshape_persian(text)
    
    # Get text dimensions
    bbox = draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # Right-align for RTL
    text_x = W - M_R - tw
    
    # Slight vertical jitter for handwriting feel
    jitter_y = random.uniform(-1.5, 1.5)
    jitter_x = random.uniform(-0.5, 0.5)
    
    draw.text((text_x + jitter_x, y + jitter_y), display_text, 
              font=font, fill=color)
    
    return th


def wrap_text(text, font, max_width, draw):
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


def add_natural_imperfections(img):
    """Add very subtle imperfections to simulate real paper."""
    # Very slight rotation (paper not perfectly aligned)
    angle = random.uniform(-0.3, 0.3)
    img = img.rotate(angle, fillcolor=PAPER, expand=False)
    
    return img


def add_correction_mark(draw, x, y, width, height):
    """Add a very subtle correction/scratch-out mark."""
    # Draw a slightly messy strikethrough
    points = []
    for i in range(int(width)):
        px = x + i
        py = y + height/2 + random.uniform(-3, 3)
        points.append((px, py))
    
    if len(points) > 1:
        draw.line(points, fill=INK_LIGHT, width=3)


def draw_page_number(draw, page_num):
    """Draw page number at bottom center."""
    font = get_font(36)
    text = f"— {page_num} —"
    display_text = reshape_persian(text)
    bbox = draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, H - M_B + 40), display_text, font=font, fill=INK_LIGHT)


def render_page(content_lines, page_num, has_title=False, has_bismillah=False, 
                has_footer=False, footer_name=None, has_thanks=False):
    """Render a single page with the given content."""
    img = create_paper_bg()
    draw = ImageDraw.Draw(img)
    
    y = M_T
    line_h = int(FS_BODY * LINE_H_FACTOR)
    
    # Draw "به نام خدا" if needed
    if has_bismillah:
        font_bismillah = get_font(FS_TITLE + 4, bold=True)
        text = reshape_persian("به نام خدا")
        bbox = draw.textbbox((0, 0), text, font=font_bismillah)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), text, font=font_bismillah, fill=INK)
        y += int(FS_TITLE * 2.2)
    
    # Process each content line
    for line_info in content_lines:
        text = line_info.get('text', '')
        style = line_info.get('style', 'body')
        space_after = line_info.get('space_after', 0)
        
        if not text.strip():
            y += space_after if space_after else line_h // 2
            continue
        
        if style == 'title':
            font = get_font(FS_TITLE, bold=True)
            display_text = reshape_persian(text)
            bbox = draw.textbbox((0, 0), display_text, font=font)
            tw = bbox[2] - bbox[0]
            x = (W - tw) // 2
            jitter = random.uniform(-1, 1)
            draw.text((x + jitter, y), display_text, font=font, fill=INK)
            y += int(FS_TITLE * LINE_H_FACTOR)
            
        elif style == 'subtitle':
            font = get_font(FS_SUBTITLE, bold=True)
            wrapped = wrap_text(text, font, TEXT_W, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw
                jitter = random.uniform(-1, 1)
                draw.text((text_x + jitter, y), display_text, font=font, fill=INK)
                y += int(FS_SUBTITLE * LINE_H_FACTOR)
                
        elif style == 'header':
            font = get_font(FS_HEADER, bold=True)
            wrapped = wrap_text(text, font, TEXT_W, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw
                jitter = random.uniform(-1, 1)
                draw.text((text_x + jitter, y), display_text, font=font, fill=INK)
                y += int(FS_HEADER * LINE_H_FACTOR)
                
        elif style == 'verse':
            font = get_font(FS_BODY + 2)
            wrapped = wrap_text(text, font, TEXT_W - 100, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw - 80  # Indent verses
                jitter = random.uniform(-1, 1)
                draw.text((text_x + jitter, y), display_text, font=font, fill=INK_LIGHT)
                y += int((FS_BODY + 2) * LINE_H_FACTOR)
            y += 10
                
        else:  # body text
            font = get_font(FS_BODY)
            wrapped = wrap_text(text, font, TEXT_W, draw)
            for wline in wrapped:
                display_text = reshape_persian(wline)
                bbox = draw.textbbox((0, 0), display_text, font=font)
                tw = bbox[2] - bbox[0]
                text_x = W - M_R - tw
                jitter_y = random.uniform(-1.5, 1.5)
                jitter_x = random.uniform(-0.5, 0.5)
                draw.text((text_x + jitter_x, y + jitter_y), display_text, 
                          font=font, fill=INK)
                y += line_h
        
        if space_after:
            y += space_after
    
    # Draw footer
    if has_thanks:
        y += 40
        font_thanks = get_font(FS_SUBTITLE, bold=True)
        text = reshape_persian("با تشکر از شما استاد")
        bbox = draw.textbbox((0, 0), text, font=font_thanks)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), text, font=font_thanks, fill=INK)
        y += int(FS_SUBTITLE * 2)
    
    if footer_name:
        font_name = get_font(FS_SUBTITLE, bold=True)
        text = reshape_persian(footer_name)
        bbox = draw.textbbox((0, 0), text, font=font_name)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), text, font=font_name, fill=INK)
    
    # Draw page number
    draw_page_number(draw, page_num)
    
    # Add natural imperfections
    img = add_natural_imperfections(img)
    
    return img


# ===== PAGE CONTENT =====

# Page 1: بسم الله + عنوان + مقدمه + شروع مطالب
page1_content = [
    {'text': 'خلاصه کتاب تفسیر موضوعی قرآن کریم', 'style': 'title', 'space_after': 20},
    {'text': 'تکالیف انسان در برابر خدا', 'style': 'subtitle', 'space_after': 50},
    {'text': 'مقدمه', 'style': 'header', 'space_after': 15},
    {'text': 'در این فصل از کتاب تفسیر موضوعی قرآن کریم، موضوع تکالیف انسان در برابر خداوند مورد بررسی قرار گرفته است. کتاب پیش از این فصل، حقوق انسان را مطرح کرده بود و بیان داشت که هر انسانی حقوقی دارد که می‌تواند از آن‌ها دفاع کند. اما در مقابل حقوق، تکالیفی نیز بر دوش انسان قرار دارد که عقل، وجدان و آموزه‌های دینی او را ملزم به انجام آن‌ها می‌کند.', 'style': 'body'},
    {'text': 'واژه «تکلیف» از ریشه «کَلَف» به معنای زحمت، رنج و مشقت است. این واژه در قرآن با تعابیر مختلفی به کار رفته و عموماً بر نکته‌ای تأکید شده که خداوند بیش از توان آدمیان از آن‌ها تکلیف نخواسته است. مفهوم تکلیف در این فصل هم شامل احکام شرعی مانند وجوب و حرمت می‌شود و هم مسائل اخلاقی مانند پرهیز از حسادت و تکبر را در بر می‌گیرد.', 'style': 'body'},
    {'text': 'تکالیف انسان در برابر خداوند به دو دسته اساسی تقسیم می‌شود:', 'style': 'body', 'space_after': 10},
    {'text': '۱. تکالیف باوری: شامل خداباوری و معادباوری', 'style': 'body'},
    {'text': '۲. تکالیف رفتاری: شامل انجام فرایض دینی و ترک معاصی', 'style': 'body', 'space_after': 30},
    {'text': 'بخش اول: تکالیف باوری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) خداباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'خداباوری نخستین و مهم‌ترین تکلیفی است که به اقتضای فطرت، وجدان درونی و دین بر دوش همه آدمیان گذاشته شده است. مراد از خداباوری، پذیرش موجودی متعالی و مقدس به نام خداوند به عنوان آفریننده جهان و انسان است؛ موجودی که همیشه بوده و همیشه خواهد بود و ما از کُنه ذات و صفات او هیچ اطلاعی نداریم.', 'style': 'body'},
    {'text': 'خداباوری بدان معناست که انسان باید اعتراف کند موجودی تصادفی پدید نیامده و خودش یا طبیعت در آفرینشش دخالتی نداشته است. انسان باید بپذیرد که در تمام هستی هوشمندی بی‌انتها نهفته است و چنان نظم و انتظامی بر سراسر عالم جاری است که هیچ عقل سالمی نمی‌تواند آن را تصادفی بداند.', 'style': 'body'},
]

# Page 2: ادامه خداباوری + فطرت خداشناسی + معادباوری
page2_content = [
    {'text': 'یکی از شگفتی‌های آفرینش، مغز انسان است. انسان‌ها نسبت به اندازه بدن خود بزرگ‌ترین مغز را دارند. مغز بسیار پیچیده است و میلیون‌ها نورون دارد که هر یک هزاران اتصال دارند. این نمایشگر هوشمندی بی‌انتها در آفرینش است.', 'style': 'body'},
    {'text': 'از منظر قرآن، شرک گناهی بزرگ است و خداوند اعلام داشته هر گناهی را به جز شرک می‌آمرزد. خداوند میل به خداشناسی را در نهاد و فطرت آدمیان قرار داده است و انسان بر اساس فطرت خود، آغاز و فرجام جهان و خوبی‌ها و بدی‌ها را می‌شناسد.', 'style': 'body'},
    {'text': 'قرآن در سوره عنکبوت مثالی زیبا از فطرت خداشناسی انسان ارائه می‌دهد: هنگامی که انسان بر کشتی سوار می‌شود، خدا را پاک‌دلانه می‌خواند، اما چون به خشکی رسید و نجات یافت، به ناگاه شرک می‌ورزد. این نشان‌دهنده آن است که خداشناسی در فطرت انسان نهادینه شده است.', 'style': 'verse'},
    {'text': 'در روایتی از امام صادق (ع)، شخصی از ایشان خواست خداوند را اثبات کند. امام از او پرسید: آیا هرگز سوار کشتی شده‌ای؟ مرد گفت: آری. امام فرمود: آیا پیش آمده که کشتی بشکند و تو دریابی که نه کشتی‌ای هست و نه نجات‌بخشی؟ آن مرد گفت: آری. امام فرمود: آیا در دلت افتاد که چیزی هست که می‌تواند تو را نجات دهد؟ مرد گفت: آری. امام فرمود: آن چیز همان خداوند است.', 'style': 'body', 'space_after': 30},
    {'text': 'ب) معادباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'معادباوری دومین تکلیف سنگین آدمیان در برابر خداوند است. قرآن بیشترین آموزه‌ها را در این زمینه دارد و تصویری روشن از اسرار جهان آخرت ارائه کرده است. مراد از معاد، مجموعه‌ای از رخدادهاست که از لحظه مرگ انسان شروع می‌شود و شامل برزخ، نفخ صور، فروپاشی عالم، اجتماع در صحرای محشر و محاسبه اعمال است.', 'style': 'body'},
    {'text': 'انسان باید باور داشته باشد که این دنیا پایان هستی نیست و روح انسان پس از مرگ نابود نمی‌شود. خداوند پس از مرگ، حیاتی دوباره به انسان می‌بخشد. نیکوکاران در بهشت جاودانه خواهند ماند و بسیاری از بدکاران پس از دوران عذاب، مشمول رحمت الهی خواهند شد.', 'style': 'body'},
    {'text': 'بهشت بالاترین پاداش مؤمنان است. قرآن از آن با عنوان «فوز عظیم»، «حیات حقیقی» و «اجر عظیم» یاد کرده است. نعمت‌های بهشت هم معنوی و هم مادی هستند. برترین نعمت معنوی، رضایت الهی و لقای خداوند است. در مقابل، جهنم برای کافران و فاسقان پیش‌بینی شده و عذاب آن بسیار فراتر از تاب و طاقت انسان است.', 'style': 'body'},
]

# Page 3: تکالیف رفتاری - عبودیت و نماز + ترک معاصی
page3_content = [
    {'text': 'بخش دوم: تکالیف رفتاری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) انجام فرایض دینی', 'style': 'subtitle', 'space_after': 10},
    {'text': 'نخستین تکلیف رفتاری آدمیان در برابر خداوند آن است که در برابر فرامین الهی سر تعظیم فرود آورند و به آن‌ها پایبند باشند. از این کار می‌توان با عنوان «عبودیت» یاد کرد. عبودیت یعنی بندگی، کرنش و سرسپردگی در برابر خداوند. قرآن هدف از آفرینش جن و انس را عبودیت خداوند دانسته است.', 'style': 'body'},
    {'text': 'عبادت شبانه‌روزی پیامبر اکرم (ص) مثال‌زدنی است. آن حضرت آن‌قدر به عبادت می‌پرداخت که خداوند به او فرمود: «ما قرآن را بر تو نفرستادیم تا خود را به زحمت اندازی». از امام صادق (ع) نقل شده که پیامبر پیوسته روی انگشتان پای خود برای عبادت می‌ایستاد. حضرت علی (ع) نیز بیشتر ساعات شب را به عبادت و مناجات می‌گذراند.', 'style': 'body'},
    {'text': 'نماز مهم‌ترین نماد عبودیت است. واژه «صلاة» بیش از ۹۰ بار در قرآن تکرار شده است. خداوند می‌فرماید: «بر نمازها و نماز میانه مواظبت کنید و خاضعانه برای خدا به پا خیزید». نماز راهکار ذکر الهی و بازدارنده از کارهای زشت و نارواست.', 'style': 'body'},
    {'text': 'در سوره مؤمنون، خداوند صفات پرهیزکاران را برشمرده و خشوع در نماز و محافظت بر آن را از ویژگی‌های آنان دانسته است. همچنین در سوره معارج، نمازگزاران را از رذایل اخلاقی مانند بخل مستثنا کرده و بر استمرار نماز آنان تأکید کرده است.', 'style': 'body', 'space_after': 30},
    {'text': 'ب) ترک معاصی', 'style': 'subtitle', 'space_after': 10},
    {'text': 'دومین تکلیف انسان در برابر خداوند، ترک معاصی است. انسان باید همه جا را محضر خداوند بداند و ادب حضور را رعایت کند. قرآن برای مفهوم گناه، واژه‌های گوناگونی مانند اثم، اصرار، جرم، ذنب، ظلم و سیئه به کار برده است.', 'style': 'body'},
    {'text': 'با بررسی آیات قرآن، هفت نکته اساسی درباره آثار گناه قابل برداشت است:', 'style': 'body'},
    {'text': '۱. گناه جایگاه انسان را فرو می‌کاهد و گاه او را مستحق لعن و نفرین می‌کند.', 'style': 'body'},
    {'text': '۲. گناه باعث محرومیت از توفیقات علمی و اخلاقی می‌شود.', 'style': 'body'},
    {'text': '۳. گناه راه‌های رسیدن به سعادت را مسدود می‌کند.', 'style': 'body'},
    {'text': '۴. گناه انسان را به خودفراموشی مبتلا می‌کند.', 'style': 'body'},
    {'text': '۵. گناه آبروی انسان را می‌برد و اعتبار اجتماعی او را نابود می‌کند.', 'style': 'body'},
    {'text': '۶. گناه باعث نزول عذاب الهی در دنیا می‌شود.', 'style': 'body'},
    {'text': '۷. گناه انسان را گرفتار عذاب برزخ و جهنم می‌کند.', 'style': 'body'},
]

# Page 4: ریشه‌های گناه + تاریخ + نتیجه‌گیری + امضا
page4_content = [
    {'text': 'ریشه‌های اصلی گناه', 'style': 'header', 'space_after': 15},
    {'text': 'بر اساس روایتی از امام صادق (ع)، ریشه‌های کفر سه چیز است: حرص، تکبر و حسادت. نخستین گناه در هستی، تکبر ابلیس بود که از سجده برای آدم سر باز زد. دومین گناه، حرص آدم بود که از درخت نهی‌شده تناول کرد. سومین گناه، حسادت قابیل بود که برادر خود هابیل را به ناحق کشت.', 'style': 'body'},
    {'text': 'گناهان دیگری که باعث نگونساری انسان می‌شوند عبارت‌اند از: عاق والدین، شراب‌خواری، منت‌گذاشتن پس از کار خیر، خون‌ریزی به ناحق، سخن‌چینی، قطع پیوند خویشاوندی، فساد اقتصادی و فجور.', 'style': 'body', 'space_after': 20},
    {'text': 'درس‌های تاریخی', 'style': 'header', 'space_after': 15},
    {'text': 'بررسی تاریخ امت‌های گذشته نشان می‌دهد که یکی از عوامل مهم سقوط آنان، ارتکاب معاصی بوده است. قوم لوط به دلیل گناه جنسی، قوم شعیب به دلیل فساد اقتصادی و کم‌فروشی، و بنی‌اسرائیل به دلیل دنیاطلبی و زیاده‌خواهی مجازات شدند. حتی در دوران رسول اکرم (ص)، لغزش‌های اخلاقی برخی مسلمانان مانند طمع در جنگ احد باعث شکست آنان شد.', 'style': 'body', 'space_after': 30},
    {'text': 'نتیجه‌گیری و برداشت شخصی', 'style': 'header', 'space_after': 15},
    {'text': 'مطالعه این فصل از تفسیر موضوعی قرآن نشان می‌دهد که انسان در برابر خداوند تکالیف مهمی بر عهده دارد که انجام آن‌ها ضامن سعادت دنیا و آخرت است. تکالیف باوری شامل شناخت خدا و باور به معاد، پایه و اساس زندگی معنوی انسان را تشکیل می‌دهد. بدون این باورها، تکالیف رفتاری نیز بی‌معنا خواهد بود.', 'style': 'body'},
    {'text': 'از مهم‌ترین نکات این فصل آن است که قرآن خداشناسی را امری فطری می‌داند و معتقد است انسان ذاتاً خدا را می‌شناسد اما عواملی مانند غفلت و دنیاطلبی این شناخت را کمرنگ می‌کند. همچنین تأکید بر آثار منفی گناه در زندگی فردی و اجتماعی، نشان‌دهنده اهمیت تقوا و پرهیزکاری در منظر قرآن است.', 'style': 'body'},
    {'text': 'در مجموع، این فصل پیام روشنی دارد: انسان با شناخت خدا، باور به معاد، انجام عبادات و دوری از گناهان می‌تواند به مقام عبودیت واقعی دست یابد و زندگی سعادتمندانه‌ای داشته باشد.', 'style': 'body'},
    {'text': '', 'style': 'body', 'space_after': 50},
    {'text': 'با تشکر از شما استاد', 'style': 'title', 'space_after': 20},
    {'text': 'یوکابد شهسواری', 'style': 'title'},
]


def main():
    """Generate all 4 pages."""
    print("Generating page 1...")
    img1 = render_page(page1_content, 1, has_bismillah=True)
    img1.save(os.path.join(OUTPUT_DIR, 'page_01.png'), 'PNG', dpi=(300, 300))
    print(f"  Saved page_01.png ({img1.size})")
    
    print("Generating page 2...")
    img2 = render_page(page2_content, 2)
    img2.save(os.path.join(OUTPUT_DIR, 'page_02.png'), 'PNG', dpi=(300, 300))
    print(f"  Saved page_02.png ({img2.size})")
    
    print("Generating page 3...")
    img3 = render_page(page3_content, 3)
    img3.save(os.path.join(OUTPUT_DIR, 'page_03.png'), 'PNG', dpi=(300, 300))
    print(f"  Saved page_03.png ({img3.size})")
    
    print("Generating page 4...")
    img4 = render_page(page4_content, 4)
    img4.save(os.path.join(OUTPUT_DIR, 'page_04.png'), 'PNG', dpi=(300, 300))
    print(f"  Saved page_04.png ({img4.size})")
    
    print("\nAll 4 pages generated successfully!")


if __name__ == '__main__':
    main()