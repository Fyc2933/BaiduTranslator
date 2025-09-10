import customtkinter as ctk
import requests
import json
import hashlib
import random
import os
import sys
from tkinter import messagebox
from datetime import datetime

class BaiduTranslatorApp:
    def __init__(self):
        # 初始化主窗口
        self.root = ctk.CTk()
        self.root.title("百度翻译工具")
        self.root.geometry("800x600")
        
        # 设置图标 - 处理打包后的路径问题
        self.set_icon()
        
        # 设置主题
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # API配置
        self.app_id = ""
        self.secret_key = ""
        self.history_file = "translation_history.json"
        
        self.setup_ui()
        self.load_config()
        self.load_history()
    
    def set_icon(self):
        """设置应用程序图标，处理打包后的路径问题"""
        try:
            # 如果是打包后的可执行文件
            if getattr(sys, 'frozen', False):
                # 打包后的可执行文件路径
                base_path = sys._MEIPASS
            else:
                # 开发环境路径
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, "icon.ico")
            
            # 检查图标文件是否存在
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"图标文件未找到: {icon_path}")
                
        except Exception as e:
            print(f"设置图标时出错: {e}")

    def setup_ui(self):
        # 创建主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # API配置区域
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(config_frame, text="API配置", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # App ID输入
        app_id_frame = ctk.CTkFrame(config_frame)
        app_id_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(app_id_frame, text="APP ID:").pack(side="left")
        self.app_id_entry = ctk.CTkEntry(app_id_frame, placeholder_text="请输入您的APP ID", width=300)
        self.app_id_entry.pack(side="left", padx=10)
        
        # Secret Key输入
        secret_frame = ctk.CTkFrame(config_frame)
        secret_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(secret_frame, text="密钥:").pack(side="left")
        self.secret_entry = ctk.CTkEntry(secret_frame, placeholder_text="请输入您的Secret Key", width=300, show="*")
        self.secret_entry.pack(side="left", padx=10)
        
        # 保存配置按钮
        ctk.CTkButton(config_frame, text="保存配置", command=self.save_config).pack(pady=10)
        
        # 翻译区域
        translate_frame = ctk.CTkFrame(main_frame)
        translate_frame.pack(fill="both", expand=True)
        
        # 输入区域
        input_frame = ctk.CTkFrame(translate_frame)
        input_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(input_frame, text="输入文本:").pack(anchor="w")
        self.input_text = ctk.CTkTextbox(input_frame, height=100)
        self.input_text.pack(fill="x", pady=5)
        
        # 语言选择
        lang_frame = ctk.CTkFrame(translate_frame)
        lang_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(lang_frame, text="源语言:").pack(side="left")
        self.from_lang = ctk.CTkComboBox(lang_frame, values=["auto", "zh", "en", "jp", "kor", "fra", "spa", "th", "ara", "ru", "pt", "de", "it", "el", "nl", "pl", "bul", "est", "dan", "fin", "cs", "rom", "slo", "swe", "hu", "vie", "yue", "wyw", "zh-TW"], width=100)
        self.from_lang.set("auto")
        self.from_lang.pack(side="left", padx=5)
        
        ctk.CTkLabel(lang_frame, text="目标语言:").pack(side="left", padx=(20, 5))
        self.to_lang = ctk.CTkComboBox(lang_frame, values=["zh", "en", "jp", "kor", "fra", "spa", "th", "ara", "ru", "pt", "de", "it", "el", "nl", "pl", "bul", "est", "dan", "fin", "cs", "rom", "slo", "swe", "hu", "vie", "yue", "wyw", "zh-TW"], width=100)
        self.to_lang.set("zh")
        self.to_lang.pack(side="left", padx=5)
        
        # 翻译按钮
        ctk.CTkButton(lang_frame, text="翻译", command=self.translate_text).pack(side="right")
        
        # 输出区域
        output_frame = ctk.CTkFrame(translate_frame)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        output_header = ctk.CTkFrame(output_frame)
        output_header.pack(fill="x")
        ctk.CTkLabel(output_header, text="翻译结果:").pack(side="left")
        
        # 复制按钮
        ctk.CTkButton(output_header, text="复制", command=self.copy_result, width=60).pack(side="right", padx=5)
        
        self.output_text = ctk.CTkTextbox(output_frame, height=100, state="disabled")
        self.output_text.pack(fill="both", expand=True, pady=5)
    
    def save_config(self):
        self.app_id = self.app_id_entry.get().strip()
        self.secret_key = self.secret_entry.get().strip()
        
        if not self.app_id or not self.secret_key:
            messagebox.showwarning("警告", "请填写完整的API配置信息")
            return
        
        # 保存到配置文件
        config = {
            "app_id": self.app_id,
            "secret_key": self.secret_key
        }
        try:
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "API配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.app_id = config.get("app_id", "")
                    self.secret_key = config.get("secret_key", "")
                    
                    # 更新界面显示
                    if self.app_id:
                        self.app_id_entry.delete(0, "end")
                        self.app_id_entry.insert(0, self.app_id)
                    if self.secret_key:
                        self.secret_entry.delete(0, "end")
                        self.secret_entry.insert(0, self.secret_key)
                        
            except Exception as e:
                print(f"加载配置失败: {e}")
    
    def generate_sign(self, query, salt):
        """生成签名"""
        sign_str = self.app_id + query + salt + self.secret_key
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def translate_text(self):
        if not self.app_id or not self.secret_key:
            messagebox.showerror("错误", "请先配置API信息")
            return
        
        query = self.input_text.get("1.0", "end-1c").strip()
        if not query:
            messagebox.showwarning("警告", "请输入要翻译的文本")
            return
        
        try:
            # 准备请求参数
            salt = str(random.randint(32768, 65536))
            sign = self.generate_sign(query, salt)
            
            # 构建请求URL
            url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
            params = {
                "q": query,
                "from": self.from_lang.get(),
                "to": self.to_lang.get(),
                "appid": self.app_id,
                "salt": salt,
                "sign": sign
            }
            
            # 发送请求
            response = requests.get(url, params=params)
            result = response.json()
            
            # 处理响应
            if "trans_result" in result:
                translated_text = "\n".join([item["dst"] for item in result["trans_result"]])
                self.output_text.configure(state="normal")
                self.output_text.delete("1.0", "end")
                self.output_text.insert("1.0", translated_text)
                self.output_text.configure(state="disabled")
                
                # 保存到历史记录
                self.save_to_history(query, self.from_lang.get(), self.to_lang.get(), translated_text)
            else:
                error_msg = result.get("error_msg", "翻译失败")
                messagebox.showerror("错误", f"翻译失败: {error_msg}")
                
        except Exception as e:
            messagebox.showerror("错误", f"翻译过程中发生错误: {str(e)}")
    
    def copy_result(self):
        """复制翻译结果到剪贴板"""
        result = self.output_text.get("1.0", "end-1c")
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            messagebox.showinfo("成功", "翻译结果已复制到剪贴板")
    
    def save_to_history(self, query, from_lang, to_lang, result):
        """保存翻译记录到历史文件"""
        history = self.load_history_data()
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "from_lang": from_lang,
            "to_lang": to_lang,
            "result": result
        }
        
        history.append(history_entry)
        # 只保留最近50条记录
        history = history[-50:]
        
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def load_history_data(self):
        """加载历史记录数据"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载历史记录失败: {e}")
        return []
    
    def load_history(self):
        """加载历史记录（预留接口）"""
        pass
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BaiduTranslatorApp()
    app.run()