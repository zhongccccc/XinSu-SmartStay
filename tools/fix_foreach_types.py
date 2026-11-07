import re
import sys
from pathlib import Path

TYPES = {
    'SEARCH_TEXT_DATA': 'SearchTextModel',
    'FIND_SEARCH_TEXT_DATA': 'SearchTextModel',
    'NAVIGATION_DATA': 'NavigationDataModel',
    'NAV_DATA': 'NavDataModel',
    'SWIPER_DATA': 'SwiperModel',
    'INDEX_DATA': 'SwiperModel',
    'TITLE_BAR_DATA': 'TitleBarModel',
    'NEW_PRODUCT_TITLE_BAR_DATA': 'NewProductTitleBarModel',
    'PRODUCT_DATA': 'ProductDataModel',
    'TAB_TITLE_DATA': 'TabTitleModel',
    'FAVOR_LIVE_LIST_DATA': 'FavorLiveListsModel',
    'ORDER_DATA': 'OrderModel',
    'SHOP_CART_ITEM_DATA': 'ShopCartItemDataModel',
}

changed_total = 0
for root in sys.argv[1:]:
    for p in Path(root).rglob('*.ets'):
        if 'oh_modules' in str(p) or '\\build\\' in str(p):
            continue
        text = p.read_text(encoding='utf-8')
        original = text
        for name, tname in TYPES.items():
            text = re.sub(rf'ForEach\({name},\s*item\s*=>', f'ForEach({name}, (item: {tname}) =>', text)
            text = re.sub(rf'\}}\s*,\s*item\s*=>\s*item\.', f'}}, (item: {tname}) => item.', text)
        text = text.replace('onPortrait(mediaQueryResult)', 'onPortrait(mediaQueryResult: mediaquery.MediaQueryResult)')
        text = text.replace('private smListener: any', 'private smListener: mediaquery.MediaQueryListener')
        text = text.replace('private mdListener: any', 'private mdListener: mediaquery.MediaQueryListener')
        text = text.replace('private lgListener: any', 'private lgListener: mediaquery.MediaQueryListener')
        if text != original:
            p.write_text(text, encoding='utf-8')
            changed_total += 1
print(f'updated files: {changed_total}')
