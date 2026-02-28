"""
Convert raster images (PNG) to SVG using image tracing.
Practical fallback for cases where direct SVG generation is difficult.
"""

import logging
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
    import potrace
    HAS_POTRACE = True
except ImportError:
    HAS_POTRACE = False

logger = logging.getLogger(__name__)


class SVGConverterService:
    """Convert PNG/raster images to SVG using potrace."""

    @staticmethod
    def png_to_svg(
        png_path: str,
        output_svg_path: Optional[str] = None,
        threshold: int = 128,
    ) -> str:
        """
        Convert PNG image to SVG using potrace.
        
        Args:
            png_path: Path to input PNG file
            output_svg_path: Path for output SVG (optional)
            threshold: Threshold for black/white conversion (0-255)
            
        Returns:
            SVG content as string
            
        Raises:
            ImportError: If potrace is not installed
            FileNotFoundError: If PNG file doesn't exist
        """
        if not HAS_POTRACE:
            raise ImportError(
                "potrace not installed. Install with: pip install pypotrace pillow"
            )

        png_file = Path(png_path)
        if not png_file.exists():
            raise FileNotFoundError(f"PNG file not found: {png_path}")

        # Load and convert image
        logger.info(f"Converting {png_path} to SVG...")
        
        img = Image.open(png_file)
        
        # Convert to grayscale if needed
        if img.mode != "L":
            img = img.convert("L")
        
        # Convert to bitmap (black and white)
        img_bw = img.point(lambda x: 0 if x < threshold else 255, "1")

        # Trace with potrace
        bitmap = potrace.Bitmap(img_bw)
        path = bitmap.trace()

        # Generate SVG
        svg = _generate_svg_from_path(path, img_bw.size)

        # Save if output path provided
        if output_svg_path:
            Path(output_svg_path).write_text(svg)
            logger.info(f"Saved SVG to {output_svg_path}")

        return svg

    @staticmethod
    def batch_convert_pngs_to_svgs(
        input_dir: str,
        output_dir: Optional[str] = None,
    ) -> dict:
        """
        Convert all PNG files in a directory to SVG.
        
        Args:
            input_dir: Directory containing PNG files
            output_dir: Directory for output SVGs (defaults to input_dir)
            
        Returns:
            Dictionary mapping PNG filenames to SVG paths
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir or input_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}
        for png_file in input_path.glob("*.png"):
            try:
                svg_path = output_path / f"{png_file.stem}.svg"
                SVGConverterService.png_to_svg(str(png_file), str(svg_path))
                results[png_file.name] = str(svg_path)
                logger.info(f"✓ Converted {png_file.name}")
            except Exception as e:
                logger.error(f"✗ Failed to convert {png_file.name}: {e}")
                results[png_file.name] = None

        return results


def _generate_svg_from_path(path, img_size: tuple) -> str:
    """Generate SVG from potrace path."""
    width, height = img_size
    
    svg_parts = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg">',
        '<style>path{fill:black;}</style>',
    ]

    # Add paths from traced bitmap
    for curve in path:
        svg_path = _curve_to_svg_path(curve)
        if svg_path:
            svg_parts.append(f'<path d="{svg_path}"/>')

    svg_parts.append("</svg>")

    return "\n".join(svg_parts)


def _curve_to_svg_path(curve) -> str:
    """Convert potrace curve to SVG path data."""
    if not hasattr(curve, "segments"):
        return ""

    parts = ["M"]
    for segment in curve.segments:
        # Start point
        if not parts[0].startswith("M"):
            parts.append("M")
        parts.append(f"{segment.start_point[0]},{segment.start_point[1]}")

        # Bezier curve
        if hasattr(segment, "control_points"):
            ctrl = segment.control_points
            end = segment.end_point
            parts.append(f"C{ctrl[0][0]},{ctrl[0][1]} {ctrl[1][0]},{ctrl[1][1]} {end[0]},{end[1]}")
        else:
            parts.append(f"L{segment.end_point[0]},{segment.end_point[1]}")

    parts.append("Z")
    return " ".join(parts)
