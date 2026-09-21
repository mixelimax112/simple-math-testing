@echo off
setlocal

:: ====== НАСТРОЙКА БАЗЫ ДАННЫХ И СБРОС ЛИМИТОВ ======
echo Configuring OmniRoute environment...
set "STORAGE_ENCRYPTION_KEY=mixel_secret_omniroute_key_2026"

call omniroute resilience reset --provider kiro --all-cooldowns --yes

:: ====== ЗАПУСК OMNIROUTE ======
echo Starting OmniRoute...
start "OmniRoute" cmd /k omniroute

:wait_loop
curl -s http://localhost:20128/v1 >nul 2>&1
if errorlevel 1 (
    echo Waiting for OmniRoute...
    timeout /t 1 >nul
    goto wait_loop
)

:: ====== НАСТРОЙКА ОКРУЖЕНИЯ CLAUDE CODE ======
set "ANTHROPIC_AUTH_TOKEN=sk-1ffc667938d1b8a7-d9f846-c21fecce"
set "ANTHROPIC_BASE_URL=http://localhost:20128/v1"
set "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1"

:: Принудительно указываем модель Kiro
set "ANTHROPIC_MODEL=kr/claude-sonnet-4.5"

echo Starting Claude Code via OmniRoute...
call npx @anthropic-ai/claude-code --model kr/claude-sonnet-4.5

echo.
echo [Система]: Процесс Claude Code завершился.
pause

endlocal