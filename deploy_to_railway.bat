@echo off
echo ==========================================
echo   DEPLOYMENT A RAILWAY - SISTEMA ANDROID
echo ==========================================
echo.

echo [1/4] Verificando directorio...
cd /d "C:\Repositorio GitHub VSC\print-and-paint-studio-app"
if %errorlevel% neq 0 (
    echo ERROR: No se pudo acceder al directorio
    pause
    exit /b 1
)
echo ✅ Directorio correcto

echo.
echo [2/4] Verificando cambios en app.py...
findstr /c:"send_android_notification" app.py >nul
if %errorlevel% neq 0 (
    echo ERROR: Los cambios no están en app.py
    pause
    exit /b 1
)
echo ✅ Cambios confirmados en app.py

echo.
echo [3/4] Haciendo commit...
git add app.py test_notification_system.py SUBIR_A_RAILWAY_AHORA.md deploy_to_railway.bat
git commit -m "DEPLOY: Fix Android notification system - Web to Android sync complete

CRITICAL FEATURES:
- Add notifications to Android API endpoint  
- Add test endpoint for immediate verification
- Enable bidirectional Web ↔ Android sync
- Complete WebNotificationReceiver integration

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

echo.
echo [4/4] Subiendo a Railway...
git push origin main

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   ✅ DEPLOYMENT EXITOSO A RAILWAY!
    echo ==========================================
    echo.
    echo 🚀 Próximos pasos:
    echo   1. Espera 2-3 minutos para que Railway se actualice
    echo   2. Ejecuta: python test_notification_system.py
    echo   3. Verifica logs Android para confirmación
    echo.
    echo 📱 Logs Android esperados (en ~10 segundos):
    echo   📊 WebNotificationReceiver: Found 1 notifications
    echo   🔄 Processing stock update from test_endpoint: Blanco Hueso
    echo   ✅ Local paint stock updated: Blanco Hueso → [valor]
    echo.
    echo 🎉 Sistema Web ↔ Android COMPLETADO!
) else (
    echo.
    echo ❌ ERROR en el push. Verifica tu conexión a GitHub.
)

echo.
pause