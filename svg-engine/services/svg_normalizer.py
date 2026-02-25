from xml.etree import ElementTree as ET


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


class SVGNormalizer:
    @staticmethod
    def normalize(svg: str, fallback_grid: int = 24, strip_transforms: bool = True) -> str:
        root = ET.fromstring(svg)

        if root.tag.endswith("svg"):
            width = root.attrib.get("width")
            height = root.attrib.get("height")
            if "viewBox" not in root.attrib:
                if width and height:
                    root.attrib["viewBox"] = f"0 0 {int(float(width))} {int(float(height))}"
                else:
                    root.attrib["viewBox"] = f"0 0 {fallback_grid} {fallback_grid}"

        for idx, elem in enumerate(root.iter()):
            elem.attrib.pop("style", None)
            if strip_transforms:
                elem.attrib.pop("transform", None)
            if elem is not root and "id" not in elem.attrib:
                elem.attrib["id"] = f"el-{idx}"

        return ET.tostring(root, encoding="unicode")
