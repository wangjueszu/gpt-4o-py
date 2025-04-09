# 🚀 GPT-4o 批量处理工具

<div align="center">

![Version](https://img.shields.io/badge/版本-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.6+-brightgreen)
![License](https://img.shields.io/badge/许可证-MIT-orange)

**解锁 GPT-4o 的无限可能 | 一次处理成百上千任务 | 多模态批量生成**

</div>

## 准备工作

在开始使用本工具前，请先完成以下准备：

1. 访问 [兔子 API Token 页面](https://api.tu-zi.com/token) 创建您的 API Token
2. 记录 API 信息：
   - 对话请求地址: `https://api.tu-zi.com/v1/chat/completions`

### 2️⃣ 选择合适的模型

根据您的需求选择最适合的模型：

| 模型 | 计费方式 | 价格 | 稳定性 | 最佳用途 |
|------|---------|------|-------|----------|
| **gpt-4o-all** | 按token | 💰 | ⭐⭐⭐ | 小规模使用 |
| **gpt-4o-image** | 按次 | 💰 | ⭐⭐ | 个人自用 |
| **gpt-4o-image-vip** | 按次 | 💰💰 | ⭐⭐⭐⭐⭐ | 关键业务需求 |

> 💡 **专家提示**：对于重要项目，推荐使用 gpt-4o-image-vip 以获得最佳稳定性和性能。

## 📂 目录结构

```
/
├── gpt-4o-batch.py      # 顺序批量处理脚本
├── gpt-4o-concurrent.py # 并发批量处理脚本
├── task_helper.py       # 任务管理辅助工具
├── .env                 # 环境变量配置 (从.env.template复制)
├── input/               # 输入目录
│   ├── tasks.json       # 任务配置文件
│   ├── tasks.json.example # 任务配置示例
│   └── images/          # 图片存放目录
└── output/              # 输出目录
    └── [任务ID_任务名称]/  # 每个任务的输出目录
        ├── task_info.json    # 任务信息
        ├── response.json     # 原始API响应
        ├── response_text.md  # 文本响应
        └── [图片文件].png     # 下载的图片
```

## 📋 使用方法

### 🔧 环境准备

确保安装了Python 3.6+和所需依赖：

```bash
pip install requests python-dotenv concurrent.futures
```

### 🔑 配置API密钥

设置您的API凭证：

```bash
cp .env.template .env
```

编辑`.env`文件：

```
API_TOKEN=your_api_token_here
MODEL=gpt-4o-image-vip
API_DELAY=2  # 顺序处理版本间隔
MAX_WORKERS=5  # 并发处理版本线程数
API_RATE_LIMIT=0.5  # 并发版本API限流间隔
```

### 📝 创建任务

#### ✨ 方法一：使用交互式任务管理器（推荐）

```bash
python task_helper.py
```

<p align="center">
  <img src="https://via.placeholder.com/600x300?text=任务管理器界面" alt="任务管理器界面" width="600"/>
</p>

通过直观的菜单界面：
- 👁️ 查看所有任务
- ➕ 创建新任务
- ✏️ 编辑现有任务
- 🗑️ 删除任务
- 📥 导入示例任务
- 💾 备份任务文件

#### 方法二：手动配置

运行以下命令创建示例配置：

```bash
python gpt-4o-batch.py
```

然后编辑`input/tasks.json`文件：

```json
[
  {
    "name": "产品描述生成",
    "prompt": "请为这款产品创建一段吸引人的营销描述。",
    "images": ["product1.jpg"],
    "model": "gpt-4o-image-vip"
  },
  {
    "name": "表情包创作",
    "prompt": "请创作一套全新的chibi sticker，共六个独特姿势，以用户形象为主角。",
    "images": ["character.jpg"],
    "model": "gpt-4o-image-vip"
  }
]
```

### 🖼️ 准备图片

将图片放入`input/images/`目录，然后在任务中引用它们。

### ▶️  顺序处理版本

```bash
python gpt-4o-batch.py
```

顺序处理版本按照任务顺序一个接一个地处理，中间有设定的延迟时间。

#### 并发处理版本

```bash
python gpt-4o-concurrent.py
```

并发处理版本同时处理多个任务，大幅提高处理效率，并提供实时进度和预计完成时间。

## 两个版本的对比

| 功能 | 顺序处理 (gpt-4o-batch.py) | 并发处理 (gpt-4o-concurrent.py) |
|------|----------------------------|--------------------------------|
| 处理方式 | 按顺序逐个处理 | 多线程并发处理 |
| 处理速度 | 较慢 | 较快（取决于设置的并发数） |
| 性能消耗 | 较低 | 较高 |
| 适用场景 | 任务数量少，对API调用有严格限制 | 任务数量多，需要快速处理 |
| 进度显示 | 简单 | 详细（含进度百分比、预计完成时间） |
| 限流方式 | 固定间隔 | 令牌桶算法 |
| 配置参数 | API_DELAY | MAX_WORKERS, API_RATE_LIMIT |

## tasks.json 配置参数

每个任务支持以下参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | 字符串 | 是 | 任务名称 |
| prompt | 字符串 | 是 | 提示词 |
| images | 数组 | 否 | 图片文件名数组（最多10张） |
| model | 字符串 | 否 | 使用的模型（默认为环境变量中设置的值）。可选值: gpt-4o-all、gpt-4o-image、gpt-4o-image-vip |

## 📊 输出说明

每个任务在`output/`目录下创建独立文件夹：

- 📄 `task_info.json` - 任务配置信息
- 📄 `response.json` - 原始API响应
- 📄 `response_text.md` - 生成的文本内容
- 🖼️ 生成的图片文件

## GitHub使用说明

### 克隆仓库

```bash
git clone https://github.com/你的用户名/仓库名.git
cd 仓库名
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 创建必要的目录结构

目录结构已通过`.gitkeep`文件预设好，无需额外操作。

### 配置API凭证

根据第2步配置API密钥，复制`.env.template`为`.env`并填写您的API凭证。

### 注意事项

- 所有敏感信息（如API密钥）均已通过`.gitignore`排除，不会上传到GitHub
- 任务配置文件和图片需要在本地添加，不会自动同步到仓库
- 运行结果保存在`output/`目录中，也不会上传到GitHub

## 注意事项

- 请确保您的API密钥有效且有足够的额度
- 图片数量不能超过10张
- 处理大量任务时，请注意API调用限制
- 默认并发数为5，可在.env文件中通过MAX_WORKERS参数调整
- 并发处理时，为避免API限流，已内置令牌桶限流算法，默认每个请求间隔0.5秒 

<div align="center">
  <p>如果这个工具对您有帮助，请考虑给我们的仓库点个⭐️</p>
  <p>有问题或建议？<a href="mailto:wangjueszu@outlook.com">联系我们</a> </p>
  
</div> 