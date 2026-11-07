# -*- coding: utf-8 -*-
"""补回被误删的 HTML 结构：语音面板内容、退出遮罩、状态栏、toast。"""
P = r"E:\zhikong\app\web\index.html"
s = open(P, encoding="utf-8").read()

TAIL_OLD = '''      <div class="sheet-head">
        <b>语音服务 · 客房助手</b>
        <button class="close" id="btnCloseService">×</button>
      </div>
<script src="/static/app.js"></script>
</body>
</html>'''

TAIL_NEW = '''      <div class="sheet-head">
        <b>语音服务 · 客房助手</b>
        <button class="close" id="btnCloseService">×</button>
      </div>
      <div class="chat" id="chat"></div>
      <div class="quick" id="quickCmds">
        <button>送一双拖鞋</button><button>开灯</button><button>关窗帘</button>
        <button>空调调至26度</button><button>送两瓶矿泉水</button><button>几点退房</button>
      </div>
      <div class="say-row">
        <button class="mic" id="btnMic">🎙 说话</button>
        <input id="sayInput" placeholder="也可以直接输入，例如：送牙刷">
        <button class="send" id="btnSend">发送</button>
      </div>
    </div>
  </main>

  <!-- 退出遮罩（长按左上角 logo 1.5 秒） -->
  <div class="exitmask" id="exitMask">
    <div class="pinbox">
      <div class="pintitle">退出一体机？</div>
      <div class="pinmsg">退出后将回到桌面，需重新启动应用</div>
      <div class="guide-actions">
        <button class="ghost" id="btnExitCancel">取消</button>
        <button class="cta small" id="btnExitOk">退出</button>
      </div>
    </div>
  </div>

  <!-- 设备状态栏 -->
  <footer class="devbar" id="devbar"></footer>
</div>

<div class="toast" id="toast"></div>
<script src="/static/app.js"></script>
</body>
</html>'''

if "btnExitCancel" in s:
    print("已存在，无需补")
elif TAIL_OLD in s:
    s = s.replace(TAIL_OLD, TAIL_NEW, 1)
    open(P, "w", encoding="utf-8").write(s)
    print("结构已补回")
else:
    print("!! 尾部不匹配，需手工处理")
