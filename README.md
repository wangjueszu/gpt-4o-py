# GPT-4o 批量处理工具

这是一个用于批量调用 gpt-4o-image-vip 及相关模型的脚本，可以处理多组提示词和图片，并获取生成结果。

## 功能特点

- 支持批量处理多个任务
- 每个任务可以使用不同的提示词和图片
- 支持无图、单图或多图（最多10张）的请求
- 自动保存生成的文本和图片
- 详细的日志和任务状态跟踪
- 任务管理辅助工具，方便创建和编辑任务

## 目录结构

```
/
├── gpt-4o-batch.py      # 批量处理脚本
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

## 使用步骤

### 1. 环境准备

确保已安装Python环境（Python 3.6+）和所需依赖库：

```bash
pip install requests python-dotenv
```

### 2. 配置API密钥

复制`.env.template`文件为`.env`，并填写您的API密钥：

```bash
cp .env.template .env
```

编辑`.env`文件：

```
API_TOKEN=your_api_token_here
MODEL=gpt-4o-image-vip
API_DELAY=2  # 任务间隔时间（可选）
```

### 3. 创建任务配置

#### 方法一：使用任务管理辅助工具（推荐）

运行任务管理辅助工具：

```bash
python task_helper.py
```

通过交互式菜单可以：
- 查看所有任务
- 创建新任务
- 编辑现有任务
- 删除任务
- 导入示例任务
- 备份任务文件

#### 方法二：手动编辑任务文件

首次运行批处理脚本将自动创建示例任务配置文件`input/tasks.json`：

```bash
python gpt-4o-batch.py
```

然后编辑`input/tasks.json`文件，添加您的任务：

```json
[
  {
    "name": "任务1",
    "prompt": "请描述这张图片。",
    "images": ["image1.jpg"],
    "model": "gpt-4o-image-vip"
  },
  {
    "name": "任务2",
    "prompt": "请创作一套全新的 chibi sticker，共六个独特姿势，以用户形象为主角。",
    "images": ["image2.jpg"],
    "model": "gpt-4o-image-vip"
  }
]
```

您也可以参考`input/tasks.json.example`中的示例任务配置。

### 4. 准备图片

将需要处理的图片放在`input/images/`目录下，并在任务配置中引用它们。

图片路径可以是相对于`input/images/`的相对路径，也可以是绝对路径。

### 5. 运行批处理

```bash
python gpt-4o-batch.py
```

脚本将按顺序处理所有任务，并将结果保存在`output/`目录中。

## tasks.json 配置参数

每个任务支持以下参数：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | 字符串 | 是 | 任务名称 |
| prompt | 字符串 | 是 | 提示词 |
| images | 数组 | 否 | 图片文件名数组（最多10张） |
| model | 字符串 | 否 | 使用的模型（默认为环境变量中设置的值） |

## 输出说明

每个任务会在`output/`目录下创建一个独立的文件夹，命名格式为`[任务ID]_[任务名称]`，包含以下文件：

- `task_info.json`：任务配置信息
- `response.json`：API原始响应
- `response_text.md`：生成的文本内容
- 图片文件：下载的所有生成图片

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
- 默认任务之间有2秒的延迟，可在.env文件中通过API_DELAY参数调整 