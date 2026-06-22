#!/usr/bin/env python3
"""
ImgBB MCP Server - 将 ImgBB 图床上传功能封装为 MCP 工具

MCP (Model Context Protocol) 服务器，提供免费的图片上传工具。
支持上传本地图片或网络图片到 ImgBB 图床，返回公网可访问的图片链接。

安装依赖:
    pip install mcp

运行方式:
    python3 mcp_server.py
    
    或通过 MCP Client 连接:
    mcp run mcp_server.py
"""

import json
import os
import sys
import base64
import urllib.request
import urllib.parse
from typing import Optional

# 尝试导入 mcp 库，如果失败则给出友好提示
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent
    from pydantic import BaseModel, Field
except ImportError:
    print("❌ 缺少依赖，请安装: pip install mcp", file=sys.stderr)
    sys.exit(1)


# ============================================================
# 核心上传函数
# ============================================================

def upload_to_imgbb(image_source: str) -> dict:
    """
    上传图片到 ImgBB（匿名，无需 API 密钥）
    
    Args:
        image_source: 本地文件路径 或 网络图片 URL
    
    Returns:
        包含上传结果的字典
    """
    if image_source.startswith(('http://', 'https://', 'ftp://')):
        # 网络图片 URL
        post_data = {
            'source': image_source,
            'type': 'url',
            'action': 'upload',
        }
        data = urllib.parse.urlencode(post_data).encode()
        req = urllib.request.Request('https://imgbb.com/json', data=data)
    else:
        # 本地文件
        if not os.path.exists(image_source):
            raise FileNotFoundError(f"文件不存在: {image_source}")
        
        file_size = os.path.getsize(image_source)
        boundary = '----WebKitFormBoundary' + base64.b64encode(os.urandom(15)).decode()
        
        with open(image_source, 'rb') as f:
            file_data = f.read()
        
        filename = os.path.basename(image_source)
        
        body = []
        body.append(f'--{boundary}'.encode())
        body.append(f'Content-Disposition: form-data; name="source"; filename="{filename}"'.encode())
        body.append(b'Content-Type: application/octet-stream')
        body.append(b'')
        body.append(file_data)
        
        body.append(f'--{boundary}'.encode())
        body.append(b'Content-Disposition: form-data; name="type"')
        body.append(b'')
        body.append(b'file')
        
        body.append(f'--{boundary}'.encode())
        body.append(b'Content-Disposition: form-data; name="action"')
        body.append(b'')
        body.append(b'upload')
        
        body.append(f'--{boundary}'.encode())
        body.append(b'Content-Disposition: form-data; name="name"')
        body.append(b'')
        body.append(b'image')
        
        body.append(f'--{boundary}--'.encode())
        
        body_data = b'\r\n'.join(body)
        
        req = urllib.request.Request(
            'https://imgbb.com/json',
            data=body_data,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'User-Agent': 'Mozilla/5.0 (compatible; ImageUploader/1.0)',
            }
        )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        raise RuntimeError(f"上传失败: {e}")
    
    if result.get('status_code') != 200:
        error_msg = result.get('status_txt', '未知错误')
        raise RuntimeError(f"ImgBB 返回错误: {error_msg}")
    
    image_data = result.get('image', {})
    
    return {
        'success': True,
        'url': image_data.get('url', '').replace('\\/', '/'),
        'url_viewer': image_data.get('url_viewer', '').replace('\\/', '/'),
        'delete_url': image_data.get('delete_url', '').replace('\\/', '/'),
        'display_url': image_data.get('display_url', '').replace('\\/', '/'),
        'filename': image_data.get('filename', ''),
        'width': image_data.get('width', 0),
        'height': image_data.get('height', 0),
        'size': image_data.get('size', 0),
        'size_formatted': image_data.get('size_formatted', ''),
        'thumb_url': image_data.get('thumb', {}).get('url', '').replace('\\/', '/'),
    }


# ============================================================
# MCP Server 定义
# ============================================================

# 创建 MCP Server 实例
server = Server("imgbb-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的 MCP 工具"""
    return [
        Tool(
            name="upload_image",
            description="上传图片到 ImgBB 免费图床，支持本地文件路径或网络图片URL，返回公网可访问的图片链接",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "图片来源：本地文件路径（如 /tmp/image.png）或网络图片 URL（如 https://example.com/photo.jpg）",
                    }
                },
                "required": ["source"],
            },
        ),
        Tool(
            name="upload_image_from_url",
            description="从网络 URL 上传图片到 ImgBB 免费图床，返回公网可访问的图片链接",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "网络图片的完整 URL 地址",
                    }
                },
                "required": ["url"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """处理工具调用请求"""
    if name not in ["upload_image", "upload_image_from_url"]:
        raise ValueError(f"未知工具: {name}")
    
    if name == "upload_image_from_url":
        source = arguments["url"]
    else:
        source = arguments["source"]
    
    try:
        result = upload_to_imgbb(source)
        return [
            TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2),
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                }, ensure_ascii=False),
            )
        ]


# ============================================================
# 主入口
# ============================================================

async def main():
    """启动 MCP Server（stdio 模式）"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
