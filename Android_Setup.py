# ============================================================
# 安卓APK一键打包工具 / Android APK Build Tool
# 功能：清理缓存、打包Debug/Release APK、中英双语界面
# Features: Clean cache, Build Debug/Release APK, Bilingual UI
# ============================================================

import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import subprocess
import os
import shutil
import threading
import sys

# ===================== 配置区 / Configuration =====================
# 修改你本地SDK路径 / Modify to your local SDK paths
ANDROID_SDK_ROOT = r"C:\Users\Administrator\AppData\Local\Android\Sdk"
ANDROID_NDK_ROOT = r"C:\Users\Administrator\AppData\Local\Android\Sdk\ndk\28.1.13356709"
# APK 输出文件夹名称（相对于项目根目录）/ APK output folder name (relative to project root)
OUTPUT_FOLDER_NAME = "build/apks"
# ================================================================

# ===================== 多语言文本 / Multilingual Text =====================
# 中文与英文对照 / Chinese and English translations
LANG = {
    "zh": {
        "title": "安卓APK一键打包工具",
        "no_project": "未选择项目源码文件夹",
        "project_dir": "安卓项目根目录：",
        "select_folder": "选择文件夹",
        "clean": "1. 清理缓存",
        "build_debug": "2. 打包Debug安装包",
        "build_release": "3. 打包Release安装包",
        "stop": "终止编译",
        "progress": "编译进度：",
        "log_title": "编译控制台日志：",
        "lang_btn": "🌐 EN",
        "close_confirm": "确定要关闭打包工具吗？窗口将常驻，无需频繁重启",
        "close_title": "提示",
        "stopped": "已手动终止编译任务",
        "no_gradle": "错误：未选择有效安卓项目文件夹！",
        "exec_cmd": "执行命令：",
        "build_fail": "打包编译失败，请查看上方红色报错日志！",
        "no_apk": "未找到编译产出的APK文件",
        "build_success": "===== 打包成功 =====",
        "apk_output": "APK输出路径：",
        "build_done": "打包完成",
        "apk_generated": "APK已生成至：\n",
        "cleaning": "开始执行Clean清理缓存...",
        "clean_done": "缓存清理完成！",
        "building_debug": "开始编译打包Debug APK...",
        "building_release": "开始编译打包Release APK...",
        "warn_no_gradle": "警告：当前文件夹未找到gradlew.bat，不是合法Android项目！",
        "selected": "已选中项目路径：",
        "err_log": "【编译错误日志】",
        "exit_code": "编译失败，进程退出码：",
        "exec_exception": "执行命令异常：",
    },
    "en": {
        "title": "Android APK Build Tool",
        "no_project": "Project source code folder not selected",
        "project_dir": "Android Project Root:",
        "select_folder": "Browse",
        "clean": "1. Clean Cache",
        "build_debug": "2. Build Debug APK",
        "build_release": "3. Build Release APK",
        "stop": "Stop Build",
        "progress": "Build Progress:",
        "log_title": "Build Console Log:",
        "lang_btn": "🌐 中文",
        "close_confirm": "Are you sure to close the tool? The window stays resident.",
        "close_title": "Notice",
        "stopped": "Build task stopped manually",
        "no_gradle": "Error: No valid Android project folder selected!",
        "exec_cmd": "Command: ",
        "build_fail": "Build failed. Please check the error log above!",
        "no_apk": "APK file not found in build output",
        "build_success": "===== BUILD SUCCESS =====",
        "apk_output": "APK output path: ",
        "build_done": "Build Complete",
        "apk_generated": "APK generated at:\n",
        "cleaning": "Starting Clean task...",
        "clean_done": "Cache cleaned!",
        "building_debug": "Building Debug APK...",
        "building_release": "Building Release APK...",
        "warn_no_gradle": "Warning: gradlew.bat not found, not a valid Android project!",
        "selected": "Project path selected: ",
        "err_log": "[Build Error Log]",
        "exit_code": "Build failed, exit code: ",
        "exec_exception": "Command exception: ",
    }
}


class ApkBuildTool:
    """APK打包工具主类 / Main class of the APK build tool"""

    def __init__(self, root_window):
        # 主窗口引用 / Reference to the root window
        self.root = root_window
        # 当前语言（默认中文）/ Current language (default Chinese)
        self.lang = "zh"
        # 当前语言文本映射 / Current language text mapping
        self.t = LANG[self.lang]
        self.root.title(self.t["title"])
        self.root.geometry("900x650")
        # 拦截窗口关闭事件 / Intercept window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # 项目路径变量 / Project path variable
        self.project_path = tk.StringVar(value=self.t["no_project"])
        # 编译进程句柄 / Build process handle
        self.compile_process = None

        self._build_ui()

    def _build_ui(self):
        """构建用户界面 / Build the user interface"""
        # 清除旧控件 / Clear old widgets
        for w in self.root.winfo_children():
            w.destroy()

        # 1. 项目选择区域 / 1. Project selection area
        frame_select = tk.Frame(self.root, pady=10)
        frame_select.pack(fill="x", padx=10)
        tk.Label(frame_select, text=self.t["project_dir"]).pack(side="left")
        tk.Entry(frame_select, textvariable=self.project_path, width=60).pack(side="left", padx=5)
        tk.Button(frame_select, text=self.t["select_folder"], command=self.select_project_folder).pack(side="left", padx=5)
        # 语言切换按钮 / Language switch button
        tk.Button(frame_select, text=self.t["lang_btn"], command=self.switch_language, bg="#89b4fa", fg="white").pack(side="right", padx=5)

        # 2. 操作按钮区域 / 2. Action buttons area
        frame_btn = tk.Frame(self.root, pady=5)
        frame_btn.pack(fill="x", padx=10)
        self.btn_clean = tk.Button(frame_btn, text=self.t["clean"], command=self.start_clean_task)
        self.btn_clean.pack(side="left", padx=5)
        self.btn_build_debug = tk.Button(frame_btn, text=self.t["build_debug"], command=self.start_build_task)
        self.btn_build_debug.pack(side="left", padx=5)
        self.btn_build_release = tk.Button(frame_btn, text=self.t["build_release"], command=lambda: self.start_build_task(release=True))
        self.btn_build_release.pack(side="left", padx=5)
        self.btn_stop = tk.Button(frame_btn, text=self.t["stop"], command=self.kill_process, bg="#ff6666", state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        # 3. 进度条 / 3. Progress bar
        frame_progress = tk.Frame(self.root, pady=5)
        frame_progress.pack(fill="x", padx=10)
        tk.Label(frame_progress, text=self.t["progress"]).pack(side="left")
        self.progress_bar = ttk.Progressbar(frame_progress, length=700, mode="determinate")
        self.progress_bar.pack(side="left", padx=5)

        # 4. 日志输出框 / 4. Log output area
        frame_log = tk.Frame(self.root, pady=10)
        frame_log.pack(fill="both", expand=True, padx=10)
        tk.Label(frame_log, text=self.t["log_title"]).pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(frame_log, wrap="word")
        self.log_text.pack(fill="both", expand=True)
        # 日志样式标签 / Log style tags
        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")

    def switch_language(self):
        """切换界面语言 / Switch interface language"""
        # 记录切换前的占位文本 / Record the placeholder text before switching
        old_placeholder = LANG["zh"]["no_project"] if self.lang == "zh" else LANG["en"]["no_project"]
        self.lang = "en" if self.lang == "zh" else "zh"
        self.t = LANG[self.lang]
        self.root.title(self.t["title"])
        saved_path = self.project_path.get()
        # 如果当前是占位文本，切换为对应语言的占位文本
        # If current text is a placeholder, replace with the new language placeholder
        if saved_path == old_placeholder:
            saved_path = self.t["no_project"]
        self._build_ui()
        self.project_path.set(saved_path)

    def log_print(self, msg, level="info"):
        """打印日志到文本框 / Print log to text box"""
        self.log_text.insert(tk.END, msg + "\n", level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def select_project_folder(self):
        """选择项目文件夹 / Select project folder"""
        folder = filedialog.askdirectory()
        if folder:
            self.project_path.set(folder)
            self.log_print(f"{self.t['selected']}{folder}")
            # 检查是否存在gradlew.bat / Check if gradlew.bat exists
            gradlew_path = os.path.join(folder, "gradlew.bat")
            if not os.path.exists(gradlew_path):
                self.log_print(self.t["warn_no_gradle"], "error")

    def on_close(self):
        """窗口关闭确认 / Window close confirmation"""
        if messagebox.askyesno(self.t["close_title"], self.t["close_confirm"]):
            self.root.destroy()

    def kill_process(self):
        """终止编译进程 / Kill the build process"""
        if self.compile_process and self.compile_process.poll() is None:
            self.compile_process.terminate()
            self.log_print(self.t["stopped"], "error")
            self.progress_bar["value"] = 0
            self._reset_buttons()

    def _reset_buttons(self):
        """重置按钮状态 / Reset button states"""
        self.btn_stop.config(state="disabled")
        self.btn_clean.config(state="normal")
        self.btn_build_debug.config(state="normal")
        self.btn_build_release.config(state="normal")

    def run_gradle_cmd(self, cmd_list, progress_start, progress_end):
        """
        执行Gradle命令并实时输出日志
        Execute a Gradle command and stream output in real time

        参数 / Parameters:
            cmd_list: 命令参数列表 / Command arguments list
            progress_start: 进度起始值 / Progress start value
            progress_end: 进度结束值 / Progress end value
        返回 / Returns: True=成功(success), False=失败(failure)
        """
        project_dir = self.project_path.get()
        # 检查gradlew.bat是否存在 / Check if gradlew.bat exists
        if not os.path.exists(os.path.join(project_dir, "gradlew.bat")):
            self.log_print(self.t["no_gradle"], "error")
            return False

        # 继承系统环境变量并设置SDK路径 / Inherit system env and set SDK paths
        env = os.environ.copy()
        env["ANDROID_SDK_ROOT"] = ANDROID_SDK_ROOT
        env["ANDROID_NDK_ROOT"] = ANDROID_NDK_ROOT
        env["JAVA_TOOL_OPTIONS"] = "-Dfile.encoding=UTF-8"

        self.log_print("=" * 60)
        self.log_print(f"{self.t['exec_cmd']}{' '.join(cmd_list)}")
        self.progress_bar["value"] = progress_start
        try:
            # 启动子进程，捕获stdout和stderr / Start subprocess, capture stdout and stderr
            self.compile_process = subprocess.Popen(
                cmd_list, cwd=project_dir, env=env, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8"
            )
            # 逐行读取stdout / Read stdout line by line
            while True:
                line = self.compile_process.stdout.readline()
                if not line and self.compile_process.poll() is not None:
                    break
                if line:
                    # 含错误关键词的行标红 / Highlight lines with error keywords in red
                    if any(key in line.lower() for key in ["error", "fail", "exception"]):
                        self.log_print(line.strip(), "error")
                    else:
                        self.log_print(line.strip(), "info")
                    self.progress_bar["value"] += 0.08
                    if self.progress_bar["value"] > progress_end:
                        self.progress_bar["value"] = progress_end
            # 读取stderr错误日志 / Read stderr error log
            err_log = self.compile_process.stderr.read()
            if err_log:
                self.log_print(f"{self.t['err_log']}\n{err_log}", "error")
            exit_code = self.compile_process.wait()
            self.progress_bar["value"] = progress_end
            self.compile_process = None
            if exit_code == 0:
                return True
            else:
                self.log_print(f"{self.t['exit_code']}{exit_code}", "error")
                return False
        except Exception as e:
            self.log_print(f"{self.t['exec_exception']}{str(e)}", "error")
            self.compile_process = None
            return False

    def start_clean_task(self):
        """启动清理缓存任务 / Start cache clean task"""
        def task():
            self.btn_clean.config(state="disabled")
            self.btn_build_debug.config(state="disabled")
            self.btn_build_release.config(state="disabled")
            self.btn_stop.config(state="normal")
            self.log_print(self.t["cleaning"])
            gradlew = os.path.join(self.project_path.get(), "gradlew.bat")
            success = self.run_gradle_cmd([gradlew, "clean"], 0, 30)
            if success:
                self.log_print(self.t["clean_done"], "success")
            self._reset_buttons()
        threading.Thread(target=task, daemon=True).start()

    def start_build_task(self, release=False):
        """
        启动APK打包任务 / Start APK build task

        参数 / Parameters:
            release: True=Release包(Release build), False=Debug包(Debug build)
        """
        def task():
            self.btn_clean.config(state="disabled")
            self.btn_build_debug.config(state="disabled")
            self.btn_build_release.config(state="disabled")
            self.btn_stop.config(state="normal")
            project_dir = self.project_path.get()
            gradlew = os.path.join(project_dir, "gradlew.bat")

            # 构建类型：release 或 debug / Build type: release or debug
            build_type = "release" if release else "debug"
            if release:
                self.log_print(self.t["building_release"])
            else:
                self.log_print(self.t["building_debug"])

            # 执行打包命令 / Execute build command
            build_success = self.run_gradle_cmd([gradlew, f"app:assemble{build_type.capitalize()}"], 30, 90)
            if not build_success:
                self.log_print(self.t["build_fail"], "error")
                self.progress_bar["value"] = 0
                self._reset_buttons()
                return

            # APK 源输出目录 / APK source output directory
            source_apk_dir = os.path.join(project_dir, "app", "build", "outputs", "apk", build_type)
            # APK 目标存放目录 / APK target directory
            target_dir = os.path.join(project_dir, OUTPUT_FOLDER_NAME)
            os.makedirs(target_dir, exist_ok=True)

            # 查找生成的APK文件 / Find the generated APK file
            apk_file = None
            for file_name in os.listdir(source_apk_dir):
                if file_name.endswith(f"-{build_type}.apk"):
                    apk_file = os.path.join(source_apk_dir, file_name)
                    break
            if not apk_file or not os.path.exists(apk_file):
                self.log_print(self.t["no_apk"], "error")
                self.progress_bar["value"] = 0
                self._reset_buttons()
                return

            # 复制APK到目标目录 / Copy APK to target directory
            target_apk_path = os.path.join(target_dir, os.path.basename(apk_file))
            shutil.copy2(apk_file, target_apk_path)
            self.progress_bar["value"] = 100
            self.log_print(f"{self.t['build_success']}\n{self.t['apk_output']}{target_apk_path}", "success")
            messagebox.showinfo(self.t["build_done"], f"{self.t['apk_generated']}{target_apk_path}")
            self._reset_buttons()
        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    # 程序入口 / Program entry point
    main_root = tk.Tk()
    tool = ApkBuildTool(main_root)
    main_root.mainloop()