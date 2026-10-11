#!/usr/bin/env python3
"""
Generate high-quality PDF from PIL-rendered A4 pages.
Uses the existing Mikhak-DS1-FD font rendering pipeline.
"""

import os
import sys
import random
import math

# Add the project directory
sys.path.insert(0, '/home/user/taklif')

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
    base = INK_BASE
    r = max(0, min(255, base[0] + random.randint(-5, 5)))
    g = max(0, min(255, base[1] + random.randint(-5, 5)))
    b = max(0, min(255, base[2] + random.randint(-6, 6)))
    return (r, g, b)


def reshape_persian(text):
    if not text or not text.strip():
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def get_font(size, bold=False):
    if bold:
        path = os.path.join(FONTS_DIR, 'Mikhak-DS1-FD-Bold.ttf')
    else:
        path = os.path.join(FONTS_DIR, 'Mikhak-DS1-FD-Medium.ttf')
    return ImageFont.truetype(path, size)


def create_paper_background():
    img = Image.new('RGB', (W, H), PAPER_BASE)
    draw = ImageDraw.Draw(img)
    
    random.seed(42)
    
    for _ in range(40000):
        x = random.randint(0, W-1)
        y = random.randint(0, H-1)
        shade = random.randint(246, 255)
        draw.point((x, y), fill=(shade, max(0, shade-2), max(0, shade-5)))
    
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
    
    margin_x = W - M_R + 50
    for y in range(M_T - 40, H - M_B + 40, 2):
        draw.point((int(margin_x + random.uniform(-0.5, 0.5)), y), fill=(215, 170, 170))
    
    return img


def render_line_to_image(text, font, color):
    display_text = reshape_persian(text)
    
    temp_img = Image.new('RGBA', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    bbox = temp_draw.textbbox((0, 0), display_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    padding = 30
    line_img = Image.new('RGBA', (tw + padding*2, th + padding*2), (0, 0, 0, 0))
    line_draw = ImageDraw.Draw(line_img)
    
    line_draw.text((padding, padding), display_text, font=font, fill=color + (255,))
    
    return line_img, tw + padding*2, th + padding*2


def apply_line_transformations(line_img, rotation=0, scale=1.0):
    if abs(rotation) > 0.01:
        line_img = line_img.rotate(rotation, expand=True, resample=Image.BICUBIC, 
                                    fillcolor=(0, 0, 0, 0))
    
    if abs(scale - 1.0) > 0.01:
        new_w = max(1, int(line_img.width * scale))
        new_h = max(1, int(line_img.height * scale))
        line_img = line_img.resize((new_w, new_h), Image.LANCZOS)
    
    return line_img


def composite_line_on_paper(paper, line_img, x, y):
    x = max(0, min(paper.width - line_img.width, int(x)))
    y = max(0, min(paper.height - line_img.height, int(y)))
    
    region = paper.crop((x, y, x + line_img.width, y + line_img.height))
    composite = Image.alpha_composite(region.convert('RGBA'), line_img)
    paper.paste(composite.convert('RGB'), (x, y))
    
    return paper


def add_ink_effects(img):
    blurred = img.filter(ImageFilter.GaussianBlur(radius=0.4))
    result = Image.blend(img, blurred, 0.12)
    return result


def add_paper_effects(img):
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
    angle = random.uniform(-0.12, 0.12)
    img = img.rotate(angle, fillcolor=PAPER_BASE, expand=False)
    img = add_ink_effects(img)
    img = add_paper_effects(img)
    return img


def draw_page_number(draw, page_num):
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
    img = create_paper_background()
    
    y = M_T
    line_h = int(FS_BODY * LINE_H_FACTOR)
    
    if has_bismillah:
        font_bism = get_font(FS_TITLE + 4, bold=True)
        text = reshape_persian("به نام خدا")
        temp_draw = ImageDraw.Draw(img)
        bbox = temp_draw.textbbox((0, 0), text, font=font_bism)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        
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
        else:
            font = get_font(FS_BODY)
            wrapped = wrap_text_persian(text, font, TEXT_W, temp_draw)
            indent = 0
        
        for wline in wrapped:
            display_text = reshape_persian(wline)
            bbox = temp_draw.textbbox((0, 0), display_text, font=font)
            tw = bbox[2] - bbox[0]
            
            if style == 'title':
                text_x = (W - tw) // 2
            else:
                text_x = W - M_R - tw - indent
            
            rotation = random.uniform(-0.4, 0.4)
            scale = random.uniform(0.97, 1.03)
            offset_x = random.uniform(-3, 3)
            offset_y = random.uniform(-2, 2)
            
            line_img, _, _ = render_line_to_image(wline, font, get_ink_color())
            line_img = apply_line_transformations(line_img, rotation=rotation, scale=scale)
            
            img = composite_line_on_paper(img, line_img, 
                                           text_x + offset_x, 
                                           y + offset_y)
            
            y += int(font.size * LINE_H_FACTOR) + random.uniform(-1.5, 1.5)
        
        if space_after:
            y += space_after
    
    draw = ImageDraw.Draw(img)
    draw_page_number(draw, page_num)
    
    img = add_final_effects(img)
    
    return img


# ===== PAGE CONTENT =====
page1_content = [
    {'text': 'خلاصه فصل: تکالیف انسان در برابر خدا', 'style': 'title', 'space_after': 25},
    {'text': 'منبع: تفسیر موضوعی قرآن کریم — فصل ۴۰', 'style': 'subtitle', 'space_after': 50},
    {'text': 'مقدمه و تعریف تکلیف', 'style': 'header', 'space_after': 15},
    {'text': 'در فصل پیش، حقوق انسان مطرح شد و بیان گردید که هر انسانی حقوقی دارد. اما در مقابل حقوق، تکالیفی نیز بر دوش انسان قرار دارد که عقل، وجدان و آموزه‌های دینی او را ملزم به انجام آن‌ها می‌کند.', 'style': 'body'},
    {'text': 'واژه «تکلیف» از ریشه «کَلَف» به معنای زحمت، رنج و مشقت است. این واژه در قرآن با تعابیر مختلفی به کار رفته و عموماً بر نکته‌ای تأکید شده که خداوند بیش از توان آدمیان از آن‌ها تکلیف نخواسته است. مفهوم تکلیف هم شامل احکام شرعی مانند وجوب و حرمت می‌شود و هم مسائل اخلاقی مانند پرهیز از حسادت و تکبر را در بر می‌گیرد.', 'style': 'body'},
    {'text': 'تکالیف انسان در برابر خداوند به دو دسته تقسیم می‌شود: ۱. تکالیف باوری (خداباوری و معادباوری) ۲. تکالیف رفتاری (انجام فرایض و ترک معاصی).', 'style': 'body', 'space_after': 35},
    {'text': 'بخش اول: تکالیف باوری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) خداباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'نخستین و مهم‌ترین تکلیف، پذیرش موجودی متعالی به نام خداوند به عنوان آفریننده جهان و انسان است. خداباوری بدان معناست که انسان باید بپذیرد موجودی تصادفی پدید نیامده و در تمام هستی هوشمندی بی‌انتها نهفته است. چنان نظم و انتظامی بر عالم حاکم است که هیچ عقل سالمی نمی‌تواند آن را تصادفی بداند.', 'style': 'body'},
    {'text': 'از منظر قرآن، شرک گناهی بزرگ است و خداوند هر گناهی را به جز شرک می‌آمرزد. خداوند میل به خداشناسی را در نهاد و فطرت آدمیان قرار داده.', 'style': 'body'},
]

page2_content = [
    {'text': 'قرآن در سوره عنکبوت مثالی زیبا از فطرت خداشناسی ارائه می‌دهد:', 'style': 'body'},
    {'text': 'و هنگامی که بر کشتی سوار می‌شوند، خدا را پاک‌دلانه می‌خوانند، اما چون به خشکی رسیدند، به ناگاه شرک می‌ورزند. (عنکبوت/۶۵)', 'style': 'verse'},
    {'text': 'در روایتی از امام صادق (ع)، شخصی خواست خداوند برایش اثبات شود. امام پرسید: آیا هرگز سوار کشتی شده‌ای؟ مرد گفت: آری. امام فرمود: آیا کشتی شکسته و نجات‌بخشی نیافتی؟ مرد گفت: آری. امام فرمود: آیا در دلت افتاد چیزی هست که نجاتت دهد؟ مرد گفت: آری. امام فرمود: آن همان خداوند است.', 'style': 'body', 'space_after': 35},
    {'text': 'ب) معادباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'معادباوری دومین تکلیف سنگین آدمیان است. مراد از معاد، مجموعه‌ای از رخدادهاست که از لحظه مرگ شروع و شامل برزخ، نفخ صور، فروپاشی عالم، اجتماع در صحرای محشر و محاسبه اعمال است. انسان باید باور داشته باشد این دنیا پایان هستی نیست.', 'style': 'body'},
    {'text': 'حیات برزخی: خداوند درباره شهیدان می‌فرماید: «هرگز کسانی را که در راه خدا کشته شده‌اند، مرده مپندار، بلکه زنده‌اند». قبر باغی از باغ‌های بهشت یا چاله‌ای از چاله‌های آتش است.', 'style': 'body'},
    {'text': 'بهشت و جهنم: قرآن از بهشت با عنوان «فوز عظیم» و «حیات حقیقی» یاد کرده. نعمت‌های بهشت هم معنوی (رضایت الهی و لقای خداوند) و هم مادی (همسران بهشتی، باغ‌ها) هستند. جهنم برای کافران و فاسقان پیش‌بینی شده و عذاب آن فراتر از طاقت انسان است.', 'style': 'body'},
]

page3_content = [
    {'text': 'بخش دوم: تکالیف رفتاری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) انجام فرایض دینی (عبودیت)', 'style': 'subtitle', 'space_after': 10},
    {'text': 'نخستین تکلیف رفتاری آن است که در برابر فرامین الهی سر تعظیم فرود آورند. عبودیت یعنی بندگی و سرسپردگی. قرآن هدف از آفرینش جن و انس را عبودیت دانسته: «و جن و انس را نیافریدم جز برای آنکه مرا بپرستند» (ذاریات/۵۶).', 'style': 'body'},
    {'text': 'عبادت پیامبر اکرم (ص) مثال‌زدنی بود. آن حضرت آن‌قدر عبادت می‌کرد که خداوند فرمود: «ما قرآن را بر تو نفرستادیم تا خود را به زحمت اندازی» (طه/۲). حضرت علی (ع) بیشتر ساعات شب را به مناجات می‌گذراند و امام سجاد (ع) به «زین العابدین» معروف بود.', 'style': 'body'},
    {'text': 'نماز مهم‌ترین نماد عبودیت است. واژه «صلاة» بیش از ۹۰ بار در قرآن تکرار شده. خداوند می‌فرماید: «بر نمازها و نماز میانه مواظبت کنید» (بقره/۲۳۸). نماز بازدارنده از کارهای زشت است: «نماز از کار زشت و ناپسند باز می‌دارد» (عنکبوت/۴۵).', 'style': 'body'},
    {'text': 'از نگاه قرآن، نماز در برنامه عبادی همه پیامبران جایگاه ویژه‌ای داشته. از زبان ابراهیم (ع): «مرا برپادارنده نماز قرار ده و از فرزندان من نیز» (ابراهیم/۴۰).', 'style': 'body', 'space_after': 35},
    {'text': 'ب) ترک معاصی', 'style': 'subtitle', 'space_after': 10},
    {'text': 'دومین تکلیف، ترک معاصی است. انسان باید همه‌جا را محضر خداوند بداند. قرآن برای گناه واژه‌های مختلفی (اثم، ذنب، ظلم، سیئه) به کار برده. هفت اثر مهم گناه:', 'style': 'body'},
    {'text': '۱. فروکاستن جایگاه انسان ۲. محرومیت از توفیقات ۳. مسدود شدن راه سعادت ۴. خودفراموشی ۵. از دست رفتن آبرو ۶. نزول عذاب دنیوی ۷. عذاب برزخ و جهنم', 'style': 'body'},
]

page4_content = [
    {'text': 'ریشه‌های اصلی گناه در تاریخ', 'style': 'header', 'space_after': 15},
    {'text': 'بر اساس روایت امام صادق (ع)، ریشه‌های کفر سه چیز است: حرص، تکبر و حسادت. نخستین گناه، تکبر ابلیس بود (سر باز زدن از سجده بر آدم). دومین گناه، حرص آدم (خوردن از درخت نهی‌شده). سومین گناه، حسادت قابیل (کشتن هابیل).', 'style': 'body'},
    {'text': 'گناهان دیگر: عاق والدین، شراب‌خواری، منت‌گذاشتن پس از کار خیر، خون‌ریزی ناحق، سخن‌چینی، قطع پیوند خویشاوندی و فساد اقتصادی. قوم لوط به دلیل گناه جنسی، قوم شعیب به دلیل کم‌فروشی و بنی‌اسرائیل به دلیل دنیاطلبی مجازات شدند. در جنگ احد نیز طمع برخی مسلمانان باعث شکست شد.', 'style': 'body', 'space_after': 35},
    {'text': 'نتیجه‌گیری', 'style': 'header', 'space_after': 15},
    {'text': 'انسان در برابر خداوند تکالیف مهمی دارد. تکالیف باوری (شناخت خدا و باور به معاد) پایه زندگی معنوی است. قرآن خداشناسی را امری فطری می‌داند و غفلت و دنیاطلبی را عامل کمرنگ شدن آن معرفی می‌کند.', 'style': 'body'},
    {'text': 'تأکید قرآن بر آثار منفی گناه، نشان‌دهنده اهمیت تقواست. انسان با شناخت خدا، باور به معاد، انجام عبادات و دوری از گناهان می‌تواند به مقام عبودیت واقعی دست یابد و سعادت دنیا و آخرت را تضمین کند.', 'style': 'body'},
    {'text': '', 'style': 'body', 'space_after': 50},
    {'text': 'منابع: حق و تکلیف در اسلام (جوادی آملی) / حق و سیاست در قرآن (مصباح یزدی) / نظریه حقوق اسلامی (مصباح یزدی) / دایرةالمعارف قرآن کریم', 'style': 'body'},
]


def main():
    print("Generating high-quality handwritten PDF...")
    
    pages = [
        (page1_content, 1, True),
        (page2_content, 2, False),
        (page3_content, 3, False),
        (page4_content, 4, False),
    ]
    
    images = []
    
    for content, page_num, has_bismillah in pages:
        print(f"  Rendering page {page_num}...")
        random.seed(page_num * 42)  # Deterministic per page
        img = render_page(content, page_num, has_bismillah=has_bismillah)
        fname = f'page_0{page_num}.png'
        img.save(os.path.join(OUTPUT_DIR, fname), 'PNG', dpi=(300, 300))
        images.append(img)
        print(f"    Saved {fname}")
    
    # Save as PDF
    pdf_path = os.path.join(OUTPUT_DIR, 'chapter_summary_handwritten.pdf')
    
    # Convert to RGB if needed and save as PDF
    rgb_images = []
    for img in images:
        if img.mode != 'RGB':
            rgb_images.append(img.convert('RGB'))
        else:
            rgb_images.append(img)
    
    rgb_images[0].save(
        pdf_path,
        'PDF',
        save_all=True,
        append_images=rgb_images[1:],
        resolution=300.0,
    )
    
    print(f"\nPDF saved to: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path) / 1024 / 1024:.1f} MB")
    print(f"Total pages: {len(images)}")
    
    return pdf_path


if __name__ == '__main__':
    main()