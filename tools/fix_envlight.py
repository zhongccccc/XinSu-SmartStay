# -*- coding: utf-8 -*-
J = r"E:\zhikong\app\web\app.js"
js = open(J, encoding="utf-8").read()

OLD = "    if ($id('envPir')) $id('envPir').style.color = data.pir ? '#ff7a8a' : '#8fa4c8';"
NEW = ("    if ($id('envPir')) $id('envPir').style.color = data.pir ? '#ff7a8a' : '#8fa4c8';\n"
       "    if ($id('envLight')) {\n"
       "      const lit = !!data.light;\n"
       "      $id('envLight').textContent = lit ? '\u5df2\u5f00' : '\u5df2\u5173';\n"
       "      $id('envLight').style.color = lit ? '#ffc46b' : '#8fa4c8';\n"
       "    }\n"
       "    if ($id('envFan')) {\n"
       "      const f = data.fan || 0;\n"
       "      $id('envFan').textContent = f ? ('\u5f00 ' + f) : '\u5f00';\n"
       "    }")
if OLD in js and "envLight" not in js:
    js = js.replace(OLD, NEW, 1)
    open(J, "w", encoding="utf-8").write(js)
    print("已加灯光渲染")
else:
    print("状态:", "已存在" if "envLight" in js else "未匹配")
