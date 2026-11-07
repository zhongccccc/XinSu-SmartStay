import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\pages\Index.ets'
t = io.open(p, encoding='utf-8').read()
t = t.replace("""  async refreshAudios(force: boolean): Promise<void> {
    let list = await this.mediaManager.queryAllAudios();
    if (!force && this.isSameList(list)) {
      return;
    }
    this.recordList = list;
  }""","""  async refreshAudios(force: boolean): Promise<void> {
    let start = Date.now();
    let list = await this.mediaManager.queryAllAudios();
    let same = this.isSameList(list);
    if (force || !same) {
      this.recordList = list;
    }
    Logger.info(TAG, `refreshAudios cost=${Date.now() - start}ms count=${list.length} same=${same} force=${force}`);
  }""")
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)

p2 = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\pages\RecordPage.ets'
t2 = io.open(p2, encoding='utf-8').read()
t2 = t2.replace("""  async aboutToAppear() {
    await this.recordModel.initAudioRecorder();
    this.filePath = await this.mediaManager.createAudioFile();""","""  async aboutToAppear() {
    let start = Date.now();
    await this.recordModel.initAudioRecorder();
    this.filePath = await this.mediaManager.createAudioFile();
    Logger.info(TAG, `recordPage ready cost=${Date.now() - start}ms`);""")
io.open(p2, 'w', encoding='utf-8', newline='\n').write(t2)

p3 = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\pages\Play.ets'
t3 = io.open(p3, encoding='utf-8').read()
t3 = t3.replace("""  aboutToAppear() {
    // 先用路由参数同步填充标题，保证首帧即有内容，避免页面先空白再跳变
    let name = this.filePath.substring(this.filePath.lastIndexOf('/') + 1);
    this.title = name;
    Logger.info(TAG, `PlayPage ready, title=${name}`);""","""  aboutToAppear() {
    // 先用路由参数同步填充标题，保证首帧即有内容，避免页面先空白再跳变
    let start = Date.now();
    let name = this.filePath.substring(this.filePath.lastIndexOf('/') + 1);
    this.title = name;
    Logger.info(TAG, `PlayPage ready cost=${Date.now() - start}ms, title=${name}`);""")
io.open(p3, 'w', encoding='utf-8', newline='\n').write(t3)
print('instrumented')
