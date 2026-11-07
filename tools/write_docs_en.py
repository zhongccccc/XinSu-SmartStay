# -*- coding: utf-8 -*-
import io
import os

ROOT = r'D:\XTS\code\SystemFeature'

PROJECTS = [
    {
        'dir': r'Media\GamePuzzle',
        'name': 'GamePuzzle',
        'bundle': 'ohos.samples.gamepuzzle',
        'changes': [
            'Replaced the removed `@ohos.filemanagement.userFileManager` with `photoAccessHelper.getAssets` and `dataSharePredicates`.',
            'Replaced the removed `PhotoAsset.open()` with `fileIo.open(uri, READ_ONLY)`.',
            'Migrated `srcEntrance`/`visible` to `srcEntry`/`exported` and completed the API 26 project configuration.',
            'The debug signing profile uses `system_basic` with ACLs for `READ_IMAGEVIDEO` and `MEDIA_LOCATION`.',
        ],
    },
    {
        'dir': r'Security\CertificateFramework',
        'name': 'CertificateFramework',
        'bundle': 'com.samples.certframework',
        'changes': [
            'Completed the API 26 project configuration (SDK versions, hvigorfile, hvigor-config, oh-package, local.properties) and embedded debug signing.',
            'Unified the test entry to `testrunner/OpenHarmonyTestRunner.ts` + `testability`.',
            'Added logic cases for certificate parsing, data display and tamper verification.',
        ],
    },
    {
        'dir': r'Media\Recorder',
        'name': 'Recorder',
        'bundle': 'ohos.samples.recorder',
        'changes': [
            'The audio capabilities of `@ohos.filemanagement.userFileManager` were removed in API 26, so recordings are now stored in the sandbox directory `filesDir/records` and managed with `fileIo`.',
            'Replaced `PhotoAsset.open/close` with `fileIo.open/close`; recording and playback use file descriptors (`fd://`).',
            'Removed the system permissions `READ_MEDIA`, `WRITE_MEDIA`, `READ_AUDIO` and `WRITE_AUDIO`; only `ohos.permission.MICROPHONE` remains.',
        ],
    },
    {
        'dir': r'Media\MusicPlayer',
        'name': 'MusicPlayer',
        'bundle': 'com.samples.musicplayer',
        'changes': [
            'Switched the runtime from HarmonyOS to OpenHarmony (`runtimeOS: OpenHarmony`) and added `compileSdkVersion`/`targetSdkVersion` 26.0.0.',
            'Adjusted `deviceTypes` to `default`/`tablet` to avoid an empty system-capability intersection.',
            'Added component ids (`musicTitle`, `playBtn`, `nextBtn`, `prevBtn`, `loopModeBtn`) for UI automation.',
            'Added `testability`, `testrunner`, test resources and real test cases (the original project only had template cases).',
        ],
    },
]

SECTION = '''## API 26.0.0 Adaptation

This project has been adapted to OpenHarmony SDK 26.0.0 (`compileSdkVersion` / `compatibleSdkVersion` / `targetSdkVersion` are `26.0.0`, `runtimeOS` is `OpenHarmony`).
Open it with DevEco Studio and run it directly; the debug signing material (`signature/`) and SDK configuration are already embedded, so no manual configuration dialog is required.

### Key changes

{changes}

### Build & Run

1. Open the project root with DevEco Studio (build `DS-261.23567.138.36.2600851` or later);
2. Wait until Sync finishes;
3. Select the `entry` module and a connected device, then click Run.

### Test

```bash
hdc shell aa test -b {bundle} -m entry_test -s unittest OpenHarmonyTestRunner
```

The case list (UI + logic) is available in [ohosTest.md](./ohosTest.md).
'''


def write(path, content):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


for proj in PROJECTS:
    path = os.path.join(ROOT, proj['dir'], 'README.md')
    if not os.path.exists(path):
        continue
    with io.open(path, encoding='utf-8', errors='replace') as f:
        old = f.read()
    changes = '\n'.join('- ' + c for c in proj['changes'])
    section = SECTION.format(changes=changes, bundle=proj['bundle']).strip()
    marker = '## API 26.0.0 Adaptation'
    if marker in old:
        old = old[:old.index(marker)].rstrip() + '\n\n' + section + '\n'
    else:
        old = old.rstrip() + '\n\n' + section + '\n'
    write(path, old)
    print('updated', proj['name'])
