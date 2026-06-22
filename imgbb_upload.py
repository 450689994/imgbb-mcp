#!/usr/bin/env python3
"""
ImgBB 图床上传工具 - 匿名上传图片到 ImgBB 并获取公网 URL

用法:
    python3 imgbb_upload.py <图片文件路径或URL>
    
示例:
    python3 imgbb_upload.py /tmp/myimage.png
    python3 imgbb_upload.py https://example.com/image.jpg
"""

import sys
import json
import os
import base64
import urllib.request
import urllib.parse


def upload_to_imgbb(image_source: str) -> dict:
    """
    上传图片到 ImgBB（匿名，无需 API 密钥）
    
    Args:
        image_source: 本地文件路径 或 网络图片 URL
    
    Returns:
        包含上传结果的字典，包含 url、delete_url、url_viewer 等字段
    """
    # 判断是本地文件还是 URL
    if image_source.startswith(('http://', 'https://', 'ftp://')):
        # 网络图片 URL - 直接传 URL
        print(f"📥 检测到网络图片 URL: {image_source}")
        post_data = {
            'source': image_source,
            'type': 'url',
            'action': 'upload',
        }
        data = urllib.parse.urlencode(post_data).encode()
        req = urllib.request.Request('https://imgbb.com/json', data=data)
    else:
        # 本地文件 - 读取并作为文件上传
        if not os.path.exists(image_source):
            raise FileNotFoundError(f"文件不存在: {image_source}")
        
        file_size = os.path.getsize(image_source)
        print(f"📂 本地文件: {image_source} ({file_size/1024:.1f} KB)")
        
        # 使用 multipart/form-data 上传
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
    
    # 发送请求
    print("📤 正在上传到 ImgBB...")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode())
    except Exception as e:
        raise RuntimeError(f"上传失败: {e}")
    
    # 检查结果
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


def main():
    if len(sys.argv) < 2:
        print("用法: python3 imgbb_upload.py <图片文件路径或URL>")
        print("示例: python3 imgbb_upload.py /tmp/myimage.png")
        print("      python3 imgbb_upload.py https://example.com/image.jpg")
        sys.exit(1)
    
    image_source = sys.argv[1]
    
    try:
        result = upload_to_imgbb(image_source)
        
        print("\n" + "=" * 60)
        print("✅ 上传成功！")
        print("=" * 60)
        print(f"📌 图片 URL:    {result['url']}")
        print(f"👁️ 查看链接:    {result['url_viewer']}")
        print(f"🗑️ 删除链接:    {result['delete_url']}")
        print(f"📏 尺寸:        {result['width']}x{result['height']}")
        print(f"📦 大小:        {result['size_formatted']}")
        print("=" * 60)
        
        # 输出 JSON 格式供程序调用
        print("\n--- JSON 输出 ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
