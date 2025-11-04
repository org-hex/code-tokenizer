# Code Tokenizer

**Language:** [English](README.md) | [中文](README_CN.md)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)
![PyPI Version](https://img.shields.io/pypi/v/code-tokenizer.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

A simple command-line tool to quickly calculate AI model Token usage for entire projects, helping you determine if your project is suitable for direct AI analysis.

Modern LLM models (like GPT-4 Turbo, Claude-4) have context lengths of 200k+, which can load entire project codebases at once. If your project's total code Token count is less than 200k, you can submit the entire project to LLM models for analysis at once, rather than having the model read files one by one. This tool provides a one-click feature to package all code into a single file, making this process easy.

## 🎯 Features

- **Token Statistics** - Accurately calculate Token counts for your entire project's code across different AI models
- **Context Analysis** - Display the percentage of each AI model's context window used by your project to determine if it exceeds limits
- **One-Click Packaging** - Merge all code files into a single file for easy one-time submission to AI models
- **Smart Filtering** - Automatically exclude irrelevant files (node_modules, .git, etc.) and keep only core code

## 📦 Installation

```bash
pip install code-tokenizer
```

## 🚀 Usage

```bash
# Count Tokens for current project
code-tokenizer

# Count Tokens for specified project
code-tokenizer /path/to/project

# Count and package all code into a single file
code-tokenizer --package my_project.txt

# Show only the top 5 largest files
code-tokenizer --max-show 5
```

## 📊 Example Output

![Code Tokenizer Output](docs/images/screenshot.png)

## 🔧 Supported File Types

Go, Python, JavaScript, TypeScript, Java, C/C++, Swift, Kotlin, PHP, Ruby, Vue, HTML, CSS, YAML, JSON, XML, SQL, Shell scripts, Markdown, and more

## ⚠️ Disclaimer

This project is developed based on [OpenAI tiktoken](https://github.com/openai/tiktoken). Token count results are for reference only and may vary due to tokenizer differences across AI models.

**Privacy Protection:** This project runs locally only and does not upload any code information to external servers, protecting your code privacy and security.

## 📄 License

MIT License