from adapters.png_adapter import IImageAdapter
from typing import Tuple, Optional


class SVGAdapter(IImageAdapter):
    def load(self, file_path: str) -> Tuple[Optional[object], bool]:
        try:
            from PyQt6.QtSvg import QSvgRenderer
            from PyQt6.QtGui import QImage, QPainter
            renderer = QSvgRenderer(file_path)
            if not renderer.isValid():
                return None, False
            image = QImage(800, 600, QImage.Format.Format_ARGB32)
            image.fill(0)
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
            return image, True
        except Exception:
            return None, False
    
    def get_format(self) -> str:
        return "SVG"

