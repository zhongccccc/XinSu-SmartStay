import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\README_zh.md'
t = io.open(p, encoding='utf-8').read()
old = "- 重写 UI 用例（14 条）并补充日期时间与时长格式化的逻辑用例（7 条）。"
new = ("- 重写 UI 用例（14 条）并补充日期时间与时长格式化的逻辑用例（7 条）。\n"
       "- 列表与页面切换优化：录音列表使用稳定 key，内容未变化时不再整表重建；Preferences 与目录查询复用单例；"
       "录音页、播放页首帧即渲染标题，避免异步加载造成的布局跳动。")
assert old in t
t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)

p2 = r'D:\XTS\code\SystemFeature\Media\Recorder\README.md'
t2 = io.open(p2, encoding='utf-8').read()
if 'stable list keys' not in t2:
    marker = "## API 26.0.0 Adaptation"
    add = (marker + "\n\n- UI smoothness: the recording list uses stable keys and skips rebuilding when the data is unchanged; "
           "a single Preferences instance is reused; the record and play pages render their titles on the first frame "
           "to avoid layout jumps caused by asynchronous loading.")
    t2 = t2.replace(marker, add, 1)
    io.open(p2, 'w', encoding='utf-8', newline='\n').write(t2)
print('readme updated')
