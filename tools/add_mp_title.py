import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
text = text.replace("      Text(this.viewModel.curMusicModel?.title)", "      Text(this.viewModel.curMusicModel?.title)\n      .id('musicTitle')", 1)
open(p, 'w', encoding='utf-8').write(text)
print('musicTitle added')
