@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "STREAMLIT_HOME=%~dp0"

echo ==========================================
echo    TravelFace - 个性化旅游智能体
echo ==========================================
echo.

:: ---- 1. 找 Python ----
set "PYTHON="
for %%p in (
    "%~dp0venv\Scripts\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
) do (
    if exist %%p (
        if not defined PYTHON set "PYTHON=%%~p"
    )
)
:: 最后尝试 PATH 里的 python
if not defined PYTHON (
    where python >nul 2>&1 && set "PYTHON=python"
)

if not defined PYTHON (
    echo [错误] 找不到 Python！
    echo        请安装 Python 3.11+ : https://www.python.org/downloads/
    echo        安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)
echo Python: %PYTHON%

:: ---- 2. 虚拟环境 ----
if not exist "venv\Scripts\python.exe" (
    echo [1/4] 创建虚拟环境...
    "%PYTHON%" -m venv venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
    echo [2/4] 安装依赖（首次约 1-3 分钟）...
    venv\Scripts\python.exe -m pip install --upgrade pip -q 2>nul
    venv\Scripts\python.exe -m pip install -r requirements.txt -q 2>nul
    if errorlevel 1 (
        echo [警告] 部分依赖安装失败
        echo         重试中...
        venv\Scripts\python.exe -m pip install -r requirements.txt
        if errorlevel 1 (
            echo [错误] 依赖安装失败，请检查网络
            pause
            exit /b 1
        )
    )
    echo [2/4] 依赖安装完成
) else (
    echo [1/4] 虚拟环境已就绪
    echo [2/4] 依赖已安装
)

:: ---- 3. 模型 ----
if not exist "assets\blaze_face_short_range.tflite" (
    echo [3/4] 下载人脸检测模型...
    venv\Scripts\python.exe -c "import requests; r=requests.get('https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite',timeout=60); open('assets/blaze_face_short_range.tflite','wb').write(r.content); print('ok')" 2>nul
    if errorlevel 1 (
        echo [警告] 模型下载失败，首次运行会较慢
    )
) else (
    echo [3/4] 模型已就绪
)

:: ---- 4. 清理旧端口 ----
echo [4/4] 启动服务...
echo.
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501.*LISTENING" 2^>nul') do (
    echo 关闭旧进程 PID=%%a ...
    taskkill /F /PID %%a 2>nul
    timeout /t 1 /nobreak >nul
)

echo.
echo ==========================================
echo   浏览器打开 http://localhost:8501
echo   按 Ctrl+C 停止
echo ==========================================
echo.

:: 启动后自动打开浏览器
start "" http://localhost:8501

venv\Scripts\python.exe -m streamlit run app.py --server.port 8501 --server.headless true 2>&1

if errorlevel 1 (
    echo.
    echo [错误] 启动失败！上面的错误信息已显示原因
)

pause
