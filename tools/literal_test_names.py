# -*- coding: utf-8 -*-
"""把测试用例名从模板字符串/字符串拼接改为纯字面量，避免静态解析时被判为同名。"""
import io

FILES = [
    (r'D:\XTS\code\SystemFeature\Media\GamePuzzle\entry\src\ohosTest\ets\test\Ability.test.ets', [
        ("it(`${BUNDLE}_StartAbility_001`", "it('ohos.samples.gamepuzzle_StartAbility_001'"),
        ("it(`${BUNDLE}_StartGame_001`", "it('ohos.samples.gamepuzzle_StartGame_001'"),
        ("it(`${BUNDLE}_Restart_001`", "it('ohos.samples.gamepuzzle_Restart_001'"),
    ]),
    (r'D:\XTS\code\SystemFeature\Notification\Publish\entry\src\ohosTest\ets\test\Ability.test.ets', [
        ("it(BUNDLE + '_StartAbility_001'", "it('com.samples.notificationpublish_StartAbility_001'"),
        ("it(BUNDLE + '_PublishNotification_001'", "it('com.samples.notificationpublish_PublishNotification_001'"),
    ]),
    (r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\ohosTest\ets\test\Ability.test.ets', [
        ("it(BUNDLE + 'StartAbility_001'", "it('Recorder_StartAbility_001'"),
        ("it(BUNDLE + 'RecordPage_001'", "it('Recorder_RecordPage_001'"),
        ("it(BUNDLE + 'FinishRecord_001'", "it('Recorder_FinishRecord_001'"),
    ]),
    (r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\entry\src\ohosTest\ets\test\Ability.test.ets', [
        ("it(BUNDLE + 'StartAbility_001'", "it('WindowManager_StartAbility_001'"),
        ("it(BUNDLE + 'GetPropertiesOfSystemBarPage_001'", "it('WindowManager_GetPropertiesOfSystemBarPage_001'"),
        ("it(BUNDLE + 'SetTouchableAreas_001'", "it('WindowManager_SetTouchableAreas_001'"),
        ("it(BUNDLE + 'OpenVideoPage_001'", "it('WindowManager_OpenVideoPage_001'"),
    ]),
    (r'D:\XTS\code\SystemFeature\Media\VoiceCallDemo\entry\src\ohosTest\ets\test\App.test.ets', [
        ("it(BUNDLE_NAME + 'StartAbility_001'", "it('com.samples.voicecalldemoStartAbility_001'"),
    ]),
    (r'D:\XTS\code\SystemFeature\Media\MusicPlayer\entry\src\ohosTest\ets\test\Ability.test.ets', [
        ("it(BUNDLE + '_StartAbility_001'", "it('com.samples.musicplayer_StartAbility_001'"),
        ("it(BUNDLE + '_PlayNext_001'", "it('com.samples.musicplayer_PlayNext_001'"),
        ("it(BUNDLE + '_PlayPause_001'", "it('com.samples.musicplayer_PlayPause_001'"),
        ("it(BUNDLE + '_LoopMode_001'", "it('com.samples.musicplayer_LoopMode_001'"),
    ]),
]

for path, pairs in FILES:
    text = io.open(path, encoding='utf-8').read()
    for old, new in pairs:
        if old not in text:
            print('MISS', path.split('\\')[-3], old)
        text = text.replace(old, new)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    print('patched', path.split('\\')[-3])
