---
name: image-processor
description: 综合图片处理工具。支持格式转换（JPG/PNG/WebP/ICO/BMP/TIFF互转）、分辨率调整（保持比例或精确尺寸）、图片压缩。如需链式操作，请分多次调用
argument-hint: "文件路径或目录 [操作选项]"
---

## 图片处理综合工具

功能：格式转换 + 分辨率调整 + 图片压缩

### 环境要求

请确保已安装 Python 3 和 Pillow 库：
```bash
# 检查 Python
python3 --version

# 安装 Pillow
pip3 install Pillow
```

---

### 一、格式转换

支持以下格式互转：
- **JPG/JPEG ↔ PNG**：相互转换
- **PNG → ICO**：生成图标（默认 128x128，可指定尺寸）
- **JPG/PNG/BMP/TIFF → WebP**：转为 WebP 格式
- **WebP → JPG/PNG**：转为 JPG 或 PNG
- **BMP/TIFF/GIF → JPG/PNG**：转为 JPG 或 PNG

**PNG 转 JPG 特殊处理**：
- 透明背景自动填充为白色（或自定义颜色）

**示例**：
```bash
# PNG 转 JPG
/image-processor photo.png --convert jpg

# 指定背景色（PNG 转 JPG）
/image-processor transparent.png --convert jpg --bg-color white

# 转为 WebP
/image-processor photo.jpg --convert webp

# 制作图标（默认 128x128）
/image-processor logo.png --convert ico

# 制作指定尺寸图标
/image-processor logo.png --convert ico --ico-size 256
```

---

### 二、分辨率调整

**调整方式**：
- 指定宽度（自动计算高度）
- 指定高度（自动计算宽度）
- 同时指定宽度和高度
- 百分比缩放
- 预设尺寸

**预设尺寸**：
| 预设名称 | 尺寸 |
|---------|------|
| instagram-square | 1080x1080 |
| youtube-thumb | 1280x720 |
| twitter-banner | 1500x500 |
| hd | 1920x1080 |
| 4k | 3840x2160 |

**使用 LANCZOS 重采样算法，保证高质量缩放**

**示例**：
```bash
# 指定宽度（自动保持比例）
/image-processor photo.jpg -w 1920

# 指定高度
/image-processor photo.jpg -h 1080

# 指定精确尺寸（可能变形）
/image-processor banner.jpg -w 1500 -h 500 --no-aspect

# 百分比缩放（50%）
/image-processor large.jpg -s 0.5

# 使用预设尺寸
/image-processor photo.jpg --preset hd
```

---

### 三、图片压缩

**压缩方式**：

1. **智能压缩（默认）**
   - 未指定 -q 参数时自动使用
   - 自动调整质量参数，在文件大小和质量间取得平衡
   - 适合不确定最佳压缩比的情况

2. **固定质量压缩**
   - 使用 -q 参数指定质量（1-100）
   - 质量越高文件越大
   - 推荐值：网页 85，高质量 95，大幅压缩 70

3. **PNG 无损优化**
   - 使用 --optimize 参数
   - 减小文件大小而不损失质量

**示例**：
```bash
# 智能压缩（默认）
/image-processor photo.jpg

# 固定质量压缩
/image-processor photo.jpg -q 85

# PNG 无损优化
/image-processor image.png --optimize

# 压缩到指定大小
/image-processor photo.jpg --target-size 500KB
```

---

### 四、链式操作

如果用户要求进行多个操作（如"减少50%分辨率并转换成WebP"），请分多次调用本工具，每次只执行一个操作。

**操作顺序建议**：格式转换 → 分辨率调整 → 图片压缩

**示例**：
用户要求："把这张图片减少50%的分辨率并且转换成webp格式"

处理步骤：
```bash
# 第一步：减少50%分辨率
/image-processor photo.jpg -s 0.5

# 第二步：转换为WebP格式
/image-processor photo_scaled.jpg --convert webp
```

---

### 五、批量处理

处理目录中的所有图片文件。

**支持的格式**：`.jpg, .jpeg, .png, .gif, .bmp, .tiff, .webp`

**输出**：
- 默认创建 `processed/` 子目录
- 可用 `-o` 指定输出目录

**示例**：
```bash
# 批量转换目录下所有图片
/image-processor ./photos/ --convert jpg

# 批量调整尺寸
/image-processor ./images/ -w 1920 -o ./resized/

# 批量优化网页图片
/image-processor ./web-images/ --convert webp -w 1200
```

---

### 六、参数速查

| 参数 | 说明 | 示例 |
|------|------|------|
| `input` | 输入文件或目录 | `./photo.jpg` 或 `./images/` |
| `-o, --output` | 输出文件或目录 | `./output/` |
| `--convert` | 目标格式 | `--convert jpg` |
| `--bg-color` | 背景色（PNG转JPG） | `--bg-color white` |
| `-w, --width` | 目标宽度（像素） | `-w 1920` |
| `--height` | 目标高度（像素） | `--height 1080` |
| `-s, --scale` | 缩放比例（0-1） | `-s 0.5` |
| `--no-aspect` | 不保持宽高比 | `--no-aspect` |
| `--preset` | 使用预设尺寸 | `--preset hd` |
| `-q, --quality` | 质量（1-100） | `-q 85` |
| `--optimize` | PNG 无损优化 | `--optimize` |
| `--target-size` | 目标文件大小 | `--target-size 500KB` |
| `--ico-size` | ICO 尺寸 | `--ico-size 256` |
| `--overwrite` | 覆盖原文件 | `--overwrite` |
| `-v, --verbose` | 详细输出 | `-v` |

---

### 七、常见问题

**Q: PNG 转 JPG 后背景变黑？**
A: 使用 `--bg-color white` 指定白色背景。

**Q: ICO 图标太大或太小？**
A: 使用 `--ico-size` 指定尺寸（如 64, 128, 256）。

**Q: 压缩后文件反而变大？**
A: 某些图片（如截图）本身已高度优化。尝试降低质量或使用 `--target-size`。

**Q: 批量处理支持子目录吗？**
A: 当前版本仅处理指定目录下的文件，不递归子目录。
