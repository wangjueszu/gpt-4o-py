"""
* 此脚本用于批量调用gpt-4o-image-vip及相关模型，处理多组提示词和图片，并返回处理结果
* 支持每个请求使用无图、单图或多图（最多10张）的情况
* 请确保已安装Python环境并安装所需依赖库（如requests，python-dotenv, json）
* 请复制.env.template为.env并填写您的API密钥
* 确保input和output目录存在或脚本有权限创建这些目录
* 批处理配置存放在input/tasks.json中
* 下载的图片和结果将保存在output目录中
"""

import os
import base64
import requests
import json
import time
import re
from dotenv import load_dotenv
from datetime import datetime

# 加载环境变量
load_dotenv()

# 目录配置
INPUT_DIR = os.path.join(os.getcwd(), "input")
OUTPUT_DIR = os.path.join(os.getcwd(), "output")
TASKS_FILE = os.path.join(INPUT_DIR, "tasks.json")

# 从环境变量获取配置
DEFAULT_MODEL = os.getenv("MODEL", "gpt-4o-image-vip")
API_URL = "https://api.tu-zi.com/v1/chat/completions"
API_TOKEN = os.getenv("API_TOKEN")
API_DELAY = int(os.getenv("API_DELAY", "2"))  # 默认2秒延迟

# 确保目录存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 验证API Token
if not API_TOKEN:
    print("错误：未设置API_TOKEN环境变量")
    print("请复制.env.template为.env并填写您的API密钥")
    exit(1)

# 准备请求数据
def prepare_image_data(image_path):
    """将图片转换为base64编码"""
    try:
        # 支持相对路径和绝对路径
        if not os.path.isabs(image_path):
            full_path = os.path.join(INPUT_DIR, "images", image_path)
        else:
            full_path = image_path
            
        with open(full_path, "rb") as img_file:
            encoded_data = base64.b64encode(img_file.read()).decode("utf-8")
            # 自动检测图片类型
            img_type = "png"  # 默认类型
            if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg"):
                img_type = "jpeg"
            print(f"已准备图片数据: {image_path}（内容已隐藏以确保安全）")
            return f"data:image/{img_type};base64,{encoded_data}"
    except Exception as e:
        print(f"准备图片数据时出错: {image_path} - {e}")
        raise

def process_task(task, task_id):
    """处理单个任务"""
    # 获取任务参数
    task_name = task.get("name", f"任务_{task_id}")
    prompt = task.get("prompt", "")
    images = task.get("images", [])
    model = task.get("model", DEFAULT_MODEL)
    
    # 创建任务输出目录
    task_output_dir = os.path.join(OUTPUT_DIR, f"{task_id}_{task_name}")
    os.makedirs(task_output_dir, exist_ok=True)
    
    # 保存任务信息
    with open(os.path.join(task_output_dir, "task_info.json"), "w", encoding="utf-8") as f:
        json.dump({
            "id": task_id,
            "name": task_name,
            "prompt": prompt,
            "images": images,
            "model": model,
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    # 验证图片数量
    if len(images) > 10:
        print(f"错误：任务 {task_name} 的图片数量不能超过10张")
        return False
    
    # 添加调试信息
    print(f"\n处理任务: {task_name} (ID: {task_id})")
    print(f"使用的模型: {model}")
    print(f"图片数量: {len(images)}")
    for i, img in enumerate(images, 1):
        print(f"图片 {i} 路径: {img}")
    
    # 构建消息内容
    message_content = [{"type": "text", "text": prompt}]
    
    # 添加图片到消息内容
    for image_path in images:
        try:
            image_data = prepare_image_data(image_path)
            message_content.append({
                "type": "image_url",
                "image_url": {"url": image_data}
            })
        except Exception as e:
            print(f"处理图片时出错: {image_path} - {e}")
            return False
    
    data = {
        "model": model,
        "stream": False, 
        "messages": [
            {
                "role": "user",
                "content": message_content
            }
        ],
    }
    
    # 添加调试信息
    print(f"请求数据已准备好（图片内容已隐藏）。")
    
    # 发送请求
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=1200)
        print(f"响应状态码: {response.status_code}")
        
        # 保存原始响应
        with open(os.path.join(task_output_dir, "response.json"), "w", encoding="utf-8") as f:
            f.write(response.text)
    except Exception as e:
        print(f"发送请求时出错: {e}")
        return False
    
    # 处理响应
    if response.status_code != 200:
        print(f"API 错误: {response.status_code} - {response.text}")
        return False
    
    try:
        result = response.json()
    except Exception as e:
        print(f"解析响应 JSON 时出错: {e}")
        return False
    
    if "error" in result:
        print(f"API 错误: {result['error']['message']}")
        return False
    
    # 保存文本响应
    if "choices" in result and isinstance(result["choices"], list):
        # 提取文本内容
        text_content = ""
        for choice in result["choices"]:
            if "message" in choice and "content" in choice["message"]:
                text_content += choice["message"]["content"] + "\n\n"
                
        # 保存文本内容
        with open(os.path.join(task_output_dir, "response_text.md"), "w", encoding="utf-8") as f:
            f.write(text_content)
    
    # 遍历result，提取content字段中的图片地址并保存
    if "choices" in result and isinstance(result["choices"], list):
        download_success = False
        for choice in result["choices"]:
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                print(f"正在处理内容: {content[:100]}...")  # 只显示内容的前100个字符
                
                # 使用正则表达式提取markdown中的图片地址
                matches = re.findall(r"!\[.*?\]\((https?://[^\s]+)\)", content)
                for idx, image_url in enumerate(matches):
                    try:
                        print(f"正在下载图片: {image_url}")
                        image_data = requests.get(image_url).content
                        file_name = f"{result['id']}-{choice['index']}-{idx}.png"
                        output_path = os.path.join(task_output_dir, file_name)
                        with open(output_path, "wb") as f:
                            f.write(image_data)
                        print(f"图片已保存到: {output_path}")
                        download_success = True
                    except Exception as e:
                        print(f"无法下载图片数据: {image_url} - {e}")
        if not download_success:
            print("未成功下载任何图片。")
    else:
        print("返回值格式错误。")
    
    return True

def load_tasks():
    """从tasks.json加载任务列表"""
    # 如果任务文件不存在，创建一个示例
    if not os.path.exists(TASKS_FILE):
        # 确保images目录存在
        os.makedirs(os.path.join(INPUT_DIR, "images"), exist_ok=True)
        
        example_tasks = [
            {
                "name": "示例任务1",
                "prompt": "请描述这张图片。",
                "images": ["example.jpg"],
                "model": "gpt-4o-image-vip"
            },
            {
                "name": "示例任务2",
                "prompt": "请创作一套全新的 chibi sticker，共六个独特姿势，以用户形象为主角。",
                "images": ["example.jpg"],
                "model": "gpt-4o-image-vip"
            }
        ]
        
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(example_tasks, f, ensure_ascii=False, indent=2)
            
        print(f"已创建示例任务文件: {TASKS_FILE}")
        print("请在执行批处理前编辑此文件！")
        exit(0)
    
    # 加载任务
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        print(f"已加载 {len(tasks)} 个任务")
        return tasks
    except Exception as e:
        print(f"加载任务文件失败: {e}")
        exit(1)

def main():
    """主函数，处理批量任务"""
    print("=== GPT-4o 批量处理工具 ===")
    
    # 加载任务
    tasks = load_tasks()
    
    # 任务总数
    total_tasks = len(tasks)
    success_count = 0
    
    # 处理每个任务
    for idx, task in enumerate(tasks, 1):
        print(f"\n[{idx}/{total_tasks}] 开始处理任务...")
        
        task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{idx}"
        success = process_task(task, task_id)
        
        if success:
            success_count += 1
            print(f"任务 {idx}/{total_tasks} 处理成功")
        else:
            print(f"任务 {idx}/{total_tasks} 处理失败")
            
        # 为API限流添加间隔(可选)
        if idx < total_tasks:
            delay = API_DELAY  # 使用环境变量中的延迟设置
            print(f"等待 {delay} 秒后继续下一个任务...")
            time.sleep(delay)
    
    # 输出结果统计
    print("\n=== 批量处理完成 ===")
    print(f"总任务数: {total_tasks}")
    print(f"成功任务: {success_count}")
    print(f"失败任务: {total_tasks - success_count}")
    print(f"处理结果保存在: {OUTPUT_DIR}")

if __name__ == "__main__":
    main() 