# -*- coding: utf-8 -*-
import io

# GamePuzzle: ImageModel.ts -> ImageModel.ets
gp = r'D:\XTS\code\SystemFeature\Media\GamePuzzle\README_zh.md'
t = io.open(gp, encoding='utf-8').read()
t = t.replace('|---ImageModel.ts                       // 图片操作', '|---ImageModel.ets                      // 图片操作')
io.open(gp, 'w', encoding='utf-8', newline='\n').write(t)
print('gamepuzzle tree fixed')

# MusicPlayer: MusicPlayerViewModel.ets -> MusicPlayViewModel.ets
for path in (r'D:\XTS\code\SystemFeature\Media\MusicPlayer\README.md',
             r'D:\XTS\code\SystemFeature\Media\MusicPlayer\README_zh.md'):
    t = io.open(path, encoding='utf-8').read()
    t = t.replace('MusicPlayerViewModel.ets', 'MusicPlayViewModel.ets')
    io.open(path, 'w', encoding='utf-8', newline='\n').write(t)
    print('musicplayer tree fixed:', path.split('\\')[-1])
