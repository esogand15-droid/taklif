#!/usr/bin/env python3
"""
Clean professional Persian PDF — Vazirmatn font.
No handwriting effects. Pure digital typesetting.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

BASE = '/home/user/taklif'
FDIR = os.path.join(BASE, 'fonts_vazir')
OUT  = os.path.join(BASE, 'output')
os.makedirs(OUT, exist_ok=True)

# A4 at 300 DPI
W, H = 2480, 3508
ML, MR, MT, MB = 280, 280, 240, 240
TW = W - ML - MR

# Sizes
S_BODY = 42
S_TITLE = 56
S_SUB = 48
S_HDR = 50
LH = 1.75

# Colors
C_BLACK  = (30, 30, 30)
C_TITLE  = (0, 60, 140)
C_VERSE  = (0, 100, 60)
C_DEF    = (0, 70, 150)
C_LINE   = (0, 60, 140)
C_PAPER  = (255, 255, 255)
C_FOOTER = (160, 160, 160)


def rp(text):
    """Reshape Persian text for correct RTL display."""
    if not text or not text.strip():
        return text
    return get_display(arabic_reshaper.reshape(text))


def font(size, weight='Regular'):
    return ImageFont.truetype(os.path.join(FDIR, f'Vazirmatn-{weight}.ttf'), size)


def wrap(text, f, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = cur + (" " if cur else "") + w
        bb = draw.textbbox((0, 0), rp(test), font=f)
        if bb[2] - bb[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_r(draw, txt, xr, y, f, color):
    """Draw text right-aligned."""
    d = rp(txt)
    bb = draw.textbbox((0, 0), d, font=f)
    draw.text((xr - (bb[2] - bb[0]), y), d, font=f, fill=color)
    return bb[3] - bb[1]


def text_c(draw, txt, y, f, color):
    """Draw text centered."""
    d = rp(txt)
    bb = draw.textbbox((0, 0), d, font=f)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), d, font=f, fill=color)


def render_page(lines, page_num):
    img = Image.new('RGB', (W, H), C_PAPER)
    draw = ImageDraw.Draw(img)
    y = MT
    xr = W - MR

    for item in lines:
        txt = item.get('t', '')
        sty = item.get('s', 'body')
        sp  = item.get('sp', 0)

        if not txt.strip():
            y += sp if sp else 25
            continue

        if sty == 'title':
            f = font(S_TITLE, 'Bold')
            text_c(draw, txt, y, f, C_TITLE)
            y += int(S_TITLE * 1.6)

        elif sty == 'sub':
            f = font(S_SUB, 'Bold')
            text_r(draw, txt, xr, y, f, C_TITLE)
            y += int(S_SUB * 1.5)

        elif sty == 'hdr':
            f = font(S_HDR, 'Bold')
            text_r(draw, txt, xr, y, f, C_TITLE)
            yl = y + int(S_HDR * 1.2)
            draw.line([(ML, yl), (xr, yl)], fill=C_LINE, width=2)
            y += int(S_HDR * 1.6)

        elif sty == 'verse':
            f = font(S_BODY + 2, 'Medium')
            for wl in wrap(txt, f, TW - 160, draw):
                text_r(draw, wl, xr - 80, y, f, C_VERSE)
                y += int((S_BODY + 2) * LH)
            y += 12

        elif sty == 'def':
            f = font(S_BODY, 'Bold')
            text_r(draw, txt, xr, y, f, C_DEF)
            y += int(S_BODY * 1.4)

        else:  # body
            f = font(S_BODY)
            for wl in wrap(txt, f, TW, draw):
                text_r(draw, wl, xr, y, f, C_BLACK)
                y += int(S_BODY * LH)

        if sp:
            y += sp

    # Footer
    text_c(draw, f'{page_num}', H - MB + 50, font(30), C_FOOTER)
    return img


# ──── CONTENT ────

p1 = [
    {'t': 'بسم الله الرحمن الرحیم', 's': 'title', 'sp': 20},
    {'t': 'خلاصه فصل: تکالیف انسان در برابر خدا', 's': 'title', 'sp': 8},
    {'t': 'منبع: تفسیر موضوعی قرآن کریم — فصل ۴۰', 's': 'sub', 'sp': 40},
    {'t': 'مقدمه و تعریف تکلیف', 's': 'hdr', 'sp': 12},
    {'t': 'در فصل پیش، حقوق انسان مطرح شد. در مقابل حقوق، تکالیفی بر دوش انسان قرار دارد که عقل، وجدان و آموزه‌های دینی او را ملزم به انجام آن‌ها می‌کند.', 's': 'body'},
    {'t': 'واژه «تکلیف» از ریشه «کَلَف» به معنای زحمت و مشقت است. خداوند بیش از توان آدمیان تکلیف نخواسته. مفهوم تکلیف هم شامل احکام شرعی (وجوب و حرمت) و هم مسائل اخلاقی (پرهیز از حسادت و تکبر) می‌شود.', 's': 'body'},
    {'t': 'تکالیف انسان در برابر خدا به دو دسته تقسیم می‌شود:', 's': 'body', 'sp': 8},
    {'t': '۱. تکالیف باوری: خداباوری و معادباوری', 's': 'body'},
    {'t': '۲. تکالیف رفتاری: انجام فرایض دینی و ترک معاصی', 's': 'body', 'sp': 30},
    {'t': 'بخش اول: تکالیف باوری', 's': 'hdr', 'sp': 12},
    {'t': 'الف) خداباوری', 's': 'sub', 'sp': 8},
    {'t': 'نخستین تکلیف، پذیرش موجودی متعالی به نام خداوند به عنوان آفریننده جهان و انسان است. خداباوری یعنی انسان بپذیرد موجودی تصادفی پدید نیامده و در تمام هستی هوشمندی بی‌انتها نهفته است. چنان نظمی بر عالم حاکم است که هیچ عقل سالمی نمی‌تواند آن را تصادفی بداند.', 's': 'body'},
    {'t': 'از منظر قرآن، شرک گناهی بزرگ است و خداوند هر گناهی را جز شرک می‌آمرزد. خداوند میل به خداشناسی را در فطرت آدمیان قرار داده.', 's': 'body'},
]

p2 = [
    {'t': 'قرآن در سوره عنکبوت مثالی زیبا از فطرت خداشناسی ارائه می‌دهد:', 's': 'body'},
    {'t': 'و هنگامی که بر کشتی سوار می‌شوند، خدا را پاک‌دلانه می‌خوانند، اما چون نجات یافتند، شرک می‌ورزند. (عنکبوت/۶۵)', 's': 'verse'},
    {'t': 'در روایتی از امام صادق (ع): شخصی خواست خداوند برایش اثبات شود. امام پرسید: آیا سوار کشتی شده‌ای؟ مرد گفت: آری. امام فرمود: آیا کشتی شکسته و نجات‌بخشی نیافتی؟ مرد گفت: آری. امام فرمود: آیا در دلت افتاد چیزی نجاتت دهد؟ مرد گفت: آری. امام فرمود: آن همان خداوند است.', 's': 'body', 'sp': 30},
    {'t': 'ب) معادباوری', 's': 'sub', 'sp': 8},
    {'t': 'دومین تکلیف سنگین آدمیان. مراد از معاد: مجموعه رخدادها از لحظه مرگ شامل برزخ، نفخ صور، فروپاشی عالم، اجتماع در صحرای محشر و محاسبه اعمال. انسان باید باور داشته باشد این دنیا پایان هستی نیست.', 's': 'body'},
    {'t': 'حیات برزخی:', 's': 'def'},
    {'t': 'واژه «برزخ» به معنای حد فاصل است. خداوند درباره شهیدان می‌فرماید: «هرگز کسانی را که در راه خدا کشته شده‌اند، مرده مپندار، بلکه زنده‌اند» (آل‌عمران/۱۶۹). قبر باغی از باغ‌های بهشت یا چاله‌ای از آتش است.', 's': 'body'},
    {'t': 'بهشت و جهنم:', 's': 'def'},
    {'t': 'قرآن از بهشت با عنوان «فوز عظیم» و «حیات حقیقی» یاد کرده. نعمت‌های بهشت هم معنوی (رضایت الهی) و هم مادی (باغ‌ها). جهنم برای کافران و فاسقان و عذاب آن فراتر از طاقت انسان است.', 's': 'body'},
]

p3 = [
    {'t': 'بخش دوم: تکالیف رفتاری', 's': 'hdr', 'sp': 12},
    {'t': 'الف) انجام فرایض دینی (عبودیت)', 's': 'sub', 'sp': 8},
    {'t': 'عبودیت یعنی بندگی و سرسپردگی در برابر خداوند. قرآن هدف آفرینش را عبودیت دانسته: «و جن و انس را نیافریدم جز برای آنکه مرا بپرستند» (ذاریات/۵۶).', 's': 'body'},
    {'t': 'عبادت پیامبر اکرم (ص) مثال‌زدنی بود: «ما قرآن را بر تو نفرستادیم تا خود را به زحمت اندازی» (طه/۲). حضرت علی (ع) بیشتر ساعات شب را به مناجات می‌گذراند. امام سجاد (ع) به «زین العابدین» معروف بود.', 's': 'body'},
    {'t': 'جایگاه نماز:', 's': 'def'},
    {'t': 'واژه «صلاة» بیش از ۹۰ بار در قرآن تکرار شده. «بر نمازها و نماز میانه مواظبت کنید» (بقره/۲۳۸). نماز بازدارنده از کار زشت است: «نماز از کار زشت و ناپسند باز می‌دارد» (عنکبوت/۴۵).', 's': 'body'},
    {'t': 'از زبان ابراهیم (ع): «مرا برپادارنده نماز قرار ده و از فرزندان من نیز» (ابراهیم/۴۰). از زبان عیسی (ع): «تا زنده‌ام به نماز و زکات سفارش کرده است» (مریم/۳۱).', 's': 'body', 'sp': 25},
    {'t': 'ب) ترک معاصی', 's': 'sub', 'sp': 8},
    {'t': 'انسان باید همه‌جا را محضر خداوند بداند. قرآن برای گناه واژه‌های مختلفی به کار برده: اثم، ذنب، ظلم، سیئه و عثرة.', 's': 'body'},
    {'t': 'هفت اثر مهم گناه:', 's': 'body', 'sp': 5},
    {'t': '۱. فروکاستن جایگاه انسان و مستحق لعن شدن', 's': 'body'},
    {'t': '۲. محرومیت از توفیقات علمی و اخلاقی', 's': 'body'},
    {'t': '۳. مسدود شدن راه‌های سعادت', 's': 'body'},
    {'t': '۴. ابتلا به خودفراموشی', 's': 'body'},
    {'t': '۵. از دست رفتن آبرو و اعتبار اجتماعی', 's': 'body'},
    {'t': '۶. نزول عذاب الهی در دنیا (قوم نوح، قوم لوط)', 's': 'body'},
    {'t': '۷. گرفتاری عذاب برزخ و جهنم', 's': 'body'},
]

p4 = [
    {'t': 'ریشه‌های اصلی گناه در تاریخ', 's': 'hdr', 'sp': 12},
    {'t': 'بر اساس روایت امام صادق (ع)، ریشه‌های کفر سه چیز است: حرص، تکبر و حسادت. نخستین گناه: تکبر ابلیس (سر باز زدن از سجده بر آدم). دومین گناه: حرص آدم (خوردن از درخت نهی‌شده). سومین گناه: حسادت قابیل (کشتن هابیل).', 's': 'body'},
    {'t': 'گناهان دیگر: عاق والدین، شراب‌خواری، خون‌ریزی ناحق، سخن‌چینی، قطع پیوند خویشاوندی و فساد اقتصادی. قوم لوط به دلیل گناه جنسی، قوم شعیب به دلیل کم‌فروشی و بنی‌اسرائیل به دلیل دنیاطلبی مجازات شدند. در جنگ احد طمع برخی مسلمانان باعث شکست شد.', 's': 'body', 'sp': 25},
    {'t': 'نتیجه‌گیری', 's': 'hdr', 'sp': 12},
    {'t': 'تکالیف باوری (شناخت خدا و باور به معاد) پایه زندگی معنوی انسان است. قرآن خداشناسی را امری فطری می‌داند و غفلت و دنیاطلبی را عامل کمرنگ شدن آن معرفی می‌کند.', 's': 'body'},
    {'t': 'تأکید قرآن بر آثار منفی گناه، نشان‌دهنده اهمیت تقواست. انسان با شناخت خدا، باور به معاد، انجام عبادات و دوری از گناهان می‌تواند به مقام عبودیت واقعی دست یابد و سعادت دنیا و آخرت را تضمین کند.', 's': 'body'},
    {'t': '', 's': 'body', 'sp': 35},
    {'t': 'منابع برای مطالعه:', 's': 'def'},
    {'t': '۱. حق و تکلیف در اسلام — جوادی آملی — قم: اسراء', 's': 'body'},
    {'t': '۲. حق و سیاست در قرآن — مصباح یزدی — قم: مؤسسه امام خمینی', 's': 'body'},
    {'t': '۳. نظریه حقوق اسلام — مصباح یزدی — قم: مؤسسه امام خمینی', 's': 'body'},
    {'t': '۴. دایرةالمعارف قرآن کریم — ج ۸ — قم: بوستان کتاب', 's': 'body'},
]


def main():
    print("Generating clean Vazirmatn PDF...")
    pages = [(p1, 1), (p2, 2), (p3, 3), (p4, 4)]
    imgs = []
    for content, num in pages:
        print(f"  Page {num}...")
        img = render_page(content, num)
        img.save(os.path.join(OUT, f'vazir_{num:02d}.png'), 'PNG', dpi=(300, 300))
        imgs.append(img)

    pdf = os.path.join(OUT, 'chapter_vazirmatn.pdf')
    imgs[0].save(pdf, 'PDF', save_all=True, append_images=imgs[1:], resolution=300.0)
    print(f"\n✓ PDF: {pdf}")
    print(f"✓ Size: {os.path.getsize(pdf) / 1024:.0f} KB")
    print(f"✓ Pages: {len(imgs)}")
    print(f"✓ Font: Vazirmatn (digital, no handwriting)")


if __name__ == '__main__':
    main()