"""
辅助脚本: 用于创建和管理GPT-4o批处理任务
"""

import os
import json
import shutil
from datetime import datetime

# 目录配置
INPUT_DIR = os.path.join(os.getcwd(), "input")
TASKS_FILE = os.path.join(INPUT_DIR, "tasks.json")
TASKS_EXAMPLE = os.path.join(INPUT_DIR, "tasks.json.example")
IMAGES_DIR = os.path.join(INPUT_DIR, "images")

# 确保目录存在
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')

def list_images():
    """列出images目录中的所有图片"""
    if not os.path.exists(IMAGES_DIR):
        return []
    
    images = []
    for file in os.listdir(IMAGES_DIR):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
            images.append(file)
    return images

def load_tasks():
    """加载当前任务列表"""
    if not os.path.exists(TASKS_FILE):
        return []
    
    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载任务文件失败: {e}")
        return []

def save_tasks(tasks):
    """保存任务列表"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(tasks)} 个任务到 {TASKS_FILE}")

def show_tasks(tasks):
    """显示任务列表"""
    if not tasks:
        print("当前没有任务。")
        return
    
    print("\n当前任务列表:")
    print("=" * 60)
    for i, task in enumerate(tasks, 1):
        name = task.get("name", "未命名任务")
        images = task.get("images", [])
        model = task.get("model", "默认模型")
        prompt_preview = task.get("prompt", "")[:40] + "..." if len(task.get("prompt", "")) > 40 else task.get("prompt", "")
        
        print(f"{i}. {name} [{model}] - 图片数量: {len(images)}")
        print(f"   提示词: {prompt_preview}")
    print("=" * 60)
    
def create_tasks():
    """批量创建相同提示词任务"""
    print("\n批量创建任务")
    print("=" * 60)
    
    name = input("任务名称前缀: ")
    prompt = input("提示词: ")
    model = input("模型 (默认为gpt-4o-image-vip): ") or "gpt-4o-image-vip"
    
    # 获取所有可用图片
    available_images = list_images()
    if not available_images:
        print("\n没有可用的图片。请将图片放在 input/images/ 目录下。")
        return
    
    print(f"\n找到 {len(available_images)} 张图片，将为每张图片创建一个任务...")
    
    tasks = load_tasks()
    for i, image in enumerate(available_images, 1):
        task = {
            "name": f"{name}_{i}",
            "prompt": prompt,
            "images": [image],
            "model": model
        }
        tasks.append(task)
    
    save_tasks(tasks)
    print(f"已批量创建 {len(available_images)} 个任务")

def create_task():
    """创建新任务"""
    print("\n创建新任务")
    print("=" * 60)
    
    name = input("任务名称: ")
    prompt = input("提示词: ")
    model = input("模型 (默认为gpt-4o-image-vip): ") or "gpt-4o-image-vip"
    
    # 显示可用的图片
    available_images = list_images()
    if available_images:
        print("\n可用图片:")
        for i, img in enumerate(available_images, 1):
            print(f"{i}. {img}")
        
        selected = input("\n选择图片编号 (多个用逗号分隔，留空表示不使用图片): ")
        if selected.strip():
            try:
                indices = [int(idx.strip()) - 1 for idx in selected.split(",")]
                images = [available_images[i] for i in indices if 0 <= i < len(available_images)]
            except:
                print("无效的选择，未添加图片。")
                images = []
        else:
            images = []
    else:
        print("\n没有可用的图片。请将图片放在 input/images/ 目录下。")
        images = []
    
    task = {
        "name": name,
        "prompt": prompt,
        "images": images,
        "model": model
    }
    
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f"已添加任务: {name}")

def edit_task(tasks):
    """编辑现有任务"""
    show_tasks(tasks)
    if not tasks:
        return
    
    try:
        idx = int(input("\n选择要编辑的任务编号: ")) - 1
        if idx < 0 or idx >= len(tasks):
            print("无效的选择！")
            return
        
        task = tasks[idx]
        print(f"\n编辑任务 {task.get('name', '未命名任务')}")
        print("=" * 60)
        
        name = input(f"任务名称 [{task.get('name', '')}]: ") or task.get('name', '')
        prompt = input(f"提示词 [{task.get('prompt', '')}]: ") or task.get('prompt', '')
        model = input(f"模型 [{task.get('model', 'gpt-4o-image-vip')}]: ") or task.get('model', 'gpt-4o-image-vip')
        
        # 显示当前图片
        current_images = task.get("images", [])
        if current_images:
            print("\n当前图片:")
            for i, img in enumerate(current_images, 1):
                print(f"{i}. {img}")
        
        # 显示可用的图片
        available_images = list_images()
        if available_images:
            print("\n可用图片:")
            for i, img in enumerate(available_images, 1):
                print(f"{i}. {img}")
            
            selected = input("\n重新选择图片编号 (多个用逗号分隔，留空表示保持原样): ")
            if selected.strip():
                try:
                    indices = [int(idx.strip()) - 1 for idx in selected.split(",")]
                    images = [available_images[i] for i in indices if 0 <= i < len(available_images)]
                except:
                    print("无效的选择，保持原有图片。")
                    images = current_images
            else:
                images = current_images
        else:
            print("\n没有可用的图片。请将图片放在 input/images/ 目录下。")
            images = current_images
        
        tasks[idx] = {
            "name": name,
            "prompt": prompt,
            "images": images,
            "model": model
        }
        
        save_tasks(tasks)
        print(f"已更新任务: {name}")
    except Exception as e:
        print(f"编辑任务时出错: {e}")

def delete_task(tasks):
    """删除任务"""
    show_tasks(tasks)
    if not tasks:
        return
    
    try:
        idx = int(input("\n选择要删除的任务编号: ")) - 1
        if idx < 0 or idx >= len(tasks):
            print("无效的选择！")
            return
        
        task = tasks[idx]
        confirm = input(f"确认删除任务 '{task.get('name', '未命名任务')}' [y/N]: ")
        if confirm.lower() == 'y':
            tasks.pop(idx)
            save_tasks(tasks)
            print("任务已删除。")
        else:
            print("已取消删除。")
    except Exception as e:
        print(f"删除任务时出错: {e}")

def import_example():
    """导入示例任务"""
    if not os.path.exists(TASKS_EXAMPLE):
        print(f"示例文件不存在: {TASKS_EXAMPLE}")
        return
    
    try:
        with open(TASKS_EXAMPLE, 'r', encoding='utf-8') as f:
            example_tasks = json.load(f)
        
        # 加载现有任务
        current_tasks = load_tasks()
        
        # 添加示例任务
        current_tasks.extend(example_tasks)
        
        # 保存任务
        save_tasks(current_tasks)
        print(f"已导入 {len(example_tasks)} 个示例任务。")
    except Exception as e:
        print(f"导入示例任务时出错: {e}")

def backup_tasks():
    """备份当前任务文件"""
    if not os.path.exists(TASKS_FILE):
        print("没有任务文件可以备份。")
        return
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = os.path.join(INPUT_DIR, f"tasks_backup_{timestamp}.json")
        shutil.copy2(TASKS_FILE, backup_file)
        print(f"已备份任务文件到: {backup_file}")
    except Exception as e:
        print(f"备份任务文件时出错: {e}")

def main_menu():
    """主菜单"""
    while True:
        clear_screen()
        tasks = load_tasks()
        
        print("\n=== GPT-4o 批处理任务管理器 ===\n")
        print(f"当前有 {len(tasks)} 个任务")
        print(f"图片目录: {IMAGES_DIR}")
        print(f"任务文件: {TASKS_FILE}\n")
        
        print("1. 查看所有任务")
        print("2. 创建新任务")
        print("3. 编辑任务")
        print("4. 删除任务")
        print("5. 导入示例任务")
        print("6. 备份任务文件")
        print("7. 批量创建任务")
        print("0. 退出")
        
        choice = input("\n请选择 [0-6]: ")
        
        if choice == '1':
            show_tasks(tasks)
            input("\n按回车键继续...")
        elif choice == '2':
            create_task()
            input("\n按回车键继续...")
        elif choice == '3':
            edit_task(tasks)
            input("\n按回车键继续...")
        elif choice == '4':
            delete_task(tasks)
            input("\n按回车键继续...")
        elif choice == '5':
            import_example()
            input("\n按回车键继续...")
        elif choice == '6':
            backup_tasks()
            input("\n按回车键继续...")
        elif choice == '7':
            create_tasks()
            input("\n按回车键继续...")
        elif choice == '0':
            print("再见！")
            break
        else:
            print("无效的选择，请重试。")
            input("\n按回车键继续...")

if __name__ == "__main__":
    main_menu() 