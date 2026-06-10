import requests
import urllib.parse
import pycountry
import os

SOURCE_URL = "https://raw.githubusercontent.com/shervinofpersia/PsiphonProxy/refs/heads/main/proxies.json"
REMARK = "☬SHΞN™🪽"   # بدون هیچ عددی

def country_name_to_flag(name):
    """تبدیل نام کشور به ایموجی پرچم (بدون عدد)"""
    if not name:
        return ""

    manual = {
        "Russian Federation": "RU",
        "Iran, Islamic Republic of": "IR",
        "United States": "US",
        "Taiwan, Province of China": "TW",
        "Korea, Republic of": "KR",
        "Czech Republic": "CZ",
        "Hong Kong": "HK",
        "Netherlands": "NL",
        "United Kingdom": "GB",
        "Kazakstan": "KZ",
        "Bahamas": "BS",
        "Macedonia": "MK",
        "Palestine, State of": "PS",
        "Viet Nam": "VN",
        "Syrian Arab Republic": "SY",
        "Lao People's Democratic Republic": "LA",
        "Republic of Moldova": "MD",
    }
    name = name.strip()
    if name in manual:
        code = manual[name]
    else:
        try:
            country = pycountry.countries.lookup(name)
            code = country.alpha_2
        except LookupError:
            try:
                matches = pycountry.countries.search_fuzzy(name)
                code = matches[0].alpha_2 if matches else ""
            except:
                code = ""
    if code:
        return "".join(chr(ord(c) + 127397) for c in code.upper())
    return ""

def interleave_lists(list1, list2):
    """آمیختن دو لیست به صورت یکی درمیان"""
    result = []
    min_len = min(len(list1), len(list2))
    for i in range(min_len):
        result.append(list1[i])
        result.append(list2[i])
    # اضافه کردن باقی‌مانده از لیست بلندتر
    if len(list1) > min_len:
        result.extend(list1[min_len:])
    elif len(list2) > min_len:
        result.extend(list2[min_len:])
    return result

def main():
    resp = requests.get(SOURCE_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    socks_lines = []
    http_lines = []

    for item in data:
        proxy_type = item.get('type', '').lower()
        ip = item.get('ip') or item.get('host')
        port = item.get('port')
        country = item.get('country', '')

        if not ip or not port:
            continue

        flag = country_name_to_flag(country)
        fragment = REMARK + flag   # فقط ریمارک و پرچم، بدون عدد
        fragment_encoded = urllib.parse.quote(fragment, safe='')

        if 'socks5' in proxy_type:
            socks_lines.append(f"socks5://{ip}:{port}#{fragment_encoded}")
        elif 'http' in proxy_type or 'https' in proxy_type:
            http_lines.append(f"http://{ip}:{port}#{fragment_encoded}")

    # چینش مخلوط (یکی درمیان)
    all_lines = interleave_lists(socks_lines, http_lines)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'ProxyNg.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_lines))

    print(f"✔️ {len(all_lines)} پروکسی در {output_path} ذخیره شد. (چینش: یک SOCKS5 و یک HTTP به نوبت)")

if __name__ == "__main__":
    main()
