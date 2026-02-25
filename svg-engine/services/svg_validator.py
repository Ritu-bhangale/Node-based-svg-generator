from xml.etree import ElementTree as ET


class SVGValidator:
    @staticmethod
    def strip_markdown_fences(raw: str) -> str:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```svg", "").replace("```xml", "").replace("```", "").strip()
        return cleaned

    @staticmethod
    def parse(svg: str) -> ET.Element:
        return ET.fromstring(svg)

    @staticmethod
    def validate_svg(svg: str) -> None:
        root = SVGValidator.parse(svg)
        if not (root.tag == "svg" or root.tag.endswith("}svg")):
            raise ValueError("Invalid SVG: root must be <svg>")
        if "viewBox" not in root.attrib:
            raise ValueError("Invalid SVG: viewBox is required")

        has_xmlns = root.tag.startswith("{http://www.w3.org/2000/svg}") or root.attrib.get("xmlns") == "http://www.w3.org/2000/svg"
        if not has_xmlns:
            raise ValueError("Invalid SVG: xmlns must be http://www.w3.org/2000/svg")

    @staticmethod
    def validate_xml(svg: str) -> None:
        SVGValidator.validate_svg(svg)
