"""二代身份证读卡器接入。

只依赖一个约定：reader.read() 返回 IdCardData，其中 photo 是芯片里取出的
BGR 图像（二代证是 358x441 JPEG）。具体厂商 SDK（华视 CVR-100、新中新、
精伦等）各自不同，用子类包一层即可，不要污染主流程。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import numpy as np

from .io_utils import imread_unicode


@dataclass
class IdCardData:
    name: str = ""
    sex: str = ""
    nation: str = ""
    birth: str = ""
    address: str = ""
    id_number: str = ""
    photo: np.ndarray | None = None
    raw: dict = field(default_factory=dict)


class IdCardReader(Protocol):
    def read(self) -> IdCardData: ...


class JsonIdCardReader:
    """开发/联调用：从一个 JSON 里读字段和照片路径，模拟读卡器。"""

    def __init__(self, json_path: str | Path) -> None:
        self.data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    def read(self) -> IdCardData:
        photo = None
        if self.data.get("photo"):
            photo = imread_unicode(self.data["photo"])
        return IdCardData(
            name=self.data.get("name", ""),
            sex=self.data.get("sex", ""),
            nation=self.data.get("nation", ""),
            birth=self.data.get("birth", ""),
            address=self.data.get("address", ""),
            id_number=self.data.get("id_number", ""),
            photo=photo,
            raw=self.data,
        )


class StaticIdCardReader:
    """把一张现成的证件照当作读卡结果，用于跑通链路。"""

    def __init__(self, photo_path: str | Path, id_number: str = "000000000000000000") -> None:
        self.photo_path = photo_path
        self.id_number = id_number

    def read(self) -> IdCardData:
        return IdCardData(id_number=self.id_number, photo=imread_unicode(self.photo_path))


# 厂商 SDK 接入示例（伪代码，按实际 SDK 补全）：
#
# class HuaShiReader:
#     def __init__(self):
#         self.sdk = load_vendor_sdk()          # .so / .dll
#         self.sdk.Init()
#     def read(self) -> IdCardData:
#         res = self.sdk.ReadCard()
#         photo = cv2.imdecode(np.frombuffer(res.wlt, np.uint8), cv2.IMREAD_COLOR)
#         return IdCardData(name=res.name, id_number=res.idno, photo=photo)
