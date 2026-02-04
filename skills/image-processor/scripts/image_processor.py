#!/usr/bin/env python3
"""
图片处理工具
支持格式转换、分辨率调整、图片压缩
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image, ImageOps


# ============================================================
# 预设尺寸定义
# ============================================================
PRESETS = {
    "instagram-square": (1080, 1080),
    "youtube-thumb": (1280, 720),
    "twitter-banner": (1500, 500),
    "hd": (1920, 1080),
    "4k": (3840, 2160),
}

# 支持的图片格式
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"}


# ============================================================
# 工具函数
# ============================================================
def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def parse_size(size_str: str) -> int:
    """解析文件大小字符串（如 500KB, 2MB）"""
    size_str = size_str.strip().upper()
    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}

    for unit, mult in multipliers.items():
        if size_str.endswith(unit):
            return int(float(size_str[:-2]) * mult)
    # 默认为字节
    return int(size_str)


def get_output_path(input_path: Path, output_dir: Optional[Path] = None, new_ext: str = None) -> Path:
    """生成输出文件路径"""
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        if input_path.is_dir():
            return output_dir
        return output_dir / input_path.name

    # 默认创建 processed 子目录
    processed_dir = input_path.parent / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    if input_path.is_dir():
        return processed_dir

    if new_ext:
        return processed_dir / (input_path.stem + new_ext)
    return processed_dir / input_path.name


# ============================================================
# 图片加载与验证
# ============================================================
def load_image(image_path: Path) -> Image.Image:
    """加载图片"""
    img = Image.open(image_path)
    # 转换为 RGB（处理 PNG 等带透明通道的图片）
    if img.mode in ("RGBA", "LA", "P"):
        # 保持为 P 模式（调色板）以便后续处理
        pass
    return img


# ============================================================
# 格式转换模块
# ============================================================
def convert_format(
    img: Image.Image,
    target_format: str,
    bg_color: str = "white"
) -> Image.Image:
    """转换图片格式"""
    target_format = target_format.lower()

    # PNG 转 JPG 处理透明背景
    if target_format in ("jpg", "jpeg") and img.mode in ("RGBA", "LA", "P"):
        if bg_color == "white":
            background = Image.new("RGB", img.size, (255, 255, 255))
        elif bg_color == "black":
            background = Image.new("RGB", img.size, (0, 0, 0))
        elif bg_color.startswith("#"):
            bg_color = bg_color.lstrip("#")
            r = int(bg_color[0:2], 16)
            g = int(bg_color[2:4], 16)
            b = int(bg_color[4:6], 16)
            background = Image.new("RGB", img.size, (r, g, b))
        else:
            background = Image.new("RGB", img.size, (255, 255, 255))

        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background

    return img


def save_image(
    img: Image.Image,
    output_path: Path,
    format_name: str = None,
    quality: int = 95,
    optimize: bool = False
) -> None:
    """保存图片"""
    format_map = {
        "jpg": "JPEG",
        "jpeg": "JPEG",
        "png": "PNG",
        "webp": "WEBP",
        "ico": "ICO",
        "bmp": "BMP",
    }

    save_format = format_map.get(format_name.lower(), format_name.upper()) if format_name else None

    if save_format == "JPEG":
        img = img.convert("RGB")

    save_kwargs = {"format": save_format}
    if save_format in ("JPEG", "WEBP"):
        save_kwargs["quality"] = quality
    if save_format == "PNG" and optimize:
        save_kwargs["optimize"] = True

    img.save(output_path, **save_kwargs)


# ============================================================
# 分辨率调整模块
# ============================================================
def calculate_new_size(
    img: Image.Image,
    target_width: Optional[int] = None,
    target_height: Optional[int] = None,
    scale: Optional[float] = None,
    preset: Optional[str] = None,
    maintain_aspect: bool = True
) -> Tuple[int, int]:
    """计算目标尺寸"""
    original_width, original_height = img.size

    # 使用预设
    if preset:
        if preset not in PRESETS:
            raise ValueError(f"未知预设: {preset}，可选: {', '.join(PRESETS.keys())}")
        return PRESETS[preset]

    # 缩放比例
    if scale is not None:
        return int(original_width * scale), int(original_height * scale)

    # 指定宽度
    if target_width is not None and target_height is None:
        if maintain_aspect:
            ratio = target_width / original_width
            return target_width, int(original_height * ratio)
        return target_width, original_height

    # 指定高度
    if target_height is not None and target_width is None:
        if maintain_aspect:
            ratio = target_height / original_height
            return int(original_width * ratio), target_height
        return original_width, target_height

    # 同时指定宽度和高度
    if target_width is not None and target_height is not None:
        return target_width, target_height

    return original_width, original_height


def resize_image(
    img: Image.Image,
    new_size: Tuple[int, int],
    maintain_aspect: bool = True
) -> Image.Image:
    """调整图片尺寸"""
    target_width, target_height = new_size

    if maintain_aspect:
        # 保持比例，可能需要填充或适应
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    else:
        # 精确尺寸（可能变形）
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    return img


# ============================================================
# 压缩模块
# ============================================================
def get_image_size(image_path: Path) -> int:
    """获取图片文件大小"""
    return image_path.stat().st_size


def smart_compress(
    img: Image.Image,
    output_path: Path,
    format_name: str = "jpeg",
    target_size: Optional[int] = None,
    min_quality: int = 10,
    max_quality: int = 100
) -> Tuple[int, int]:
    """智能压缩，自动调整质量参数"""
    if format_name.lower() in ("png"):
        # PNG 使用无损优化
        save_image(img, output_path, format_name, optimize=True)
        return get_image_size(output_path)

    # JPEG/WebP 使用有损压缩
    original_size = get_image_size(output_path) if output_path.exists() else 0

    if target_size is None:
        # 默认使用质量 85
        save_image(img, output_path, format_name, quality=85)
        return get_image_size(output_path)

    # 二分查找最佳质量
    low, high = min_quality, max_quality
    best_quality = 85
    best_size = 0

    while low <= high:
        mid_quality = (low + high) // 2
        save_image(img, output_path, format_name, quality=mid_quality)
        current_size = get_image_size(output_path)

        if current_size <= target_size:
            best_quality = mid_quality
            best_size = current_size
            high = mid_quality - 1
        else:
            low = mid_quality + 1

    return best_size


def compress_image(
    img: Image.Image,
    output_path: Path,
    format_name: str = "jpeg",
    quality: Optional[int] = None,
    optimize: bool = False,
    target_size: Optional[int] = None
) -> Tuple[int, int]:
    """压缩图片"""
    if target_size is not None:
        # 智能压缩
        original_size = 0  # 尚未保存，无法获取原始大小
        compressed_size = smart_compress(img, output_path, format_name, target_size)
    elif quality is not None:
        # 固定质量压缩
        save_image(img, output_path, format_name, quality=quality, optimize=optimize)
        compressed_size = get_image_size(output_path)
    else:
        # 默认智能压缩
        compressed_size = smart_compress(img, output_path, format_name)

    return compressed_size


# ============================================================
# ICO 特殊处理
# ============================================================
def save_ico(img: Image.Image, output_path: Path, size: int = 128) -> None:
    """保存 ICO 图标（指定尺寸）"""
    # 转换为 RGBA
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # 缩放到目标尺寸
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    img.save(output_path, format="ICO", sizes=[(size, size)])


# ============================================================
# 单文件处理
# ============================================================
def process_single_image(
    input_path: Path,
    output_path: Optional[Path] = None,
    convert: Optional[str] = None,
    bg_color: str = "white",
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: Optional[float] = None,
    preset: Optional[str] = None,
    no_aspect: bool = False,
    quality: Optional[int] = None,
    optimize: bool = False,
    target_size: Optional[str] = None,
    ico_size: Optional[int] = 128,
    overwrite: bool = False,
    verbose: bool = False
) -> dict:
    """处理单张图片"""
    result = {
        "input": str(input_path),
        "output": None,
        "original_size": 0,
        "compressed_size": 0,
        "success": False,
        "error": None
    }

    try:
        # 加载图片
        img = load_image(input_path)
        result["original_size"] = get_image_size(input_path)

        # 确定输出路径
        new_ext = None
        if convert:
            ext_map = {
                "jpg": ".jpg", "jpeg": ".jpg",
                "png": ".png", "webp": ".webp",
                "ico": ".ico", "bmp": ".bmp"
            }
            new_ext = ext_map.get(convert.lower(), f".{convert}")

        if output_path is None:
            output_path = get_output_path(input_path, None, new_ext)
        elif convert and new_ext:
            # 如果指定了格式转换，使用正确的扩展名替换用户指定的扩展名
            output_path = Path(str(output_path).rsplit('.', 1)[0] + new_ext)

        if input_path.is_file() and not output_path.is_dir():
            result["output"] = str(output_path)
        else:
            result["output"] = str(output_path / input_path.name)

        # 格式转换
        if convert:
            if convert.lower() == "ico":
                save_ico(img, output_path, ico_size)
                result["compressed_size"] = get_image_size(output_path)
            else:
                img = convert_format(img, convert, bg_color)
                # 压缩
                ts = parse_size(target_size) if target_size else None
                compress_image(
                    img, output_path,
                    format_name=convert,
                    quality=quality,
                    optimize=optimize,
                    target_size=ts
                )
                result["compressed_size"] = get_image_size(output_path)

        # 分辨率调整
        if width is not None or height is not None or scale is not None or preset:
            new_size = calculate_new_size(
                img, width, height, scale, preset, not no_aspect
            )
            img = resize_image(img, new_size, not no_aspect)

        # 如果只有分辨率调整而没有格式转换，需要保存
        if convert is None and (width is not None or height is not None or scale is not None or preset):
            # 确定输出格式
            format_name = input_path.suffix[1:].lower() if input_path.suffix else "png"
            ts = parse_size(target_size) if target_size else None
            compress_image(
                img, output_path,
                format_name=format_name,
                quality=quality,
                optimize=optimize,
                target_size=ts
            )
            result["compressed_size"] = get_image_size(output_path)
        # 如果没有格式转换也没有分辨率调整，但需要压缩（智能压缩）
        elif convert is None:
            format_name = input_path.suffix[1:].lower() if input_path.suffix else "png"
            ts = parse_size(target_size) if target_size else None
            compress_image(
                img, output_path,
                format_name=format_name,
                quality=quality,
                optimize=optimize,
                target_size=ts
            )
            result["compressed_size"] = get_image_size(output_path)

        result["success"] = True

        if verbose:
            reduction = (1 - result["compressed_size"] / result["original_size"]) * 100
            print(f"处理完成: {input_path.name}")
            print(f"  原始大小: {format_size(result['original_size'])}")
            print(f"  处理后大小: {format_size(result['compressed_size'])}")
            print(f"  减少: {reduction:.1f}%")

    except Exception as e:
        result["error"] = str(e)
        print(f"错误: {input_path.name} - {e}")

    return result


# ============================================================
# 批量处理
# ============================================================
def process_directory(
    input_dir: Path,
    output_dir: Optional[Path] = None,
    convert: Optional[str] = None,
    bg_color: str = "white",
    width: Optional[int] = None,
    height: Optional[int] = None,
    scale: Optional[float] = None,
    preset: Optional[str] = None,
    no_aspect: bool = False,
    quality: Optional[int] = None,
    optimize: bool = False,
    target_size: Optional[str] = None,
    ico_size: int = 128,
    overwrite: bool = False,
    verbose: bool = False
) -> List[dict]:
    """批量处理目录中的图片"""
    results = []

    # 获取所有图片文件
    image_files = []
    for ext in IMAGE_EXTENSIONS:
        image_files.extend(input_dir.glob(f"*{ext}"))
        image_files.extend(input_dir.glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"未在 {input_dir} 中找到图片文件")
        return results

    print(f"找到 {len(image_files)} 张图片")

    # 创建输出目录
    if output_dir is None:
        output_dir = input_dir / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    for image_file in sorted(image_files):
        result = process_single_image(
            image_file,
            output_dir,
            convert,
            bg_color,
            width,
            height,
            scale,
            preset,
            no_aspect,
            quality,
            optimize,
            target_size,
            ico_size,
            overwrite,
            verbose
        )
        results.append(result)

    # 统计
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    print(f"\n处理完成: {success_count} 成功, {fail_count} 失败")

    # 显示总压缩效果
    if success_count > 0:
        total_original = sum(r["original_size"] for r in results if r["success"])
        total_compressed = sum(r["compressed_size"] for r in results if r["success"])
        if total_original > 0:
            reduction = (1 - total_compressed / total_original) * 100
            print(f"总大小: {format_size(total_original)} -> {format_size(total_compressed)}")
            print(f"总减少: {reduction:.1f}%")

    return results


# ============================================================
# 环境检查
# ============================================================
def check_environment():
    """检查运行环境"""
    print("检查环境...")

    # 检查 Python
    try:
        import PIL
        print(f"✓ Pillow 已安装 (版本 {PIL.__version__})")
    except ImportError:
        print("✗ Pillow 未安装")
        print("  请运行: pip3 install Pillow")
        return False

    return True


# ============================================================
# 主函数
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="图片处理工具 - 支持格式转换、分辨率调整、图片压缩",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s photo.png --convert jpg
  %(prog)s photo.jpg -w 1920
  %(prog)s photo.jpg -q 85
  %(prog)s logo.png --convert ico --ico-size 256
  %(prog)s ./images/ --convert webp -w 1200 -q 85
  %(prog)s ./photos/ -o ./output/
        """
    )

    # 输入输出
    parser.add_argument("input", help="输入文件或目录")
    parser.add_argument("-o", "--output", help="输出文件或目录")

    # 格式转换
    parser.add_argument("--convert", choices=["jpg", "jpeg", "png", "webp", "ico", "bmp"],
                        help="目标格式")
    parser.add_argument("--bg-color", default="white",
                        help="PNG转JPG的背景色（默认: white）")

    # 分辨率调整
    parser.add_argument("-w", "--width", type=int, help="目标宽度（像素）")
    parser.add_argument("--height", type=int, help="目标高度（像素）")
    parser.add_argument("-s", "--scale", type=float, help="缩放比例（0-1）")
    parser.add_argument("--no-aspect", action="store_true",
                        help="不保持宽高比")
    parser.add_argument("--preset", choices=list(PRESETS.keys()),
                        help="使用预设尺寸")

    # 压缩
    parser.add_argument("-q", "--quality", type=int, choices=range(1, 101),
                        help="JPG/WebP质量（1-100）")
    parser.add_argument("--optimize", action="store_true",
                        help="启用PNG无损优化")
    parser.add_argument("--target-size",
                        help="目标文件大小（如: 500KB, 2MB）")

    # ICO 专用
    parser.add_argument("--ico-size", type=int, default=128,
                        help="ICO图标尺寸（默认: 128）")

    # 其他
    parser.add_argument("--check", action="store_true",
                        help="检查运行环境")
    parser.add_argument("--overwrite", action="store_true",
                        help="覆盖原文件")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="详细输出")

    args = parser.parse_args()

    # 环境检查
    if args.check:
        check_environment()
        return

    # 验证输入
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入路径不存在: {args.input}")
        sys.exit(1)

    # 处理
    if input_path.is_file():
        process_single_image(
            input_path,
            Path(args.output) if args.output else None,
            args.convert,
            args.bg_color,
            args.width,
            args.height,
            args.scale,
            args.preset,
            args.no_aspect,
            args.quality,
            args.optimize,
            args.target_size,
            args.ico_size,
            args.overwrite,
            args.verbose
        )
    elif input_path.is_dir():
        process_directory(
            input_path,
            Path(args.output) if args.output else None,
            args.convert,
            args.bg_color,
            args.width,
            args.height,
            args.scale,
            args.preset,
            args.no_aspect,
            args.quality,
            args.optimize,
            args.target_size,
            args.ico_size,
            args.overwrite,
            args.verbose
        )


if __name__ == "__main__":
    main()
