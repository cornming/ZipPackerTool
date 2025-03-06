import os
import shutil
import zipfile
import json
import datetime
from tkinter import Tk, filedialog, messagebox
from tkinter import simpledialog  # 新增引入 simpledialog 模組

# 儲存打包紀錄的檔案路徑
RECORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zip_packer_records.json")

def select_source_path():
    root = Tk()
    root.withdraw()
    source_path = filedialog.askdirectory(title="選擇要打包zip的來源路徑")
    return source_path

def select_save_path():
    root = Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("Zip files", "*.zip")], title="選擇壓縮完之後要儲存的路徑位置")
    return save_path

def exclude_files(file_list, exclude_patterns):
    return [f for f in file_list if not any(pattern in f for pattern in exclude_patterns)]

def create_zip(source_path, save_path, exclude_patterns):
    with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            files = exclude_files(files, exclude_patterns)
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=source_path)
                zipf.write(file_path, arcname)

def open_file_explorer(path):
    os.startfile(path)

def load_records():
    """載入打包紀錄"""
    if os.path.exists(RECORD_FILE):
        try:
            with open(RECORD_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"載入紀錄時發生錯誤: {e}")
    return {}

def save_record(source_path, save_path, exclude_patterns):
    """儲存打包紀錄"""
    records = load_records()
    
    # 建立新的紀錄項目
    records[source_path] = {
        "save_path": save_path,
        "exclude_patterns": exclude_patterns,
        "last_used": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        with open(RECORD_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"儲存紀錄時發生錯誤: {e}")

def get_previous_record(source_path):
    """取得特定來源路徑的先前打包紀錄"""
    records = load_records()
    return records.get(source_path)

def main():
    source_path = select_source_path()
    if not source_path:
        messagebox.showerror("錯誤", "未選擇來源路徑")
        return

    # 檢查是否有此路徑的打包紀錄
    previous_record = get_previous_record(source_path)
    default_save_path = ""
    default_exclude_patterns = []
    
    if previous_record:
        use_previous = messagebox.askyesno(
            "發現先前的打包設定",
            f"此路徑已打包過，是否要套用先前的設定?\n\n"
            f"上次打包路徑: {previous_record['save_path']}\n"
            f"排除條件: {', '.join(previous_record['exclude_patterns'])}\n"
            f"上次打包時間: {previous_record['last_used']}"
        )
        
        if use_previous:
            save_path = previous_record["save_path"]
            exclude_patterns = previous_record["exclude_patterns"]
            
            # 確認儲存路徑的資料夾是否存在
            save_dir = os.path.dirname(save_path)
            if not os.path.exists(save_dir):
                messagebox.showwarning("警告", "先前的儲存路徑資料夾不存在，請重新選擇儲存位置")
                save_path = select_save_path()
                if not save_path:
                    messagebox.showerror("錯誤", "未選擇儲存路徑")
                    return
            else:
                # 如果檔案已存在，詢問是否覆蓋
                if os.path.exists(save_path):
                    overwrite = messagebox.askyesno("覆蓋確認", f"檔案 {os.path.basename(save_path)} 已存在，是否覆蓋?")
                    if not overwrite:
                        save_path = select_save_path()
                        if not save_path:
                            messagebox.showerror("錯誤", "未選擇儲存路徑")
                            return
            
            create_zip(source_path, save_path, exclude_patterns)
            open_file_explorer(os.path.dirname(save_path))
            messagebox.showinfo("完成", "打包完成")
            
            # 更新使用時間
            save_record(source_path, save_path, exclude_patterns)
            return
        else:
            # 使用先前的設定作為預設值，但允許修改
            default_save_path = previous_record["save_path"]
            default_exclude_patterns = previous_record["exclude_patterns"]
    
    # 選擇儲存路徑
    initialdir = os.path.dirname(default_save_path) if default_save_path else None
    initialfile = os.path.basename(default_save_path) if default_save_path else None
    
    root = Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(
        defaultextension=".zip",
        filetypes=[("Zip files", "*.zip")],
        title="選擇壓縮完之後要儲存的路徑位置",
        initialdir=initialdir,
        initialfile=initialfile
    )
    
    if not save_path:
        messagebox.showerror("錯誤", "未選擇儲存路徑")
        return

    # 請求排除條件
    root = Tk()
    root.withdraw()
    default_exclude = ",".join(default_exclude_patterns) if default_exclude_patterns else ""
    exclude_input = simpledialog.askstring(
        "排除條件",
        "輸入要排除的檔案或副檔名，以逗號分隔\n若不輸入將預設排除 zip、json、config",
        initialvalue=default_exclude
    )
    
    # 若使用者沒有輸入，則預設排除 zip、json、config 副檔名
    if exclude_input:
        exclude_patterns = exclude_input.split(',')
    else:
        exclude_patterns = ['.zip', '.json', '.config']

    create_zip(source_path, save_path, exclude_patterns)
    open_file_explorer(os.path.dirname(save_path))
    messagebox.showinfo("完成", "打包完成")
    
    # 儲存這次的打包紀錄
    save_record(source_path, save_path, exclude_patterns)

if __name__ == "__main__":
    main()