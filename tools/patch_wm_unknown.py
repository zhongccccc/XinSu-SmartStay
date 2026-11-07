import io
p = r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\WindowComponent\src\main\ets\components\feature\WindowManger.ts'
t = io.open(p, encoding='utf-8').read()
old = """          default:
            message = $r('app.string.unknown');
            break;
        }
        AppStorage.SetOrCreate('focusText', message);"""
new = """          default:
            // 未知事件不覆盖上一次状态，避免页面显示无意义的 Unknown
            message = null;
            break;
        }
        if (message !== null) {
          AppStorage.SetOrCreate('focusText', message);
        }"""
assert old in t
t = t.replace(old, new)
io.open(p, 'w', encoding='utf-8', newline='\n').write(t)

p2 = r'D:\XTS\code\SystemFeature\WindowManagement\WindowManage\WindowComponent\src\main\ets\components\MainPage\MainPage.ets'
t2 = io.open(p2, encoding='utf-8').read()
old2 = """    this.showSubWindow = false;
    WindowManger.destorySubWindowCallback();
    this.videoController.start();"""
new2 = """    this.showSubWindow = false;
    WindowManger.destorySubWindowCallback();
    AppStorage.SetOrCreate('focusText', '');
    this.videoController.start();"""
assert old2 in t2
t2 = t2.replace(old2, new2)
io.open(p2, 'w', encoding='utf-8', newline='\n').write(t2)
print('patched unknown handling')
