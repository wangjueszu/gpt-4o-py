# 🚀 GPT-4o 绘图批量处理工具

<div align="center">

![Version](https://img.shields.io/badge/版本-1.0-blue)
![Python](https://img.shields.io/badge/Python-3.6+-brightgreen)
![License](https://img.shields.io/badge/许可证-MIT-orange)

**解锁 GPT-4o 的无限可能 | 一次处理成百上千任务 | 多模态批量生成**

</div>

## 🖼️ 图片保存与多图支持

- 工具现已支持批量下载任务返回的多张图片。
- 仅保存 markdown 文本中 `[点击下载](...)` 格式的图片链接，避免重复下载预览图片。
- 图片会自动识别扩展名（如 .png/.jpg/.webp 等），并保存在每个任务的 output 子目录下。
- 支持每个任务返回和保存多张图片。

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

### 🆕 gpt-4o-image-vip 模型更新

- 现在可以通过 chat 格式调用 gpt-4o-image-vip。
- 在提示词（prompt）中要求返回"1/2/4"张图片（如：请返回4张不同风格的图片），即可获得对应数量的图片，默认返回2张。
- 价格不会增加，仍然为 0.07 元/次请求。

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

## 📸 使用案例展示

以下是使用本工具生成的一些实际案例，展示了不同场景下GPT-4o的多模态能力。

### 🎎 中式婚礼Q版3D人物 -by [贝壳里奇](https://x.com/balconychy)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/1.png" width="300" alt="中式婚礼Q版3D人物">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/1-old.jpg)

**提示词**：
```
将照片里的两个人转换成Q版3D人物，中式古装婚礼，大红颜色，背景囍字剪纸风格图案。 服饰要求：写实，男士身着长袍马褂，主体为红色，上面以金色绣龙纹图案，彰显尊贵大气 ，胸前系着大红花，寓意喜庆吉祥。女士所穿是秀禾服，同样以红色为基调，饰有精美的金色花纹与凤凰刺绣，展现出典雅华丽之感 ，头上搭配花朵发饰，增添柔美温婉气质。二者皆为中式婚礼中经典着装，蕴含着对新人婚姻美满的祝福。 头饰要求： 男士：中式状元帽，主体红色，饰有金色纹样，帽顶有精致金饰，尽显传统儒雅庄重。 女士：凤冠造型,以红色花朵为中心,搭配金色立体装饰与垂坠流苏,华丽富贵,古典韵味十足。注意面部特征保持一致。
```

### 💍 求婚场景Q版3D人物-by [贝壳里奇](https://x.com/balconychy)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/2.png" width="300" alt="求婚场景Q版3D人物">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/2-old.jpg)

**提示词**：
```
将照片里的两个人转换成Q版3D人物，场景换成求婚，背景换成淡雅五彩花瓣做的拱门，背景换成浪漫颜色，地上散落着玫瑰花瓣。除了人物采用Q版3D人物风格，其他环境采用真实写实风格。注意面部特征保持一致
```

### 🎨 吉卜力风格化 -by [兔子](https://x.com/ovst36099)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/3.png" width="300" alt="吉卜力风格化">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/3-old.jpg)

**提示词**：
```
依据图片内容，将其转化为千与千寻、风之谷那样画风的图画；注意保持人物、场景、色彩一致。
```

### 🎁 双人浪漫3D摆件 -by [宝玉](https://x.com/dotey)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/4.png" width="300" alt="双人浪漫3D摆件">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/4-old.jpg)

**提示词**：
```
根据照片上的内容打造一款细致精美、萌趣可爱的3D渲染收藏摆件，装置在柔和粉彩色调、温馨浪漫的展示盒中。展示盒为浅奶油色搭配柔和的金色装饰，形似精致的便携珠宝盒。打开盒盖，呈现出一幕温暖浪漫的场景：两位Q版角色正甜蜜相望。盒顶雕刻着某某某（见文末）的字样，周围点缀着小巧精致的星星与爱心图案。盒内站着照片上的女性，手中捧着一束小巧的白色花束。她的身旁是她的伴侣，照片上的男性。两人都拥有大而闪亮、充满表现力的眼睛，以及柔和、温暖的微笑，传递出浓浓的爱意和迷人的气质。他们身后有一扇圆形窗户，透过窗户能看到阳光明媚的中国古典小镇天际线和轻柔飘浮的云朵。盒内以温暖的柔和光线进行照明，背景中漂浮着花瓣点缀气氛。整个展示盒和角色的色调优雅和谐，营造出一个奢华而梦幻的迷你纪念品场景。某某某的具体内容为：我爱你。
```

### 🧸 公仔包装盒 -by [宝玉](https://x.com/dotey)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/5.png" width="300" alt="公仔包装盒">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/5-old.jpg)

**提示词**：
```
把照片中的人物变成 泡泡玛特 公仔包装盒的风格，以等距视角（isometric）呈现，并在包装盒上标注标题为某某（具体见文末）。包装盒内展示的是照片中人物形象，旁边搭配有日常必备物品（具体见文末）同时，在包装盒旁边还应呈现该公仔本体的实物效果，采用逼真的、具有真实感的渲染风格。

标题为雷总，日常必备物品帽子、鞋子、耳坠。
```

### 📝 手绘信息图表卡  -by [兔子](https://x.com/ovst36099)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/6-small.png" width="300" alt="手绘信息图表卡">

**提示词**：
```
创作一张9:16竖版手绘信息图表卡，背景为质感米白或灰白纹理纸，标题使用红黑撞色毛笔大字（中文草书）。内容架构包含2-4个主题区块，每个区块配有简笔插画（如人物、问号、符号等），并附上中文草书短句，字体遒劲流畅，兼具辨识度。视觉要点包括：泼墨式标题的冲击力，手绘元素的留白感，图文错落以营造思辨氛围，关键处使用朱砂墨色点睛。文字输出时，请查阅新华字典中文字笔画顺序。

文案布局方面，设置**醒世三问**朱砂大标题，接着是三句话：1. 执念何所缚？配有解绳的简笔插画；2. 心镜可明台？配有拭镜的小插图；3. 浮云归处是？绘有远山和飞鸟的场景。
```

### 🔮 Q版牵手穿越 -by [宝玉](https://x.com/dotey)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/8.png" width="300" alt="Q版牵手穿越">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/8-old.jpg)

**提示词**：
```
照片中的角色的3D Q版形象穿过传送门，牵着观众的手，在将观众拉向前时动态地回头一看。传送门外的背景是观众的现实世界，传送门内是角色所处的3D Q版世界，细节可以参考照片，整体呈蓝色调，和现实世界形成鲜明对比。传送门散发着神秘的蓝色和紫色色调，是两个世界之间的完美椭圆形框架处在画面中间。从第三人称视角拍摄的摄像机角度，显示观看者的手被拉入角色世界。

现实世界一个典型的程序员的书房，有书桌，显示器和笔记本电脑。
```

### 🧙‍♂️ 分帽院 -by [-Zho-](https://x.com/ZHO_ZHO_ZHO)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/9.png" width="300" alt="分帽院">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/9-old.jpg)

**提示词**：
```
先根据上传的图片人物特点分配到，狮院：勇敢、活力、骑士精神和正义感；蛇院：野心、精明、重视荣耀、胜利至上；鹰院：机敏、聪慧和博学 ；猩院：正直、忠诚、诚实和不畏辛苦。然后每个学院对应不同颜色和象征，狮院：狮子，代表元素为火，颜色为红色和金色；蛇院：蛇，代表元素为水，颜色为绿色和银色 ；鹰院：鹰，代表元素为风，颜色为蓝色和青铜色 ；猩院：猩猩，代表元素为土，颜色为黄色和黑色 。生成人物背景和元素就要自配所属学院 ，把图片中的人物头像Q版人像大头照，图形渐变背景区域，保持学院特点，随时添加一些魔法小道具，如猫头鹰、魔杖等。
```

### 📱 Q版APP图标 -by [宝玉](https://x.com/dotey)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/10.png" width="300" alt="Q版APP图标">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/10-old.jpg)

**提示词**：
```
把这张照片设计成一个3D风格的Q版APP图标，保留人物特征，风格要可爱一些，人物要稍微超出图标背景边框。
```

### 🚽 极简主义3D插画 -by [宝玉](https://x.com/dotey)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/11-small.png" width="300" alt="极简主义3D插画">

**提示词**：
```
这幅画的艺术风格应该是极简主义的3D插画。整体造型采用圆润的边缘和简化几何造型，外形平滑且柔和，尽量减少复杂的细节。色彩方面，画面主色调为柔和的米色和浅灰色，给人温暖的感觉，而焦点元素则使用了暖橙色，带有一定的视觉冲击力。色彩过渡应该是柔和的渐变，避免使用强烈的阴影和高光，以保持画面整体的平滑感。光照部分使用柔和、漫反射的光源，来自上方略偏右，阴影风格也应当微妙且漫射，无锐利或强对比度的阴影。这种柔和的光照可以让画面看起来更具亲和力和现代感。 材质方面，表面应当是哑光且平滑的，细微的明暗变化能够增加材质的层次感，但避免明显的光泽感。反射性很低，力求简洁而不华丽。构图上，画面中的马桶是单一、居中的物体，周围留出大量的负空间，让主体更加突出，视角稍微倾斜，以呈现出适度的三维感，但没有明显的景深效果。背景采用纯色，低饱和度的色调，应该与主体的色彩协调，不干扰视线。字体排版的设计要求也非常简洁，采用无衬线字体，字体的颜色为灰色，放置在左下角，尺寸较小且不突出，与背景色形成低对比度，保持整体简洁的氛围。在渲染风格上，使用简化的低多边形3D渲染风格，细节程度适中，重点突出形状和色彩，避免复杂的纹理和细节，力求呈现干净、简洁的视觉效果，强调现代感和亲和力。

画的内容是一个马桶。
```

### 👚 9宫格试衣服  -by [兔子](https://x.com/ovst36099)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/12.png" width="300" alt="9宫格试衣服">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/12-old.jpg)

**提示词**：
```
使用九宫格的方式给模特穿上不同流行款衣服，请保持人物面部、主体特征一致。
```

### 🔮 3D Q版水晶球 -by [贝壳里奇](https://x.com/balconychy)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/13.png" width="300" alt="3D Q版水晶球">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/13-old.jpg)

**提示词**：
```
将附图中的人物转换成水晶球场景。 整体环境：水晶球放在窗户旁桌面上，背景模糊，暖色调。阳光透过球体，洒下点点金光，照亮了周围的黑暗。 水晶球内部：人物是可爱Q版3D造型，相互之间满眼的爱意。
```

### 🐱 心中的灵兽 -by [贝壳里奇](https://x.com/balconychy)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/14.png" width="300" alt="心中的灵兽">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/14-old.jpg)

**提示词**：
```
画一个动物，头换成图中的人，并且将五官中的一个特征换成动物的特征。动物请根据人像的特征选择。
```

### 💇 九宫格发型  -by [兔子](https://x.com/ovst36099)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/15.png" width="300" alt="九宫格发型">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/15-old.jpg)

**提示词**：
```
截图图片人物头像部分，已九宫格的方式生成这个人不同的发型头像，注意保持人物面部特征一致。
```

### 👩‍✈️ 职业生成 -by [-Zho-](https://x.com/ZHO_ZHO_ZHO)
<img src="https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/16.png" width="300" alt="职业生成">

**原图**：[查看原图](https://tuziai.oss-cn-shenzhen.aliyuncs.com/small/16-old.jpg)

**提示词**：
```
为图片人物生成不同职业风的OOTD，时尚穿搭和配饰，和人物色系一致的纯色背景，Q版 3d，c4d渲染，保持人脸特征，姿势都要保持一致，人物的比例腿很修长；顶部文字：OOTD，左侧为人物ootd q版形象，右侧为穿搭的单件展示。

本次职业为：飞行员。
```

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