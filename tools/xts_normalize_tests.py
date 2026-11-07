# -*- coding: utf-8 -*-
"""按 XTS 编码规范改造测试用例：@tc 注释、命名、过滤参数、TAG、起止日志。"""
import io
import os
import re

ROOT = r'D:\XTS\code\SystemFeature'

# 每个工程：目录、短前缀（用于 @tc.name / @tc.number）、用例映射（旧名 -> (动作, 英文描述)）
PROJECTS = [
    {
        'dir': r'Notification\Publish',
        'short': 'Publish',
        'num': 'SUB_PUBLISH',
        'files': {
            'Ability.test.ets': [
                ('com.samples.notificationpublish_StartAbility_001', 'StartAbility',
                 'Start the app and verify the main page is displayed.'),
                ('com.samples.notificationpublish_PublishNotification_001', 'PublishNotification',
                 'Publish a notification and verify the preview card is displayed.'),
            ],
            'PublishLogic.test.ets': [
                ('Publish_Request_Basic_001', 'RequestBasic',
                 'Verify the notification request id and slot type.'),
                ('Publish_Request_Content_001', 'RequestContent',
                 'Verify the notification content type, title and text.'),
                ('Publish_Request_AdditionalText_001', 'RequestAdditional',
                 'Verify the additional text is passed through.'),
                ('Publish_Request_Independent_001', 'RequestIndependent',
                 'Verify each notification request is an independent object.'),
            ],
        },
    },
    {
        'dir': r'ResourceAllocation\ApplicationThemeSwitch',
        'short': 'ThemeSwitch',
        'num': 'SUB_THEME_SWITCH',
        'files': {
            'Ability.test.ets': [
                ('StartAbility_001', 'StartAbility', 'Start the app and verify the home page.'),
                ('changeThemeDialog_001', 'ChangeThemeDialog', 'Open the theme menu and verify the options.'),
                ('changeToDay_001', 'ChangeToDay', 'Switch to the day theme and verify it takes effect.'),
                ('changeToNight_001', 'ChangeToNight', 'Switch to the night theme and verify it takes effect.'),
                ('changeToCustom_001', 'ChangeToCustom', 'Switch to the custom theme and verify it takes effect.'),
                ('changeToDay_002', 'BackToDay', 'Switch back to the day theme and verify it takes effect.'),
            ],
            'ThemeSwitchLogic.test.ets': [
                ('ThemeSwitch_GetTheme_Custom_001', 'GetThemeCustom',
                 'Verify the custom theme is selected by theme index.'),
                ('ThemeSwitch_GetTheme_Default_001', 'GetThemeDefault',
                 'Verify the default theme is selected by theme index.'),
                ('ThemeSwitch_ThemeRes_Diff_001', 'ThemeResDiff',
                 'Verify theme resources differ between the two themes.'),
                ('ThemeSwitch_ThemeFields_Defined_001', 'ThemeFields',
                 'Verify all theme resource fields are defined.'),
                ('ThemeSwitch_DefaultSelectedColor_001', 'DefaultColor',
                 'Verify the selected color of the default theme.'),
            ],
        },
    },
    {
        'dir': r'Media\GamePuzzle',
        'short': 'GamePuzzle',
        'num': 'SUB_GAME_PUZZLE',
        'files': {
            'Ability.test.ets': [
                ('ohos.samples.gamepuzzle_StartAbility_001', 'StartAbility', 'Start the app.'),
                ('ohos.samples.gamepuzzle_GetPermission_001', 'GetPermission',
                 'Grant the media permission.'),
                ('ohos.samples.gamepuzzle_EnsureImages_001', 'EnsureImages',
                 'Verify an image is available for the puzzle.'),
                ('ohos.samples.gamepuzzle_StartAbility_002', 'StartAgain',
                 'Start the app again and verify it is alive.'),
                ('CheckIndexPage_001', 'CheckIndexPage', 'Verify the index page elements.'),
                ('StartGame_001', 'StartGame', 'Start the game and verify the countdown.'),
                ('ChangePhoto_001', 'ChangePhoto', 'Change the photo and verify the timer reset.'),
                ('StartGame_002', 'StartGameAgain', 'Start the game again and verify the countdown.'),
                ('GameOver_001', 'GameOver', 'Simulate puzzle completion and verify the dialog.'),
                ('StartGame_003', 'StartGameThird', 'Start the game after completion and verify it.'),
                ('GameFailed_003', 'GameFailed', 'Simulate timeout and verify the dialog.'),
            ],
            'GamePuzzleLogic.test.ets': [
                ('GamePuzzle_FindEmptyIndex_001', 'FindEmptyIndex',
                 'Verify the empty cell lookup result.'),
                ('GamePuzzle_ItemChange_001', 'ItemChange',
                 'Verify the swap moves the empty cell to the clicked position.'),
                ('GamePuzzle_GameBegin_001', 'GameBegin',
                 'Verify the shuffle keeps all indices without duplication.'),
                ('GamePuzzle_GameInit_NotStarted_001', 'GameInitIdle',
                 'Verify a click is ignored before the game starts.'),
                ('GamePuzzle_GameInit_Started_001', 'GameInitActive',
                 'Verify an adjacent cell moves after the game starts.'),
            ],
        },
    },
    {
        'dir': r'WindowManagement\WindowManage',
        'short': 'WindowManage',
        'num': 'SUB_WINDOW_MANAGE',
        'files': {
            'Ability.test.ets': [
                ('WindowManager_StartAbility_001', 'StartAbility',
                 'Start the app and verify the index page entries.'),
                ('WindowManager_OpenGetPropertiesOfSystemBarPage_001', 'OpenSystemBar',
                 'Open the system bar properties page and verify the button.'),
                ('WindowManager_GetPropertiesOfSystemBarPage_001', 'GetSystemBar',
                 'Get the system bar properties and verify the text is not empty.'),
                ('WindowManager_OpenSetTouchableAreasPage_001', 'OpenTouchable',
                 'Open the touchable areas page and verify the areas.'),
                ('WindowManager_SetTouchableAreas_001', 'TouchArea1',
                 'Tap area1 and verify the toast is displayed.'),
                ('WindowManager_TouchArea2_001', 'TouchArea2',
                 'Tap area2 and verify the page stays available.'),
                ('WindowManager_TouchArea4_001', 'TouchArea4',
                 'Tap area4 and verify the toast is displayed.'),
                ('WindowManager_BackToIndex_001', 'BackToIndex', 'Return to the index page.'),
                ('WindowManager_OpenVideoPage_001', 'OpenVideo',
                 'Open the video page and verify the window button.'),
                ('WindowManager_VideoPage_001', 'VideoPage', 'Verify the video page elements.'),
                ('WindowManager_WindowBtn_001', 'WindowBtn',
                 'Tap the window button and verify the page stays available.'),
                ('WindowManager_MainVideoClick_001', 'MainVideoClick',
                 'Tap the main video and verify it is still displayed.'),
                ('WindowManager_VideoBack_001', 'VideoBack',
                 'Close the sub window and return to the previous page.'),
            ],
            'WindowManageLogic.test.ets': [
                ('WindowManage_EventId_001', 'EventId',
                 'Verify the sub window event id constant.'),
                ('WindowManage_WindowColor_001', 'WindowColor',
                 'Verify the system bar color constants.'),
                ('WindowManage_WindowType_001', 'WindowType',
                 'Verify the window attribute structure.'),
                ('WindowManage_FormatProperties_001', 'FormatProperties',
                 'Verify the system bar properties formatting.'),
            ],
        },
    },
    {
        'dir': r'Security\CertificateFramework',
        'short': 'CertFramework',
        'num': 'SUB_CERT_FRAMEWORK',
        'files': {
            'Ability.test.ets': [
                ('StartAbility_001', 'StartAbility', 'Start the app.'),
                ('DisplayData_001', 'DisplayData', 'Display the certificate data and verify it.'),
                ('Verify_001', 'Verify1', 'Verify the signature and check the success toast.'),
                ('ModifyOriginData_001', 'ModifyOrigin', 'Modify the origin data and verify it.'),
                ('ModifySignatureData_001', 'ModifySignature', 'Modify the signature data and verify it.'),
                ('Verify_002', 'Verify2', 'Verify the signature again.'),
                ('Verify_003', 'Verify3', 'Verify the signature for the third time.'),
                ('Verify_004', 'Verify4', 'Verify the signature for the fourth time.'),
                ('CertChain_001', 'CertChain1', 'Parse the certificate chain and verify it.'),
                ('CertChain_002', 'CertChain2', 'Parse the certificate chain again.'),
            ],
            'CertFrameworkLogic.test.ets': [
                ('Cert_StringToUint8Array_001', 'StringToBytes',
                 'Verify the string to byte array conversion.'),
                ('Cert_StringToUint8Array_002', 'EmptyString',
                 'Verify an empty string returns null.'),
                ('Cert_CreateX509Cert_001', 'CreateX509',
                 'Verify the certificate parsing and public key export.'),
                ('Cert_DataDisplay_001', 'DataDisplay', 'Verify the data display fields.'),
                ('Cert_ModifyOriginData_001', 'ModifyOriginData', 'Verify the modified origin data.'),
                ('Cert_ModifySignatureData_001', 'ModifySignatureData',
                 'Verify the modified signature data.'),
                ('Cert_ChainDataDisplay_001', 'ChainData', 'Verify the chain display data.'),
                ('Cert_CreateX509CertChain_001', 'CreateChain', 'Verify the certificate chain creation.'),
            ],
        },
    },
    {
        'dir': r'Media\VoiceCallDemo',
        'short': 'VoiceCall',
        'num': 'SUB_VOICE_CALL',
        'files': {
            'App.test.ets': [
                ('com.samples.voicecalldemoStartAbility_001', 'StartAbility',
                 'Start the app and grant the microphone permission.'),
                ('Switch_window_001', 'SwitchWindow',
                 'Switch to the call page and tap the float window button.'),
                ('com.samples.voicecalldemoStartAbility_002', 'StartVoicePage',
                 'Switch to the voice page and verify the timer.'),
                ('Answer_001', 'Answer', 'Answer the call and verify the timer.'),
                ('Hangup_001', 'Hangup', 'Hang up and verify the call page is closed.'),
            ],
            'VoiceCallLogic.test.ets': [
                ('VoiceCall_TimeUtil_Invalid_001', 'TimeInvalid',
                 'Verify the placeholder for an invalid duration.'),
                ('VoiceCall_TimeUtil_Minute_001', 'TimeMinute',
                 'Verify the duration format shorter than one hour.'),
                ('VoiceCall_TimeUtil_Hour_001', 'TimeHour',
                 'Verify the duration format longer than one hour.'),
                ('VoiceCall_TimeUtil_FixZero_001', 'TimeFixZero', 'Verify the zero padding.'),
                ('VoiceCall_IpUtils_001', 'IpAddress', 'Verify the IP address conversion.'),
                ('VoiceCall_ArrayBufferUtils_Bytes_001', 'BufferBytes',
                 'Verify the byte array conversion.'),
                ('VoiceCall_ArrayBufferUtils_String_001', 'BufferString',
                 'Verify the string conversion.'),
            ],
        },
    },
    {
        'dir': r'Media\Recorder',
        'short': 'Recorder',
        'num': 'SUB_RECORDER',
        'files': {
            'Ability.test.ets': [
                ('Recorder_StartAbility_001', 'StartAbility', 'Start the app.'),
                ('Recorder_RequestPermissionFunction_001', 'RequestPermission',
                 'Grant the microphone permission.'),
                ('Recorder_RecordePage_001', 'EnterRecordPage', 'Enter the recording page.'),
                ('Recorder_RecordePage_002', 'RecordTimer', 'Verify the recording timer changes.'),
                ('Recorder_RecordePage_003', 'RecordControls',
                 'Verify the pause and finish buttons.'),
                ('Recorder_Play_001', 'PlayRecording',
                 'Finish the recording and play it.'),
                ('Recorder_RE_Recorde_001', 'RecordAgain', 'Record again.'),
                ('Recorder_Del_Recorde_001', 'FinishRecording',
                 'Finish the recording and return to the list.'),
                ('Recorder_RE_Recorde_002', 'RecordThird',
                 'Record for the third time and finish it.'),
                ('Recorder_CheckState_001', 'CheckState',
                 'Long press an item to enter the check state.'),
                ('Recorder_DeleteRecord_001', 'DeleteDialog',
                 'Open the delete dialog and cancel it.'),
                ('Recorder_Del_All_001', 'ExitCheck', 'Exit the check state.'),
                ('Recorder_SlideAudioItem_001', 'SlideItem',
                 'Swipe the item to show the actions.'),
                ('Recorder_RenameRepeat_001', 'RenameDialog',
                 'Open the rename dialog and cancel it.'),
            ],
            'RecorderLogic.test.ets': [
                ('Recorder_DateTimeUtil_Fill_001', 'FillNumber',
                 'Verify the zero padding helper.'),
                ('Recorder_DateTimeUtil_ConcatDate_001', 'ConcatDate',
                 'Verify the date concatenation.'),
                ('Recorder_DateTimeUtil_ConcatTime_001', 'ConcatTime',
                 'Verify the time concatenation.'),
                ('Recorder_DurationString_001', 'DurationShort',
                 'Verify the duration format shorter than one hour.'),
                ('Recorder_DurationString_002', 'DurationLong',
                 'Verify the duration format longer than one hour.'),
                ('Recorder_UpdateTime_001', 'UpdateTime', 'Verify the recording timer format.'),
                ('Recorder_TimeString_001', 'TimeString',
                 'Verify the playback progress format.'),
            ],
        },
    },
    {
        'dir': r'Media\MusicPlayer',
        'short': 'MusicPlayer',
        'num': 'SUB_MUSIC_PLAYER',
        'files': {
            'Ability.test.ets': [
                ('com.samples.musicplayer_StartAbility_001', 'StartAbility',
                 'Start the app and verify the player information.'),
                ('com.samples.musicplayer_PlayNext_001', 'PlayNext',
                 'Play the next song and verify the title changes.'),
                ('com.samples.musicplayer_PlayPause_001', 'PlayPause',
                 'Play and pause the song and verify the page stays available.'),
                ('com.samples.musicplayer_LoopMode_001', 'LoopMode',
                 'Switch the loop mode and verify the page stays available.'),
            ],
            'MusicPlayerLogic.test.ets': [
                ('MusicPlayer_MusicList_Count_001', 'ListCount',
                 'Verify the music list size.'),
                ('MusicPlayer_MusicList_Content_001', 'ListContent',
                 'Verify the music list fields.'),
                ('MusicPlayer_PlayerState_001', 'PlayerState',
                 'Verify the player state constants.'),
                ('MusicPlayer_SliderRange_001', 'SliderRange',
                 'Verify the slider range constants.'),
            ],
        },
    },
]


def upper_snake(name):
    s = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
    return s.upper()


def transform_file(path, project, file_cases, index_start):
    text = io.open(path, encoding='utf-8').read()
    # 1) 补充 hypium 导入
    m = re.search(r"import \{([^}]+)\} from '@ohos/hypium';", text)
    if m:
        names = [n.strip() for n in m.group(1).split(',') if n.strip()]
        for extra in ('TestType', 'Size', 'Level'):
            if extra not in names:
                names.append(extra)
        text = text[:m.start()] + "import { " + ', '.join(names) + " } from '@ohos/hypium';" + text[m.end():]

    idx = index_start
    for old_name, action, desc in file_cases:
        new_name = '{}{}Test{:04d}'.format(project['short'], action, idx)
        tc_number = '{}_{}_{:04d}'.format(project['num'], upper_snake(action), idx * 100)
        # 2) 找到 it 行
        pattern = re.compile(
            r"^(\s*)it\('" + re.escape(old_name) + r"',\s*0,\s*(async\s*\(done: Function\)|\(\))\s*=>\s*\{",
            re.M)
        mm = pattern.search(text)
        if not mm:
            print('  MISS it:', old_name)
            idx += 1
            continue
        indent = mm.group(1)
        body_indent = indent + '  '
        is_async = mm.group(2).startswith('async')
        signature = (
            "it('{}', TestType.FUNCTION | Size.MEDIUMTEST | Level.LEVEL0,\n"
            "{}{} => {{".format(
                new_name,
                indent,
                'async (done: () => void): Promise<void>' if is_async else '()'
            )
        )
        header = (
            "/**\n"
            "{i} * @tc.number    {num}\n"
            "{i} * @tc.name      {name}\n"
            "{i} * @tc.desc      {desc}\n"
            "{i} * @tc.size      MediumTest\n"
            "{i} * @tc.type      Function\n"
            "{i} * @tc.level     Level 0\n"
            "{i} */\n"
            "{i}{sig}".format(i=indent, num=tc_number, name=new_name, desc=desc, sig=signature)
        )
        text = text[:mm.start()] + header + text[mm.end():]

        # 3) 在 it 块结束前插入结束日志
        close_pattern = re.compile(r"^" + re.escape(indent) + r"\}\)", re.M)
        cm = close_pattern.search(text, mm.start() + len(header))
        if cm:
            insert = "{i}  console.log(TAG + ' end');\n".format(i=indent)
            text = text[:cm.start()] + insert + text[cm.start():]
        # 4) 在块开始处插入 TAG 与开始日志
        open_pos = text.find('{', mm.start() + len(header))
        # 找 header 内 signature 的 { 位置
        sig_pos = text.find(signature, mm.start())
        brace_pos = text.find('{', sig_pos + len(signature) - 1)
        insert2 = "\n{i}const TAG = '{name}';\n{i}console.log(TAG + ' start');".format(
            i=body_indent, name=new_name)
        text = text[:brace_pos + 1] + insert2 + text[brace_pos + 1:]
        idx += 1
    io.open(path, 'w', encoding='utf-8', newline='\n').write(text)
    return idx


total_start = 1
for project in PROJECTS:
    base = os.path.join(ROOT, project['dir'])
    tdir = os.path.join(base, 'entry', 'src', 'ohosTest', 'ets', 'test')
    print('==', project['short'])
    index = 1
    for fname, cases in project['files'].items():
        path = os.path.join(tdir, fname)
        index = transform_file(path, project, cases, index)
    print('   cases:', index - 1)
