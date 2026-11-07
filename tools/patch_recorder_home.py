import io
p = r'D:\XTS\code\SystemFeature\Media\Recorder\entry\src\main\ets\common\HomeView.ets'
t = io.open(p, encoding='utf-8').read()

# 1) 稳定 key：使用文件路径，避免 duration/title 变化导致条目重建闪烁
t = t.replace(
"""        }, (item: Record, index) => {
          return JSON.stringify(item) + index;
        })""",
"""        }, (item: Record) => {
          return item.filePath;
        })""")

# 2) 勾选时只刷新单条，避免整表 reload
t = t.replace(
"""  checkItem = (index: number) => {
    this.recordList[index].isCheck = !this.recordList[index].isCheck;
    this.checkNum = this.checkNum + (this.recordList[index].isCheck ? 1 : -1);
    this.recordDataSource.setData(this.recordList);
    this.recordDataSource.notifyDataReload();
  }""",
"""  checkItem = (index: number) => {
    this.recordList[index].isCheck = !this.recordList[index].isCheck;
    this.checkNum = this.checkNum + (this.recordList[index].isCheck ? 1 : -1);
    this.recordDataSource.notifyDataChange(index);
  }""")

io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('homeview patched')
