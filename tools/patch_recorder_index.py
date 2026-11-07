import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\pages\Index.ets'
t = io.open(p, encoding='utf-8').read()

# 1) 字段：增加首帧标记
t = t.replace(
"  @State renameRecord: Record | undefined = undefined;\n",
"  @State renameRecord: Record | undefined = undefined;\n  private firstPageShow: boolean = true;\n")

# 2) delete 分支：由 deleteDialogShow 统一删除与刷新，避免重复 unlink
t = t.replace(
"""    } else if (operate === 'delete') {
      this.deleteDialogShow(1, [recorder], async () => {
        if (recorder.filePath.length > 0) {
          await this.mediaManager.deleteFile(recorder.filePath);
          let index = this.recordList.indexOf(recorder);
          this.recordList.splice(index, 1);
          this.getAudios();
        }
      })
""",
"""    } else if (operate === 'delete') {
      this.deleteDialogShow(1, [recorder], () => {
      })
""")

# 3) deleteDialogShow：统一删除文件并刷新一次列表
t = t.replace(
"""          action: async () => {
            deleteAction()
            for(let i = 0; i < checkRecords.length; i++) {
              await this.mediaManager.deleteFile(checkRecords[i].filePath);
              if (this.record && this.record.title === checkRecords[i].title) {
                this.audioModel.finish();
                this.record = new Record(getContext(this) as common.UIAbilityContext);
                this.record.init(undefined, false);
              }
            }
          }
""",
"""          action: async () => {
            deleteAction()
            for (let i = 0; i < checkRecords.length; i++) {
              await this.mediaManager.deleteFile(checkRecords[i].filePath);
              if (this.record && this.record.title === checkRecords[i].title) {
                this.audioModel.finish();
                this.record = new Record(getContext(this) as common.UIAbilityContext);
                await this.record.init(undefined, false);
              }
            }
            await this.refreshAudios(true);
          }
""")

# 4) 列表刷新：内容不变时跳过赋值，避免整表重绘
t = t.replace(
"""  async getAudios() {
    this.recordList = await this.mediaManager.queryAllAudios();
  }
""",
"""  private isSameList(list: Array<Record>): boolean {
    if (list.length !== this.recordList.length) {
      return false;
    }
    for (let i = 0; i < list.length; i++) {
      if (list[i].filePath !== this.recordList[i].filePath) {
        return false;
      }
    }
    return true;
  }

  async refreshAudios(force: boolean): Promise<void> {
    let list = await this.mediaManager.queryAllAudios();
    if (!force && this.isSameList(list)) {
      return;
    }
    this.recordList = list;
  }

  async getAudios() {
    await this.refreshAudios(true);
  }
""")

# 5) aboutToAppear / onPageShow
t = t.replace(
"""  async aboutToAppear() {
    this.record.init(undefined, false);
    this.appContext = getContext(this);
    await this.getAudios();
    this.listener.on('change', this.onPortrait);
    this.mediaManager.onAudioChange(this.getAudios);
  }

  async onPageShow() {
    this.recordList = await this.mediaManager.queryAllAudios();
  }
""",
"""  async aboutToAppear() {
    await this.record.init(undefined, false);
    this.appContext = getContext(this);
    await this.refreshAudios(true);
    this.listener.on('change', this.onPortrait);
    this.mediaManager.onAudioChange(this.getAudios);
  }

  async onPageShow() {
    // 首次展示已在 aboutToAppear 中加载，避免重复查询
    if (this.firstPageShow) {
      this.firstPageShow = false;
      return;
    }
    await this.refreshAudios(false);
  }
""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('index patched')
