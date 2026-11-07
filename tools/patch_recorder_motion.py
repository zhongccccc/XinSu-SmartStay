import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\common\AudioItem.ets'
t = io.open(p, encoding='utf-8').read()
old = """  leftSliderChange() {
    animateTo({ duration: 500, curve: Curve.Linear }, () => {
      if (this.index !== this.leftSliderIndex) {
        this.translateLeft = 0;
        this.translateRight = TRANSLATE;
      } else {
        if (this.translateLeft < 0) {
          this.translateLeft = 0;
          this.translateRight = TRANSLATE;
        } else {
          this.translateLeft = TRANSLATE;
          this.translateRight = 0;
        }
      }
    })
  }"""
new = """  leftSliderChange() {
    let open = this.index === this.leftSliderIndex;
    let targetLeft = open ? TRANSLATE : 0;
    let targetRight = open ? 0 : TRANSLATE;
    // 状态未变化的条目直接跳过，避免一次左滑让列表中所有条目同时播放动画
    if (this.translateLeft === targetLeft && this.translateRight === targetRight) {
      return;
    }
    animateTo({ duration: 300, curve: Curve.EaseOut }, () => {
      this.translateLeft = targetLeft;
      this.translateRight = targetRight;
    })
  }"""
assert old in t
t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)

p2 = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\common\AnimateView.ets'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace("""  aboutToAppear() {
    this.animator()
  }""","""  aboutToAppear() {
    this.animator()
  }

  aboutToDisappear() {
    clearInterval(this.intervalId)
  }""")
io.open(p2, 'w', encoding='utf-8', newline='\n').write(t2)
print('patched audioitem + animateview')
