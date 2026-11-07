import re, sys
p = sys.argv[1]
text = open(p, encoding='utf-8').read()
# 1) 去掉外层 it('assertContain') 包裹
text = text.replace("    it('assertContain', 0, () => {", "    beforeAll(async () => {", 1)
# 2) 结尾多出的一个 "})" 需要调整：把最后一个 "    })\n  })\n}" 改成 "    })\n  })\n}"
# 外层 beforeAll 不需要额外闭合，因此把最后的 "    })\n  })\n}" 变为 "  })\n}"
idx = text.rfind("    })\n  })\n}")
if idx != -1:
    text = text[:idx] + "  })\n}"
# 3) 把原来的内层缩进 6 空格降为 4 空格（可选，不影响编译）
open(p, 'w', encoding='utf-8').write(text)
print('flattened')
