# ESP32 Toolchain Downloader (CN Mirror) 🚀

这是一个简单但强大的 Python 脚本，专为**加速 ESP32 开发环境配置**而设计。

它能够解析 Espressif 官方提供的 `package_esp32_index_cn.json` 索引文件，并自动从**国内镜像源 (dl.espressif.cn)** 批量下载指定版本的 ESP32 SDK 和编译工具链（GCC, OpenOCD 等）。

解决在国内网络环境下，Arduino IDE 或 PlatformIO 下载 ESP32 开发包速度极慢或连接超时的问题。

## ✨ 主要特性

* **⚡ 国内极速下载**：自动过滤并提取 `dl.espressif.cn` 域名的下载链接。
* **🛠️ 零依赖**：基于 Python 标准库编写，**无需 `pip install` 任何第三方库**即可运行。
* **🛡️ 健壮的下载策略**：内置三级降级下载机制，确保在各种环境下都能成功下载：
    1.  优先尝试 `wget` (显示详细进度条)。
    2.  失败则尝试 `curl` (Windows 10/11 自带)。
    3.  最后兜底使用 Python 原生 `urllib` 库 (确保 100% 可用性)。
* **💻 跨平台支持**：支持 Windows (32/64), Linux (x64/ARM), macOS (Intel/Apple Silicon) 的工具链匹配。

## 📂 目录结构

在使用前，请确保你的目录结构如下所示：

```text
.
├── esp32-download.py          # 主脚本
├── package_esp32_index_cn.json # 必需：官方索引文件 (需放置在同级目录)
└── README.md
