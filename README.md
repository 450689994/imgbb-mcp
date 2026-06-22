# ImgBB MCP Server 🖼️

> 免费图床 MCP 服务 - 将图片上传到 ImgBB 并获取公网链接

## 📋 简介

这是一个基于 **MCP (Model Context Protocol)** 的免费图床服务，将 ImgBB 匿名上传功能封装为 MCP 工具，供 AI 客户端（如 Claude Desktop、Cursor 等）直接调用。

**核心特性：**
- ✅ **完全免费** - 无需注册、无需 API Key
- ✅ **匿名上传** - 保护隐私，无需登录
- ✅ **支持本地文件** - 直接上传本地图片
- ✅ **支持网络图片** - 传入 URL 即可转存
- ✅ **返回丰富信息** - 图片链接、缩略图、删除链接等
- ✅ **MCP 标准协议** - 兼容所有 MCP 客户端

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install mcp
```

### 2. 运行 MCP Server

```bash
python3 mcp_server.py
```

### 3. 配置 MCP 客户端

#### Claude Desktop

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "imgbb": {
      "command": "python3",
      "args": ["/path/to/imgbb-mcp/mcp_server.py"]
    }
  }
}
```

#### Cursor

在 Cursor 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "imgbb": {
      "command": "python3",
      "args": ["/path/to/imgbb-mcp/mcp_server.py"]
    }
  }
}
```

## 🛠️ 可用工具

### 1. `upload_image`

上传图片到 ImgBB 图床（支持本地文件和网络 URL）

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `source` | string | ✅ | 本地文件路径 或 网络图片 URL |

**返回示例：**

```json
{
  "success": true,
  "url": "https://i.ibb.co/xxxxx/image.png",
  "url_viewer": "https://ibb.co/xxxxx",
  "delete_url": "https://ibb.co/delete/xxxxx",
  "display_url": "https://i.ibb.co/xxxxx/image.png",
  "filename": "image.png",
  "width": 1920,
  "height": 1080,
  "size": 123456,
  "size_formatted": "120 KB",
  "thumb_url": "https://i.ibb.co/xxxxx/thumb-image.png"
}
```

### 2. `upload_image_from_url`

专门从网络 URL 上传图片

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | string | ✅ | 网络图片的完整 URL 地址 |

## 📦 项目结构

```
imgbb-mcp/
├── mcp_server.py       # MCP Server 主程序
├── imgbb_upload.py     # 独立上传脚本（可直接命令行使用）
├── requirements.txt    # Python 依赖
├── pyproject.toml      # 项目配置
├── package.json        # MCP 配置（兼容格式）
└── README.md           # 本文件
```

## 🔧 独立使用（无需 MCP）

也可以直接使用上传脚本：

```bash
# 上传本地图片
python3 imgbb_upload.py /path/to/image.png

# 上传网络图片
python3 imgbb_upload.py https://example.com/photo.jpg
```

## ⚠️ 注意事项

- ImgBB 是免费图床，请勿上传违规内容
- 单张图片最大支持 **32MB**
- 上传的图片默认 **永久保存**，除非手动删除
- 删除链接请妥善保存，删除后不可恢复

## 📄 许可证

MIT
