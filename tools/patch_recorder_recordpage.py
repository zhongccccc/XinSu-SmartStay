import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\pages\RecordPage.ets'
t = io.open(p, encoding='utf-8').read()

t = t.replace(
"""  @State duration: string = '00:00';
  @State resetAnimation: boolean = false;
""",
"""  @State duration: string = '00:00';
  @State resetAnimation: boolean = false;
  @State title: string = '录音';
  private finished: boolean = false;
""")

t = t.replace(
"""  async finish() {
    Logger.info(TAG, `avRecordder finished. ${this.filePath}`);
    if (this.filePath.length > 0) {
""",
"""  async finish() {
    Logger.info(TAG, `avRecordder finished. ${this.filePath}`);
    if (this.finished) {
      return;
    }
    this.finished = true;
    if (this.filePath.length > 0) {
""")

t = t.replace(
"""    this.filePath = await this.mediaManager.createAudioFile();
""",
"""    this.filePath = await this.mediaManager.createAudioFile();
    this.title = this.filePath.substring(this.filePath.lastIndexOf('/') + 1);
""")

t = t.replace(
"""      if (this.filePath.length > 0) {
        TitleBar({ title: this.filePath.substring(this.filePath.lastIndexOf('/') + 1) })
      }
""",
"""      // 标题栏始终渲染，避免异步创建文件后插入导致页面内容下移（视觉抖动）
      TitleBar({ title: this.title })
""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('recordpage patched')
