#!/usr/bin/env python3
"""
Clean digital Persian PDF using Mikhak-DS1-FD font.
Renders text with PIL (correct glyph shaping) then composites into PDF.
No handwriting effects — clean professional look.
"""

import os, random
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

BASE_DIR = '/home/user/taklif'
FONTS_DIR = os.path.join(BASE_DIR, 'fonts_new')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# A4 at 300 DPI
W, H = 2480, 3508
M_R, M_L, M_T, M_B = 280, 280, 260, 260
TEXT_W = W - M_R - M_L

FS_BODY = 44
FS_TITLE = 60
FS_SUBTITLE = 50
FS_HEADER = 54
LINE_H_FACTOR = 1.72

INK_COLOR = (20, 20, 20)  # black digital ink
TITLE_COLOR = (0, 51, 153)
VERSE_COLOR = (0, 100, 60)
PAPER_COLOR = (255, 255, 255)


def reshape_persian(text):
    if not text or not text.strip():
        return text
    return get_display(arabic_reshaper.reshape(text))


def get_font(size, bold=False):
    if bold:
        path = os.path.join(FONTS_DIR, 'Mikhak-DS1-FD-Bold.ttf')
    else:
        path = os.path.join(FONTS_DIR, 'Mikhak-DS1-FD-Medium.ttf')
    return ImageFont.truetype(path, size)


def wrap_text_persian(text, font, max_width, draw):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), reshape_persian(test), font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text_right(draw, text, x_right, y, font, color):
    display = reshape_persian(text)
    bbox = draw.textbbox((0, 0), display, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x_right - tw, y), display, font=font, fill=color)
    return tw


def draw_text_center(draw, text, y, font, color):
    display = reshape_persian(text)
    bbox = draw.textbbox((0, 0), display, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), display, font=font, fill=color)


def render_page(content_lines, page_num):
    img = Image.new('RGB', (W, H), PAPER_COLOR)
    draw = ImageDraw.Draw(img)

    y = M_T
    x_right = W - M_R

    for item in content_lines:
        text = item.get('text', '')
        style = item.get('style', 'body')
        space_after = item.get('space_after', 0)

        if not text.strip():
            y += space_after if space_after else 30
            continue

        if style == 'title':
            font = get_font(FS_TITLE, bold=True)
            draw_text_center(draw, text, y, font, TITLE_COLOR)
            y += int(FS_TITLE * 1.6)

        elif style == 'subtitle':
            font = get_font(FS_SUBTITLE, bold=True)
            draw_text_right(draw, text, x_right, y, font, TITLE_COLOR)
            y += int(FS_SUBTITLE * 1.5)

        elif style == 'header':
            font = get_font(FS_HEADER, bold=True)
            draw_text_right(draw, text, x_right, y, font, (0, 51, 153))
            # underline
            y_line = y + int(FS_HEADER * 1.2)
            draw.line([(M_L, y_line), (x_right, y_line)], fill=(0, 51, 153), width=2)
            y += int(FS_HEADER * 1.6)

        elif style == 'verse':
            font = get_font(FS_BODY + 2)
            wrapped = wrap_text_persian(text, font, TEXT_W - 160, draw)
            for wl in wrapped:
                draw_text_right(draw, wl, x_right - 80, y, font, VERSE_COLOR)
                y += int(FS_BODY * LINE_H_FACTOR)
            y += 10

        elif style == 'def':
            font = get_font(FS_BODY, bold=True)
            draw_text_right(draw, text, x_right, y, font, (0, 51, 153))
            y += int(FS_BODY * 1.4)

        else:  # body
            font = get_font(FS_BODY)
            wrapped = wrap_text_persian(text, font, TEXT_W, draw)
            for wl in wrapped:
                draw_text_right(draw, wl, x_right, y, font, INK_COLOR)
                y += int(FS_BODY * LINE_H_FACTOR)

        if space_after:
            y += space_after

    # Page number
    font_num = get_font(32)
    draw_text_center(draw, f'— {page_num} —', H - M_B + 40, font_num, (150, 150, 150))

    return img


# ===== CONTENT =====
page1 = [
    {'text': 'بسم الله الرحمن الرحیم', 'style': 'title', 'space_after': 20},
    {'text': 'خلاصه فصل: تکالیف انسان در برابر خدا', 'style': 'title', 'space_after': 10},
    {'text': 'منبع: تفسیر موضوعی قرآن کریم — فصل ۴۰', 'style': 'subtitle', 'space_after': 40},
    {'text': 'مقدمه و تعریف تکلیف', 'style': 'header', 'space_after': 15},
    {'text': 'در فصل پیش، حقوق انسان مطرح شد. در مقابل حقوق، تکالیفی بر دوش انسان قرار دارد که عقل، وجدان و آموزه‌های دینی او را ملزم به انجام آن‌ها می‌کند.', 'style': 'body'},
    {'text': 'واژه «تکلیف» از ریشه «کَلَف» به معنای زحمت و مشقت است. خداوند بیش از توان آدمیان تکلیف نخواسته. مفهوم تکلیف هم شامل احکام شرعی (وجوب و حرمت) و هم مسائل اخلاقی (پرهیز از حسادت و تکبر) می‌شود.', 'style': 'body'},
    {'text': 'تکالیف انسان در برابر خدا به دو دسته تقسیم می‌شود:', 'style': 'body', 'space_after': 10},
    {'text': '۱. تکالیف باوری: خداباوری و معادباوری', 'style': 'body'},
    {'text': '۲. تکالیف رفتاری: انجام فرایض دینی و ترک معاصی', 'style': 'body', 'space_after': 35},
    {'text': 'بخش اول: تکالیف باوری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) خداباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'نخستین تکلیف، پذیرش موجودی متعالی به نام خداوند به عنوان آفریننده جهان و انسان است. خداباوری یعنی انسان بپذیرد موجودی تصادفی پدید نیامده و در تمام هستی هوشمندی بی‌انتها نهفته است. چنان نظمی بر عالم حاکم است که هیچ عقل سالمی نمی‌تواند آن را تصادفی بداند.', 'style': 'body'},
    {'text': 'از منظر قرآن، شرک گناهی بزرگ است و خداوند هر گناهی را جز شرک می‌آمرزد. خداوند میل به خداشناسی را در فطرت آدمیان قرار داده.', 'style': 'body'},
]

page2 = [
    {'text': 'قرآن در سوره عنکبوت مثالی زیبا از فطرت خداشناسی ارائه می‌دهد:', 'style': 'body'},
    {'text': 'و هنگامی که بر کشتی سوار می‌شوند، خدا را پاک‌دلانه می‌خوانند، اما چون نجات یافتند، شرک می‌ورزند. (عنکبوت/۶۵)', 'style': 'verse'},
    {'text': 'در روایتی از امام صادق (ع): شخصی خواست خداوند برایش اثبات شود. امام پرسید: آیا سوار کشتی شده‌ای؟ مرد گفت: آری. امام فرمود: آیا کشتی شکسته و نجات‌بخشی نیافتی؟ مرد گفت: آری. امام فرمود: آیا در دلت افتاد چیزی نجاتت دهد؟ مرد گفت: آری. امام فرمود: آن همان خداوند است.', 'style': 'body', 'space_after': 35},
    {'text': 'ب) معادباوری', 'style': 'subtitle', 'space_after': 10},
    {'text': 'دومین تکلیف سنگین آدمیان. مراد از معاد: مجموعه رخدادها از لحظه مرگ شامل برزخ، نفخ صور، فروپاشی عالم، اجتماع در صحرای محشر و محاسبه اعمال. انسان باید باور داشته باشد این دنیا پایان هستی نیست.', 'style': 'body'},
    {'text': 'حیات برزخی:', 'style': 'def'},
    {'text': 'واژه «برزخ» به معنای حد فاصل است. خداوند درباره شهیدان می‌فرماید: «هرگز کسانی را که در راه خدا کشته شده‌اند، مرده مپندار، بلکه زنده‌اند» (آل‌عمران/۱۶۹). قبر باغی از باغ‌های بهشت یا چاله‌ای از آتش است.', 'style': 'body'},
    {'text': 'بهشت و جهنم:', 'style': 'def'},
    {'text': 'قرآن از بهشت با عنوان «فوز عظیم» و «حیات حقیقی» یاد کرده. نعمت‌های بهشت هم معنوی (رضایت الهی) و هم مادی (باغ‌ها). جهنم برای کافران و فاسقان و عذاب آن فراتر از طاقت انسان است.', 'style': 'body'},
]

page3 = [
    {'text': 'بخش دوم: تکالیف رفتاری', 'style': 'header', 'space_after': 15},
    {'text': 'الف) انجام فرایض دینی (عبودیت)', 'style': 'subtitle', 'space_after': 10},
    {'text': 'عبودیت یعنی بندگی و سرسپردگی در برابر خداوند. قرآن هدف آفرینش را عبودیت دانسته: «و جن و انس را نیافریدم جز برای آنکه مرا بپرستند» (ذاریات/۵۶).', 'style': 'body'},
    {'text': 'عبادت پیامبر اکرم (ص) مثال‌زدنی بود: «ما قرآن را بر تو نفرستادیم تا خود را به زحمت اندازی» (طه/۲). حضرت علی (ع) بیشتر ساعات شب را به مناجات می‌گذراند. امام سجاد (ع) به «زین العابدین» معروف بود.', 'style': 'body'},
    {'text': 'جایگاه نماز:', 'style': 'def'},
    {'text': 'واژه «صلاة» بیش از ۹۰ بار در قرآن تکرار شده. «بر نمازها و نماز میانه مواظبت کنید» (بقره/۲۳۸). نماز بازدارنده از کار زشت است: «نماز از کار زشت و ناپسند باز می‌دارد» (عنکبوت/۴۵).', 'style': 'body'},
    {'text': 'از زبان ابراهیم (ع): «مرا برپادارنده نماز قرار ده و از فرزندان من نیز» (ابراهیم/۴۰). از زبان عیسی (ع): «تا زنده‌ام به نماز و زکات سفارش کرده است» (مریم/۳۱).', 'style': 'body', 'space_after': 30},
    {'text': 'ب) ترک معاصی', 'style': 'subtitle', 'space_after': 10},
    {'text': 'انسان باید همه‌جا را محضر خداوند بداند. قرآن برای گناه واژه‌های مختلفی به کار برده: اثم، ذنب، ظلم، سیئه و عثرة.', 'style': 'body'},
    {'text': 'هفت اثر مهم گناه:', 'style': 'body'},
    {'text': '۱. فروکاستن جایگاه انسان  ۲. محرومیت از توفیقات  ۳. مسدود شدن راه سعادت  ۴. خودفراموشی  ۵. از دست رفتن آبرو  ۶. نزول عذاب دنیوی  ۷. عذاب برزخ و جهنم', 'style': 'body'},
]

page4 = [
    {'text': 'ریشه‌های اصلی گناه در تاریخ', 'style': 'header', 'space_after': 15},
    {'text': 'بر اساس روایت امام صادق (ع)، ریشه‌های کفر سه چیز است: حرص، تکبر و حسادت. نخستین گناه: تکبر ابلیس (سر باز زدن از سجده بر آدم). دومین گناه: حرص آدم (خوردن از درخت نهی‌شده). سومین گناه: حسادت قابیل (کشتن هابیل).', 'style': 'body'},
    {'text': 'گناهان دیگر: عاق والدین، شراب‌خواری، خون‌ریزی ناحق، سخن‌چینی، قطع پیوند خویشاوندی و فساد اقتصادی. قوم لوط به دلیل گناه جنسی، قوم شعیب به دلیل کم‌فروشی و بنی‌اسرائیل به دلیل دنیاطلبی مجازات شدند. در جنگ احد طمع برخی مسلمانان باعث شکست شد.', 'style': 'body', 'space_after': 30},
    {'text': 'نتیجه‌گیری', 'style': 'header', 'space_after': 15},
    {'text': 'تکالیف باوری (شناخت خدا و باور به معاد) پایه زندگی معنوی انسان است. قرآن خداشناسی را امری فطری می‌داند و غفلت و دنیاطلبی را عامل کمرنگ شدن آن معرفی می‌کند.', 'style': 'body'},
    {'text': 'تأکید قرآن بر آثار منفی گناه، نشان‌دهنده اهمیت تقواست. انسان با شناخت خدا، باور به معاد، انجام عبادات و دوری از گناهان می‌تواند به مقام عبودیت واقعی دست یابد و سعادت دنیا و آخرت را تضمین کند.', 'style': 'body'},
    {'text': '', 'style': 'body', 'space_after': 40},
    {'text': 'منابع برای مطالعه:', 'style': 'def'},
    {'text': '۱. حق و تکلیف در اسلام — جوادی آملی — قم: اسراء', 'style': 'body'},
    {'text': '۲. حق و سیاست در قرآن — مصباح یزدی — قم: مؤسسه امام خمینی', 'style': 'body'},
    {'text': '۳. نظریه حقوق اسلام — مصباح یزدی — قم: مؤسسه امام خمینی', 'style': 'body'},
    {'text': '۴. دایرةالمعارف قرآن کریم — ج ۸ — قم: بوستان کتاب', 'style': 'body'},
]


def main():
    print("Generating clean digital Persian PDF...")
    pages = [(page1, 1), (page2, 2), (page3, 3), (page4, 4)]
    images = []
    for content, num in pages:
        print(f"  Page {num}...")
        img = render_page(content, num)
        img.save(os.path.join(OUTPUT_DIR, f'page_clean_{num:02d}.png'), 'PNG', dpi=(300, 300))
        images.append(img)

    pdf_path = os.path.join(OUTPUT_DIR, 'chapter_summary_clean.pdf')
    images[0].save(pdf_path, 'PDF', save_all=True, append_images=images[1:], resolution=300.0)
    print(f"\nPDF: {pdf_path}")
    print(f"Size: {os.path.getsize(pdf_path) / 1024:.0f} KB")
    print(f"Pages: {len(images)}")

if __name__ == '__main__':
    main()