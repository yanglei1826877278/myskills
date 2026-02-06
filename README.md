# 我的技能集

个人技能仓库，存放为 Claude Code 编写的自定义技能。

## 技能列表

### Agent Browser
AI 智能体浏览器自动化工具。用于与网站交互，包括导航页面、填写表单、点击按钮、截图、提取数据、测试 Web 应用等。

**主要功能：**
- 浏览器自动化（导航、点击、填充表单）
- 元素快照与交互（使用 @e1、@e2 等引用）
- 状态持久化（保存登录状态）
- 截图和 PDF 导出
- 多会话管理（并行操作多个网站）
- 支持 iOS 模拟器（移动端 Safari）

**使用方法：**
```bash
agent-browser open <url>
agent-browser snapshot -i
agent-browser click @e1
```

详细使用说明请查看 [Agent Browser 文档](skills/agent-browser/SKILL.md)。

### 图片处理器
功能全面的图片处理工具。

**主要功能：**
- 格式转换（支持 JPG/PNG/WebP/ICO/BMP/TIFF 互转）
- 分辨率调整
- 图片压缩

**使用方法：**
```bash
/image-processor <文件路径> [选项]
```

详细使用说明请查看 [图片处理器文档](skills/image-processor/SKILL.md)。

## 在 Claude Code 中使用

如需使用这些技能，请将 `skills/` 目录复制到你的 Claude Code 配置目录中。
