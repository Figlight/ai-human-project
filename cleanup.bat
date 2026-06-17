@echo off
echo ========================================
echo 清理项目缓存文件
echo ========================================
echo.

echo [1/2] 清理 Python __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo ✓ Python 缓存已清理

echo.
echo [2/2] 清理日志文件（如果未被占用）...
if exist backend.log del /f /q backend.log 2>nul && echo ✓ backend.log 已删除 || echo ⚠ backend.log 被占用，跳过
if exist frontend.log del /f /q frontend.log 2>nul && echo ✓ frontend.log 已删除 || echo ⚠ frontend.log 被占用，跳过

echo.
echo ========================================
echo 清理完成！
echo ========================================
pause
