import requests
import json
import urllib.parse
import pycountry
import os

# لینک منبع
SOURCE_URL = "https://raw.githubusercontent.com/shervinofpersia/PsiphonProxy/refs/heads/main/proxies.json"
# ریمارک ثابت (بدون URL encode)
REMARK = "☬SHΞN™🪽"

def country_name_to_flag(name):
    """تبدیل نام کشور به ایموجی پرچم با استفاده از pycountry و اصلاحات دستی"""
    # اصلاحات دستی برای مواردی که pycountry نمی‌شناسد
    manual_map = {
        "Russian Federation": "RU",
        "Iran, Islamic Republic of": "IR",
        "United States": "US",
        "Taiwan, Province of China": "TW",
        "Korea, Republic of": "KR",
        "Czech Republic": "CZ",
        "Hong Kong": "HK",
        "Netherlands": "NL",
        "United Kingdom": "GB",
        "Kazakstan": "KZ",          # املای نادرست در داده‌ها
        "Bahamas": "BS",
        "Macedonia": "MK",
        "Palestine, State of": "PS",
    }
    name = name.strip()
    if name in manual_map:
        code = manual_map[name]
    else:
        try:
            country = pycountry.countries.lookup(name)
            code = country.alpha_2
        except LookupError:
            try:
                # جستجوی فازی
                matches = pycountry.countries.search_fuzzy(name)
                code = matches[0].alpha_2 if matches else ""
            except Exception:
                code = ""
    if code:
        # تبدیل کد دوحرفی به ایموجی پرچم (A => 🇦)
        return ''.join(chr(ord(c) + 127397) for c in code.upper())
    return ""

def generate_fragment(country_flag):
    """ساخت بخش #... با ریمارک + پرچم و URL-encode کامل"""
    fragment = REMARK + country_flag
    return urllib.parse.quote(fragment, safe='')

def main():
    # دانلود JSON
    resp = requests.get(SOURCE_URL)
    resp.raise_for_status()
    data = resp.json()

    socks_lines = []
    http_lines = []

    for item in data:
        proxy_type = (item.get('type', '')).lower()
        ip = item.get('ip') or item.get('host')
        port = item.get('port')
        country = item.get('country', '')

        if not ip or not port:
            continue

        flag = country_name_to_flag(country) if country else ""
        fragment = generate_fragment(flag)

        # پروکسی‌های SOCKS5 (حتی اگر SOCKS4, SOCKS5 ترکیبی باشد)
        if 'socks5' in proxy_type:
            socks_lines.append(f"socks5://{ip}:{port}#{fragment}")
        elif 'http' in proxy_type or 'https' in proxy_type:
            # برای http و https از http استفاده می‌کنیم (طبق نمونه)
            scheme = 'http'
            http_lines.append(f"{scheme}://{ip}:{port}#{fragment}")

    # ادغام (اول SOCKS5 سپس HTTP)
    all_lines = socks_lines + http_lines

    # ذخیره‌سازی در کنار همین فایل
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'ProxyNg.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_lines))

    print(f"✔️ {len(all_lines)} پروکسی در {output_path} ذخیره شد.")

if __name__ == "__main__":
    main()
