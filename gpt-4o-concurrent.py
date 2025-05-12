"""
* 此脚本用于并发批量调用gpt-4o-image-vip及相关模型，处理多组提示词和图片，并返回处理结果
* 支持每个请求使用无图、单图或多图（最多10张）的情况
* 请确保已安装Python环境并安装所需依赖库（如requests，python-dotenv, json, concurrent.futures）
* 请复制.env.template为.env并填写您的API密钥
* 确保input和output目录存在或脚本有权限创建这些目录
* 批处理配置存放在input/tasks.json中
* 下载的图片和结果将保存在output目录中
* 并发版本可以同时处理多个任务，提高效率
"""

import os
import base64
import requests
import json
import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
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
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "5"))  # 默认最大并发数为5
API_RATE_LIMIT = float(os.getenv("API_RATE_LIMIT", "0.5"))  # 默认每秒最多2个请求 (0.5秒间隔)

# 创建一个线程安全的锁，用于输出打印
print_lock = threading.Lock()

# 创建一个令牌桶，用于API限流
class TokenBucket:
    def __init__(self, rate_limit):
        self.rate_limit = rate_limit  # 时间间隔
        self.last_request_time = 0
        self.lock = threading.Lock()
        
    def consume(self):
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.rate_limit:
                sleep_time = self.rate_limit - time_since_last
                time.sleep(sleep_time)
                
            self.last_request_time = time.time()
            return True

# 实例化令牌桶
token_bucket = TokenBucket(API_RATE_LIMIT)

# 确保目录存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 验证API Token
if not API_TOKEN:
    print("错误：未设置API_TOKEN环境变量")
    print("请复制.env.template为.env并填写您的API密钥")
    exit(1)

# 线程安全的打印函数
def safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)

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
            safe_print(f"已准备图片数据: {image_path}（内容已隐藏以确保安全）")
            return f"data:image/{img_type};base64,{encoded_data}"
    except Exception as e:
        safe_print(f"准备图片数据时出错: {image_path} - {e}")
        raise

def process_task(task, task_idx, total_tasks):
    """处理单个任务"""
    # 生成任务ID
    task_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{task_idx}"
    
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
        safe_print(f"错误：任务 {task_name} (ID: {task_id}) 的图片数量不能超过10张")
        return {"success": False, "task_id": task_id, "task_name": task_name, "task_idx": task_idx}
    
    # 添加调试信息
    safe_print(f"\n[{task_idx}/{total_tasks}] 处理任务: {task_name} (ID: {task_id})")
    safe_print(f"使用的模型: {model}")
    safe_print(f"图片数量: {len(images)}")
    for i, img in enumerate(images, 1):
        safe_print(f"图片 {i} 路径: {img}")
    
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
            safe_print(f"处理图片时出错: {image_path} - {e}")
            return {"success": False, "task_id": task_id, "task_name": task_name, "task_idx": task_idx}
    
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
    safe_print(f"任务 {task_name} (ID: {task_id}) 请求数据已准备好（图片内容已隐藏）。")
    
    # 发送请求前等待令牌 (限流)
    token_bucket.consume()
    
    # 发送请求
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=1200)
        safe_print(f"任务 {task_name} (ID: {task_id}) 响应状态码: {response.status_code}")
        
        # 保存原始响应
        with open(os.path.join(task_output_dir, "response.json"), "w", encoding="utf-8") as f:
            f.write(response.text)
    except Exception as e:
        safe_print(f"任务 {task_name} (ID: {task_id}) 发送请求时出错: {e}")
        return {"success": False, "task_id": task_id, "task_name": task_name, "task_idx": task_idx}
    
    # 处理响应
    if response.status_code != 200:
        safe_print(f"任务 {task_name} (ID: {task_id}) API 错误: {response.status_code} - {response.text}")
        return {"success": False, "task_id": task_id, "task_name": task_name, "task_idx": task_idx}
    
    try:
        result = response.json()
    except Exception as e:
        safe_print(f"任务 {task_name} (ID: {task_id}) 解析响应 JSON 时出错: {e}")
        return {"success": False, "task_id": task_id, "task_name": task_name, "task_idx": task_idx}
    
    if "error" in result:
        safe_print(f"任务 {task_name} (ID: {task_id}) API 错误: {result['error']['message']}")
        return {"success": False, "task_id": task_id, "task_name": task_name, "task_idx": task_idx}
    
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
        download_count = 0
        for choice in result["choices"]:
            if "message" in choice and "content" in choice["message"]:
                content = choice["message"]["content"]
                safe_print(f"任务 {task_name} (ID: {task_id}) 正在处理内容: {content[:100]}...")  # 只显示内容的前100个字符

                # 只提取 [点击下载](http...) 这种格式的图片链接
                download_links = re.findall(r'\[点击下载\]\((https?://[^\s\)]+)\)', content)
                for idx, image_url in enumerate(download_links):
                    try:
                        safe_print(f"任务 {task_name} (ID: {task_id}) 正在下载图片: {image_url}")
                        image_data = requests.get(image_url).content
                        ext = "png"
                        m = re.search(r"\.([a-zA-Z0-9]+)(?:\?|$)", image_url)
                        if m:
                            ext = m.group(1).split("?")[0]
                            if len(ext) > 5:
                                ext = "png"
                        file_name = f"{result.get('id', 'noid')}-{choice.get('index', idx)}-{idx}.{ext}"
                        output_path = os.path.join(task_output_dir, file_name)
                        with open(output_path, "wb") as f:
                            f.write(image_data)
                        safe_print(f"任务 {task_name} (ID: {task_id}) 图片已保存到: {output_path}")
                        download_count += 1
                    except Exception as e:
                        safe_print(f"任务 {task_name} (ID: {task_id}) 无法下载图片数据: {image_url} - {e}")
        if download_count == 0:
            safe_print(f"任务 {task_name} (ID: {task_id}) 未成功下载任何图片。")
    else:
        safe_print(f"任务 {task_name} (ID: {task_id}) 返回值格式错误。")
    
    safe_print(f"任务 {task_name} (ID: {task_id}) 处理完成")
    return {"success": True, "task_id": task_id, "task_name": task_name, "task_idx": task_idx}

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
    print("=== GPT-4o 并发批量处理工具 ===")
    
    # 加载任务
    tasks = load_tasks()
    
    # 任务总数
    total_tasks = len(tasks)
    print(f"总共 {total_tasks} 个任务，将使用最多 {min(MAX_WORKERS, total_tasks)} 个并发线程")
    
    # 结果统计
    results = []
    success_count = 0
    failed_count = 0
    
    # 创建进度统计信息
    start_time = time.time()
    
    # 使用线程池执行任务
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, total_tasks)) as executor:
        # 提交所有任务
        future_to_task = {executor.submit(process_task, task, idx + 1, total_tasks): (idx + 1, task) 
                         for idx, task in enumerate(tasks)}
        
        # 处理完成的任务
        for future in as_completed(future_to_task):
            idx, task = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
                
                if result["success"]:
                    success_count += 1
                else:
                    failed_count += 1
                    
                # 计算进度和预估剩余时间
                completed = success_count + failed_count
                elapsed = time.time() - start_time
                
                if completed > 0:
                    avg_time_per_task = elapsed / completed
                    remaining_tasks = total_tasks - completed
                    estimated_remaining = avg_time_per_task * remaining_tasks
                    
                    # 格式化剩余时间
                    m, s = divmod(int(estimated_remaining), 60)
                    h, m = divmod(m, 60)
                    
                    # 输出进度信息
                    with print_lock:
                        print(f"\n进度: {completed}/{total_tasks} ({completed/total_tasks*100:.1f}%)")
                        print(f"已完成: {success_count} 成功, {failed_count} 失败")
                        print(f"平均每任务耗时: {avg_time_per_task:.1f} 秒")
                        print(f"预计剩余时间: {h:d}小时 {m:02d}分 {s:02d}秒")
                        
            except Exception as e:
                with print_lock:
                    print(f"任务 {idx} 发生异常: {e}")
                failed_count += 1
    
    # 计算总耗时
    total_time = time.time() - start_time
    m, s = divmod(int(total_time), 60)
    h, m = divmod(m, 60)
    
    # 输出结果统计
    print("\n=== 批量处理完成 ===")
    print(f"总任务数: {total_tasks}")
    print(f"成功任务: {success_count}")
    print(f"失败任务: {failed_count}")
    print(f"总耗时: {h:d}小时 {m:02d}分 {s:02d}秒")
    print(f"处理结果保存在: {OUTPUT_DIR}")

if __name__ == "__main__":
    main() 