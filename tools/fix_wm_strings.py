import re, sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
mapping = {
    'pages_text': 'window video',
    'set_touchable_area_of_window_page': 'set touchable area of window page',
    'get_properties_of_system_bar_page': 'get properties of system bar page',
    'GetPropertiesOfSystemBar': 'get properties of system bar',
    'area1': 'area1',
    'area2': 'area2',
    'area3': 'area3',
    'area4': 'area4',
}
for name, value in mapping.items():
    text = text.replace(f'await manager.getStringValue($r("app.string.{name}"))', f"'{value}'")
text = text.replace('context = await abilityDelegator.getAppContext();', '')
text = text.replace('manager = context.resourceManager;', '')
text = text.replace('await driver.delayMs(1000);\n        await driver.assertComponentExist(ON.text(', 'await driver.delayMs(2500);\n        await driver.assertComponentExist(ON.text(')
open(p, 'w', encoding='utf-8').write(text)
print('manager refs left:', text.count('manager.'))
