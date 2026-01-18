@echo off
REM Script para compilar o Sistema de Automacao MT5
echo ================================================
echo    COMPILADOR - Sistema de Automacao MT5
echo ================================================
echo.

REM Verificar se PyInstaller esta instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERRO] PyInstaller nao encontrado!
    echo Instalando PyInstaller...
    pip install pyinstaller
    echo.
)

echo [1/3] Limpando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "AutomacaoMT5.exe" del /q AutomacaoMT5.exe
echo.

echo [2/3] Compilando sistema (pode demorar alguns minutos)...
pyinstaller --clean --noconfirm build_exe.spec
echo.

if exist "dist\AutomacaoMT5.exe" (
    echo [3/3] Movendo executavel para pasta raiz...
    move "dist\AutomacaoMT5.exe" "AutomacaoMT5.exe"
    echo.
    echo ================================================
    echo    COMPILACAO CONCLUIDA COM SUCESSO!
    echo ================================================
    echo.
    echo Executavel criado: AutomacaoMT5.exe
    echo Tamanho: 
    dir AutomacaoMT5.exe | find "AutomacaoMT5.exe"
    echo.
    echo Voce pode executar AutomacaoMT5.exe diretamente
    echo.
    
    REM Limpar arquivos temporarios
    choice /c SN /m "Deseja limpar arquivos temporarios de build (S/N)"
    if errorlevel 2 goto fim
    if errorlevel 1 (
        echo Limpando...
        rmdir /s /q build
        rmdir /s /q dist
        del /q *.spec.bak 2>nul
        echo Limpeza concluida!
    )
) else (
    echo.
    echo ================================================
    echo    ERRO NA COMPILACAO!
    echo ================================================
    echo Verifique os erros acima
)

:fim
echo.
pause
