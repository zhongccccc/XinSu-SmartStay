# -*- coding: utf-8 -*-
import io

PATH = r'D:\XTS\code\SystemFeature\Security\CertificateFramework\README.md'
text = io.open(PATH, encoding='utf-8').read()
start = text.find('2. This sample has been adapted')
end = text.find('## API 26.0.0 Adaptation')
assert start != -1 and end != -1

new_block = '''2. This sample has been adapted to OpenHarmony API 26.0.0 (compileSdkVersion / compatibleSdkVersion / targetSdkVersion = 26.0.0). The hvigor version and modelVersion are fixed to 26.0.0, so the previous SDK-version switching workaround is no longer required.

3. This sample requires DevEco Studio (Build Version: DS-261.23567.138.36.2600851) or later to compile and run.

4. This sample requires no permission and no Full SDK.

'''
text = text[:start] + new_block + text[end:]
io.open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
print('cert english updated')
