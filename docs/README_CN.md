# Code Tokenizer

**语言:** [English](../README.md) | [中文](README_CN.md)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)
![PyPI Version](https://img.shields.io/pypi/v/code-tokenizer.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)


一个简单的命令行工具，快速统计整个项目的AI模型Token使用量，帮你判断项目是否适合直接给AI分析。

现代LLM模型（如GPT-4 Turbo、Claude-4）的上下文长度已达200k+，完全可以一次性加载整个项目代码。如果项目的所有代码加起来Token数小于200k，完全可以把整个项目一次性提交给LLM模型进行分析，而不是逐个文件让模型读取。本工具提供了一键打包所有代码到单文件的功能，让你轻松实现这一点。

## 🎯 功能

- **Token统计** - 精确计算整个项目的代码在不同AI模型中的Token数量
- **上下文分析** - 显示项目占用各AI模型上下文窗口的比例，判断是否超出限制
- **一键打包** - 将所有代码文件合并为单个文件，方便一次性提交给AI
- **智能过滤** - 自动排除无关文件（node_modules、.git等），保留核心代码

## 📦 安装

```bash
pip install code-tokenizer
```

## 🚀 使用

```bash
# 统计当前项目的Token数量
code-tokenizer

# 统计指定项目的Token数量
code-tokenizer /path/to/project

# 统计并打包所有代码到单个文件
code-tokenizer --package my_project.txt

# 只显示最大的5个文件
code-tokenizer --max-show 5
```

## 📊 运行示例

![Code Tokenizer Output](docs/images/screenshot.png)

## 🔧 支持的文件类型

Go, Python, JavaScript, TypeScript, Java, C/C++, Swift, Kotlin, PHP, Ruby, Vue, HTML, CSS, YAML, JSON, XML, SQL, Shell脚本, Markdown等

## ⚠️ 免责声明

本项目基于 [OpenAI tiktoken](https://github.com/openai/tiktoken) 开发。Token统计结果因不同AI模型的分词器差异仅供参考。

**隐私保护：** 本项目仅在本地运行，不会上传任何代码信息到外部服务器，保护您的代码隐私安全。

## 📄 许可证

MIT License