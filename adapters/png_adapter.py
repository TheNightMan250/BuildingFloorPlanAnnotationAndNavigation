from abc import ABC, abstractmethod
from typing import Tuple, Optional


class IImageAdapter(ABC):
    @abstractmethod
    def load(self, file_path: str) -> Tuple[Optional[object], bool]:
        pass
    
    @abstractmethod
    def get_format(self) -> str:
        pass


class PNGAdapter(IImageAdapter):
    def load(self, file_path: str) -> Tuple[Optional[object], bool]:
        try:
            from PyQt6.QtGui import QImage
            image = QImage(file_path)
            if image.isNull():
                return None, False
            return image, True
        except Exception:
            return None, False
    
    def get_format(self) -> str:
        return "PNG"

