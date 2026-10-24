# Android APK 一键打包工具
Android APK Build Tool






> 基于 tkinter 开发的 Windows 图形化 APK 打包脚本，**中英双语界面**。
> 封装 Gradle 编译命令，一键清理缓存、编译 Debug / Release 安装包，实时打印编译日志，编译完成自动归集APK。

## ✨ 功能 Features
- ✅ 图形化选择 Android Gradle 项目根目录，自动校验项目是否包含 `gradlew.bat`
- ✅ 一键 Clean 清理项目构建缓存
- ✅ 一键打包 Debug APK
- ✅ 一键打包 Release APK
- ✅ 实时滚动编译日志：报错行红色高亮、成功信息绿色高亮
- ✅ 可视化进度条展示编译进度
- ✅ 支持随时终止正在运行的编译进程
- ✅ 中文 / English 双语界面一键切换
- ✅ 打包成功后自动复制APK到项目内指定目录统一存放
- ✅ 编译任务独立子线程运行，GUI界面不会卡死无响应

## 📋 前置环境依赖 Requirements
> 全部使用 Python 标准库，**无需额外 pip 安装第三方包**
1. Python 3.8 及以上版本（Windows安装包默认自带tkinter）
2. 本地提前安装好 **Android SDK + NDK**（Android Studio配套下载）
3. 标准 Gradle Android 项目，项目根目录必须存在 `gradlew.bat`
4. 仅适配 Windows 系统（脚本调用 `gradlew.bat`，Linux/macOS需要自行修改适配）

## ⚙ 【重要】手动配置 SDK & NDK 路径
> ⚠ **所有拉取本仓库的开发者，必须手动修改这部分配置，脚本不会自动探测SDK路径！**
打开 `apk_build_tool.py`，找到文件最上方的配置区：
```python
# ========== 【必须手动修改为你本机真实路径】 ==========
ANDROID_SDK_ROOT = r"C:\Users\Administrator\AppData\Local\Android\Sdk"
ANDROID_NDK_ROOT = r"C:\Users\Administrator\AppData\Local\Android\Sdk\ndk\28.1.13356709"
# APK输出的相对目录，可按需修改
OUTPUT_FOLDER_NAME = "build/apks"
# =====================================================
