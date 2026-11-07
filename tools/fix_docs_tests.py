# -*- coding: utf-8 -*-
import io, re
p = r'E:\zhikong\tools\write_docs.py'
text = io.open(p, encoding='utf-8').read()

theme_tests = """        'tests': [
            ('StartAbility_001', '拉起应用并校验首页渲染'),
            ('changeThemeDialog_001', '点击切换主题，校验主题弹窗出现'),
            ('changeToDay_001', '切换浅色主题，校验浅色主题生效'),
            ('changeToNight_001', '切换深色主题，校验深色主题生效'),
            ('changeToCustom_001', '切换自定义主题，校验自定义主题生效'),
            ('changeToDay_002', '再次切回浅色主题，校验主题可来回切换'),
        ],"""
text = re.sub(r"        'tests': \[\n            \('changeThemeDialog_001'.*?\n        \],", theme_tests, text, flags=re.S)

cert_tests = """        'tests': [
            ('StartAbility_001', '拉起应用'),
            ('DisplayData_001', '点击展示数据，校验证书/原文/签名数据正确显示'),
            ('Verify_001', '点击签名校验，校验提示「校验通过」'),
            ('ModifyOriginData_001', '篡改原文后校验签名数据仍正确、原文已变化'),
            ('ModifySignatureData_001', '篡改签名数据后校验失败'),
            ('Verify_002', '二次签名校验'),
            ('Verify_003', '三次签名校验'),
            ('Verify_004', '四次签名校验'),
            ('CertChain_001', '证书链解析校验'),
            ('CertChain_002', '证书链二次解析校验'),
        ],"""
text = re.sub(r"        'tests': \[\n            \('StartAbility_001', '拉起应用'\),\n            \('DisplayData_001'.*?\n        \],", cert_tests, text, flags=re.S)
io.open(p, 'w', encoding='utf-8', newline='\n').write(text)
print('updated')
