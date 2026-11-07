import sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
# 1) builder 增加 id 字段并绑定
text = text.replace("""interface CtrlBtnBuilderParam {
  imgSrc: Resource,
  btnSize: number,
  callback: Function,
  needBackground?: boolean
}""", """interface CtrlBtnBuilderParam {
  imgSrc: Resource,
  btnSize: number,
  callback: Function,
  needBackground?: boolean,
  btnId?: string
}""")
text = text.replace("""    .backgroundColor($$.needBackground ? Color.Gray : '#00000000')
    .padding($$.needBackground ? $r('app.integer.foldable_screen_cases_btn_ctrl_padding') : 0)""", """    .backgroundColor($$.needBackground ? Color.Gray : '#00000000')
    .padding($$.needBackground ? $r('app.integer.foldable_screen_cases_btn_ctrl_padding') : 0)
    .id($$.btnId ?? 'ctrlBtn')""")
# 2) 为四个按钮补 id
text = text.replace("""        this.ctrlBtnBuilder({
          imgSrc: this.loopModeResArr[this.viewModel.curLoopMode],
          btnSize: CommonConstants.MUSIC_PLAYER_CTRL_BTN_SIZE_COMMON,
          callback: () => {
            this.viewModel.updateLoopMode();
          }
        });""", """        this.ctrlBtnBuilder({
          imgSrc: this.loopModeResArr[this.viewModel.curLoopMode],
          btnSize: CommonConstants.MUSIC_PLAYER_CTRL_BTN_SIZE_COMMON,
          callback: () => {
            this.viewModel.updateLoopMode();
          },
          btnId: 'loopModeBtn'
        });""")
text = text.replace("""        this.ctrlBtnBuilder({
          imgSrc: $r('app.media.foldable_screen_cases_play_last'),
          btnSize: CommonConstants.MUSIC_PLAYER_CTRL_BTN_SIZE_COMMON,
          callback: () => {
            this.viewModel.playPrevious();
          }
        });""", """        this.ctrlBtnBuilder({
          imgSrc: $r('app.media.foldable_screen_cases_play_last'),
          btnSize: CommonConstants.MUSIC_PLAYER_CTRL_BTN_SIZE_COMMON,
          callback: () => {
            this.viewModel.playPrevious();
          },
          btnId: 'prevBtn'
        });""")
open(p, 'w', encoding='utf-8').write(text)
print('loopModeBtn:', text.count("'loopModeBtn'"), 'prevBtn:', text.count("'prevBtn'"))
