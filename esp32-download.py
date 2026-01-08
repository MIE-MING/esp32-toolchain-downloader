#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import subprocess
import sys
import urllib.request  # 引入原生下载库作为保底

JSON_FILE = 'package_esp32_index_cn.json'

SYS_LIST = [
    'windows-32',
    'windows-64',
    'linux-64',
    'linux-32',
    'linux-arm64',
    'linux-armv7',
    'macos-x86_64',
    'macos-arm64',
]

SYS_MAP = {
    'windows-32': 'i686-mingw32',
    'windows-64': 'x86_64-mingw32',
    'linux-64': 'x86_64-pc-linux-gnu',
    'linux-32': 'i686-pc-linux-gnu',
    'linux-arm64': 'aarch64-linux-gnu',
    'linux-armv7': 'arm-linux-gnueabihf',
    'macos-x86_64': 'x86_64-apple-darwin',
    'macos-arm64': 'arm64-apple-darwin',
}

def load_index():
    if not os.path.isfile(JSON_FILE):
        print(f'当前目录未找到 {JSON_FILE}，请把文件放到本脚本同级目录')
        sys.exit(1)
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_versions(data):
    versions = set()
    for pkg in data['packages']:
        if pkg['name'] == 'esp32':
            for pf in pkg['platforms']:
                versions.add(pf['version'])
    return sorted(versions, reverse=True)

def build_tools_dict(data):
    tools = {}
    for t in data['packages'][0]['tools']:
        key = (t['name'], t['version'])
        tools[key] = t['systems']
    return tools

def pick_cn_url(systems, host):
    for s in systems:
        if s['host'] == host and s['url'].startswith('https://dl.espressif.cn/'):
            return s['url']
    return None

def download(url: str):
    filename = url.split('/')[-1]
    
    # 1. 优先尝试 wget (显示效果好)
    try:
        if subprocess.call(['wget', '-q', '--show-progress', '-O', filename, url]) == 0:
            return
    except FileNotFoundError:
        pass # 系统未安装 wget，继续尝试下一项
    except Exception as e:
        print(f"wget 调用出错: {e}")

    # 2. 尝试 curl (Windows 10/11 自带)
    try:
        if subprocess.call(['curl', '-L', '-o', filename, url]) == 0:
            return
    except FileNotFoundError:
        pass # 系统未安装 curl，继续尝试下一项
    except Exception as e:
        print(f"curl 调用出错: {e}")

    # 3. 使用 Python 原生库下载 (保底方案，无需额外软件)
    print(f'正在使用 Python 原生下载库获取 {filename} ...')
    try:
        def report(block_num, block_size, total_size):
            if total_size > 0:
                percent = block_num * block_size * 100 / total_size
                # 简单的进度显示
                if percent > 100: percent = 100
                sys.stdout.write(f"\r  已下载: {percent:.1f}%")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, filename, reporthook=report)
        print() # 下载完成后换行
        return
    except Exception as e:
        print(f'\n下载失败：{url}')
        print(f'错误详情：{e}')

def main():
    data = load_index()
    versions = get_versions(data)

    print('请选择 ESP32 版本：')
    for idx, ver in enumerate(versions, 1):
        print(f'  {idx}. {ver}')
    try:
        ver_idx = int(input('输入序号：')) - 1
        version = versions[ver_idx]
    except (ValueError, IndexError):
        print('选择无效')
        sys.exit(1)

    print('\n请选择系统版本：')
    for idx, sys_name in enumerate(SYS_LIST, 1):
        print(f'  {idx}. {sys_name}')
    try:
        sys_idx = int(input('输入序号：')) - 1
        sys_key = SYS_LIST[sys_idx]
        host = SYS_MAP[sys_key]
    except (ValueError, IndexError):
        print('选择无效')
        sys.exit(1)

    # 查找对应版本的平台信息
    pf = next((p for p in data['packages'][0]['platforms'] if p['version'] == version), None)
    if not pf:
        print(f"未找到版本 {version} 的平台定义")
        sys.exit(1)

    tools_map = build_tools_dict(data)

    downloads = []
    # 平台核心包 (Arduino 核心)
    if pf.get('url', '').startswith('https://dl.espressif.cn/'):
        downloads.append(('esp32-platform', pf['url']))

    # 工具链依赖
    for dep in pf['toolsDependencies']:
        name, ver_tool = dep['name'], dep['version']
        systems = tools_map.get((name, ver_tool))
        if not systems:
            continue
        url = pick_cn_url(systems, host)
        if url:
            downloads.append((name, url))

    if not downloads:
        print('未找到任何 dl.espressif.cn 的下载地址')
        sys.exit(0)

    print('\n找到以下可下载项：')
    for name, url in downloads:
        print(f'  {name} : {url}')

    confirm = input('\n是否开始下载？输入 Y 确认：').strip().lower()
    if confirm != 'y':
        print('已取消下载')
        sys.exit(0)

    os.makedirs(version, exist_ok=True)
    os.chdir(version)

    for name, url in downloads:
        print(f'正在下载 {name} ...')
        download(url)

    print('全部下载完成！')

if __name__ == '__main__':
    main()