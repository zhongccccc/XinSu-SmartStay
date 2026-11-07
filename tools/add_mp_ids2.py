import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
text = text.replace("""          },
          needBackground: true
        });""", """          },
          needBackground: true,
          btnId: 'playBtn'
        });""")
text = text.replace("""        this.ctrlBtnBuilder({
          imgSrc: $r('app.media.foldable_screen_cases_play_next'),
          btnSize: CommonConstants.MUSIC_PLAYER_CTRL_BTN_SIZE_COMMON,
          callback: () => {
            this.viewModel.playNext();
          }
        });""", """        this.ctrlBtnBuilder({
          imgSrc: $r('app.media.foldable_screen_cases_play_next'),
          btnSize: CommonConstants.MUSIC_PLAYER_CTRL_BTN_SIZE_COMMON,
          callback: () => {
            this.viewModel.playNext();
          },
          btnId: 'nextBtn'
        });""")
open(p, 'w', encoding='utf-8').write(text)
print('playBtn:', text.count("'playBtn'"), 'nextBtn:', text.count("'nextBtn'"))
