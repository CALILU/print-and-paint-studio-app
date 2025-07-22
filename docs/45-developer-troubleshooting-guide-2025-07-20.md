# 🔧 GUÍA DE TROUBLESHOOTING PARA DESARROLLADORES

**Fecha**: 2025-07-20  
**Versión**: Sistema Híbrido v2.3  
**Audiencia**: Desarrolladores, DevOps, Arquitectos de Sistema  

---

## 🎯 **OBJETIVO DE ESTA GUÍA**

Esta guía proporciona procedimientos sistemáticos para diagnosticar, resolver y prevenir problemas en el sistema híbrido Paint Scanner (Android + Web). Incluye herramientas específicas, comandos de debugging y procedimientos de recuperación.

---

## 🚨 **PROBLEMAS CRÍTICOS Y SOLUCIONES**

### **🔄 PROBLEMA: Notificaciones Duplicadas (RESUELTO)**

#### **Síntomas:**
```bash
# Android Logs
📊 Notification check result: 2 notifications found
🔄 Processing stock update: Blanco Hueso (Stock: 13 → 12)
🔄 Processing stock update: Blanco Hueso (Stock: 12 → 11)  # DUPLICADA
# Stock rotando cada 10 segundos
```

#### **Diagnóstico:**
```bash
# 1. Verificar endpoint de notificaciones
curl -X GET "https://print-and-paint-studio-app-production.up.railway.app/api/android-notify/get-notifications"

# 2. Verificar status de notificaciones
curl -X GET "https://print-and-paint-studio-app-production.up.railway.app/api/android-notify/status"

# 3. Android logs para patrones duplicados
adb logcat | grep "📊 Notification check result"
```

#### **Solución Implementada:**
- ✅ **UUID único** para cada notificación
- ✅ **Estado sent/delivered** separado
- ✅ **Timeout protection** (2 minutos)
- ✅ **Smart filtering** en endpoint

---

### **📱 PROBLEMA: UI Android No Se Actualiza**

#### **Síntomas:**
```bash
# Database updates pero UI permanece igual
✅ Local paint stock updated: Blanco Hueso → 12
❌ Gallery UI not refreshing
```

#### **Diagnóstico:**
```bash
# 1. Verificar BroadcastReceiver registrado
adb logcat | grep "📡 Gallery registered for paint update broadcasts"

# 2. Verificar broadcasts enviados
adb logcat | grep "📡 UI update broadcast sent"

# 3. Verificar recepción en Gallery
adb logcat | grep "🖼️ Gallery received paint update"
```

#### **Solución:**
```java
// En GalleryFragment.onResume()
IntentFilter filter = new IntentFilter(PaintScannerApplication.ACTION_PAINT_UPDATED);
LocalBroadcastManager.getInstance(requireContext())
    .registerReceiver(paintUpdateReceiver, filter);

// En onPause() - CRÍTICO
LocalBroadcastManager.getInstance(requireContext())
    .unregisterReceiver(paintUpdateReceiver);
```

---

### **🌐 PROBLEMA: Endpoint Web No Envía Notificaciones**

#### **Síntomas:**
```bash
# Stock actualizado en web admin pero Android no recibe nada
"count": 0, "notifications": [], "total_pending": 0
```

#### **Diagnóstico:**
```bash
# 1. Verificar función send_android_notification
curl -X PUT "https://your-app.railway.app/admin/paints/4768" \
     -H "Content-Type: application/json" \
     -d '{"stock": 15}'

# 2. Verificar logs Flask
railway logs --tail

# 3. Verificar in-memory notifications
curl -X GET "https://your-app.railway.app/api/android-notify/debug"
```

#### **Solución:**
```python
# Verificar en app.py que update_paint() llama a send_android_notification
if 'stock' in data and data.get('stock') != old_stock:
    send_android_notification(id, 'stock_updated', {
        'paint_id': paint.id,
        'paint_name': paint.name,
        'old_stock': old_stock,
        'new_stock': paint.stock,
        'source': 'web_admin'
    })
```

---

## 🛠️ **HERRAMIENTAS DE DEBUGGING**

### **📱 Android Debugging Tools**

#### **1. ADB Logging Commands**
```bash
# General Paint Scanner logs
adb logcat | grep PaintScanner

# Notification specific logs
adb logcat | grep WebNotificationReceiver

# UI updates logs
adb logcat | grep "Gallery\|UI update\|broadcast"

# Database operations
adb logcat | grep PaintRepository

# Error logs only
adb logcat | grep "ERROR\|❌"
```

#### **2. Android System Information**
```bash
# Check app is running
adb shell ps | grep paintscanner

# Check memory usage
adb shell dumpsys meminfo com.paintscanner

# Check network connectivity
adb shell ping google.com

# Check app permissions
adb shell dumpsys package com.paintscanner | grep permission
```

#### **3. Database Debugging (Android)**
```bash
# From Android Studio or adb shell
# Check Room database
adb shell
cd /data/data/com.paintscanner/databases/
sqlite3 paint_database.db
.tables
SELECT COUNT(*) FROM paints;
SELECT name, stock, sync_status FROM paints WHERE name LIKE '%Blanco%';
```

### **🌐 Web Application Debugging Tools**

#### **1. Railway Platform Commands**
```bash
# Real-time logs
railway logs --tail

# Railway environment variables
railway variables

# Railway deployment status
railway status

# Railway database connection test
railway shell psql
```

#### **2. Flask Application Debugging**
```bash
# Local development with debug
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py

# Test specific endpoints
curl -X GET "http://localhost:5000/api/android-notify/status"
curl -X GET "http://localhost:5000/api/android-notify/debug"
curl -X GET "http://localhost:5000/health"
```

#### **3. Database Debugging (Web)**
```bash
# PostgreSQL queries
railway shell psql

# Check notifications in memory (via endpoint)
GET /api/android-notify/debug

# Check paint data
SELECT id, name, stock, updated_at FROM paints WHERE name ILIKE '%blanco%';

# Check recent updates
SELECT * FROM paints WHERE updated_at > NOW() - INTERVAL '1 hour';
```

### **🔗 Integration Testing Tools**

#### **1. End-to-End Testing**
```bash
#!/bin/bash
# test_integration.sh

echo "🧪 Testing Web → Android integration"

# 1. Update stock via web API
RESPONSE=$(curl -s -X PUT "https://your-app.railway.app/admin/paints/4768" \
  -H "Content-Type: application/json" \
  -d '{"stock": 99}')
echo "✅ Web update: $RESPONSE"

# 2. Wait for notification creation
sleep 2

# 3. Check notification exists
NOTIFICATIONS=$(curl -s "https://your-app.railway.app/api/android-notify/get-notifications")
echo "📋 Notifications: $NOTIFICATIONS"

# 4. Check Android receives it (manual verification)
echo "📱 Check Android logs for: '🔔 Stock updated from web'"
```

#### **2. Performance Testing**
```bash
#!/bin/bash
# performance_test.sh

echo "⚡ Performance testing notification system"

# Test multiple rapid updates
for i in {1..5}; do
  curl -s -X PUT "https://your-app.railway.app/admin/paints/4768" \
    -H "Content-Type: application/json" \
    -d "{\"stock\": $((10 + i))}"
  echo "Update $i sent"
  sleep 1
done

# Check all notifications created
curl -s "https://your-app.railway.app/api/android-notify/status"
```

---

## 🔍 **PROCEDIMIENTOS DE DIAGNÓSTICO**

### **📊 Diagnóstico Completo del Sistema**

#### **Script de Diagnóstico Automático:**
```bash
#!/bin/bash
# system_diagnosis.sh

echo "🔍 PAINT SCANNER SYSTEM DIAGNOSIS"
echo "=================================="

# 1. Web Application Health
echo "🌐 Web Application Status:"
curl -s "https://print-and-paint-studio-app-production.up.railway.app/health" | jq .

# 2. Database Connection
echo "🗄️ Database Status:"
curl -s "https://print-and-paint-studio-app-production.up.railway.app/api/android-notify/status" | jq .

# 3. Android Connectivity (requires ADB)
echo "📱 Android Application Status:"
adb devices

# 4. Notification System
echo "🔔 Notification System:"
curl -s "https://print-and-paint-studio-app-production.up.railway.app/api/android-notify/debug" | jq .

# 5. Recent Activity
echo "📈 Recent Activity:"
curl -s "https://print-and-paint-studio-app-production.up.railway.app/api/paints?limit=5&sort=updated_at" | jq '.data[] | {name, stock, updated_at}'

echo "✅ Diagnosis complete"
```

### **🚨 Diagnóstico de Problemas Críticos**

#### **1. Sistema No Responde**
```bash
# Verificar todos los componentes
echo "🔍 System responsiveness check"

# Web app health check
timeout 10 curl -f "https://your-app.railway.app/health" || echo "❌ Web app not responding"

# Database connectivity
timeout 10 curl -f "https://your-app.railway.app/api/android-notify/status" || echo "❌ Database not accessible"

# Android app responsiveness
adb shell "ps | grep paintscanner" || echo "❌ Android app not running"
```

#### **2. Memoria y Performance**
```bash
# Web application memory usage
railway metrics

# Android application memory
adb shell dumpsys meminfo com.paintscanner

# Database connection pool status
curl -s "https://your-app.railway.app/api/android-notify/status" | jq '.database_status'
```

#### **3. Errores de Red**
```bash
# Test network connectivity Android → Web
adb shell ping print-and-paint-studio-app-production.up.railway.app

# Test API endpoints from Android
adb shell curl -f "https://print-and-paint-studio-app-production.up.railway.app/health"

# Test SSL certificates
openssl s_client -connect print-and-paint-studio-app-production.up.railway.app:443 < /dev/null
```

---

## 🛡️ **PROCEDIMIENTOS DE RECUPERACIÓN**

### **🔄 Recuperación Automática**

#### **1. Restart Android Services**
```bash
# Restart WebNotificationReceiver
adb shell am force-stop com.paintscanner
adb shell monkey -p com.paintscanner 1

# Clear app cache
adb shell pm clear com.paintscanner

# Restart app
adb shell am start -n com.paintscanner/.presentation.activities.MainActivity
```

#### **2. Restart Web Services**
```bash
# Railway restart
railway restart

# Clear Railway cache
railway cache clear

# Redeploy if necessary
git push origin main  # Triggers auto-deploy
```

### **⚡ Recuperación de Emergencia**

#### **1. Rollback System**
```bash
# Web application rollback
git log --oneline -5  # Find last working commit
git checkout <last-working-commit>
git push --force origin main

# Android application rollback
# Install previous APK version
adb install -r old_version.apk
```

#### **2. Manual Sync Reset**
```bash
# Clear notification queue
curl -X DELETE "https://your-app.railway.app/api/android-notify/clear"

# Reset Android local database
adb shell
cd /data/data/com.paintscanner/databases/
rm paint_database.db*

# Force full resync
# Restart Android app - will trigger full sync
```

---

## 📊 **MONITORING Y ALERTAS**

### **🔔 Sistema de Alertas Automáticas**

#### **1. Health Check Scripts**
```bash
#!/bin/bash
# health_monitor.sh - Run every 5 minutes

HEALTH_CHECK=$(curl -s "https://your-app.railway.app/health")
STATUS=$(echo $HEALTH_CHECK | jq -r '.status')

if [ "$STATUS" != "healthy" ]; then
    echo "🚨 ALERT: System unhealthy - $HEALTH_CHECK"
    # Send notification (email, Slack, etc.)
fi

# Check notification backlog
PENDING=$(curl -s "https://your-app.railway.app/api/android-notify/status" | jq '.pending')
if [ "$PENDING" -gt 10 ]; then
    echo "⚠️ WARNING: High notification backlog - $PENDING pending"
fi
```

#### **2. Performance Monitoring**
```bash
#!/bin/bash
# performance_monitor.sh

# Check response times
RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" "https://your-app.railway.app/health")
if (( $(echo "$RESPONSE_TIME > 5.0" | bc -l) )); then
    echo "🐌 SLOW RESPONSE: $RESPONSE_TIME seconds"
fi

# Check database connections
DB_STATUS=$(curl -s "https://your-app.railway.app/api/android-notify/status" | jq '.database_connections')
echo "📊 Database connections: $DB_STATUS"
```

### **📈 Métricas Clave a Monitorear**

#### **Android App Metrics:**
```bash
# Memory usage should be < 100MB
adb shell dumpsys meminfo com.paintscanner | grep "TOTAL:"

# Network requests per minute should be < 10
adb logcat | grep "WebNotificationReceiver.*HTTP" | wc -l

# UI refresh frequency (should be minimal)
adb logcat | grep "🔄 Refreshing gallery" | wc -l
```

#### **Web App Metrics:**
```bash
# Response time should be < 1 second
curl -o /dev/null -s -w "%{time_total}" "https://your-app.railway.app/health"

# Notification queue size should be < 10
curl -s "https://your-app.railway.app/api/android-notify/status" | jq '.pending'

# Database connection pool utilization
railway metrics database
```

---

## 🚀 **OPTIMIZACIÓN Y TUNNING**

### **📱 Android Performance Tuning**

#### **1. Memory Optimization**
```java
// En PaintAdapter - Use ViewHolder pattern
@Override
public void onBindViewHolder(@NonNull PaintViewHolder holder, int position) {
    Paint paint = paints.get(position);
    
    // Clear previous image to prevent memory leaks
    Glide.with(holder.itemView.getContext()).clear(holder.imageView);
    
    // Load image efficiently
    Glide.with(holder.itemView.getContext())
        .load(paint.getImageUrl())
        .placeholder(R.drawable.placeholder)
        .error(R.drawable.error_image)
        .into(holder.imageView);
}
```

#### **2. Network Optimization**
```java
// En WebNotificationReceiver - Reduce polling if no activity
private void adjustPollingFrequency() {
    long timeSinceLastActivity = System.currentTimeMillis() - lastUserActivity;
    
    if (timeSinceLastActivity > 60000) { // 1 minute
        pollingInterval = 30000; // 30 seconds
    } else {
        pollingInterval = 10000; // 10 seconds
    }
}
```

### **🌐 Web Performance Tuning**

#### **1. Database Query Optimization**
```python
# Optimize notification queries
@app.route('/api/android-notify/get-notifications', methods=['GET'])
def get_android_notifications():
    # Use list comprehension for efficiency
    unsent_notifications = [
        notif for notif in app.pending_android_notifications 
        if not notif.get('sent', False) and 
           not notif.get('delivered_at') or 
           (datetime.utcnow() - datetime.fromisoformat(notif['delivered_at'].replace('Z', ''))).total_seconds() > 120
    ]
    
    return jsonify({
        'count': len(unsent_notifications),
        'notifications': unsent_notifications[:10]  # Limit response size
    })
```

#### **2. Caching Strategy**
```python
# Implement Redis cache for frequent queries
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)  # 5 minutes
def get_paint_data(paint_id):
    return Paint.query.filter_by(id=paint_id).first()
```

---

## 🔐 **SEGURIDAD Y LOGS**

### **🛡️ Security Monitoring**

#### **1. API Security Checks**
```bash
# Check for unauthorized access attempts
railway logs | grep "401\|403\|404" | tail -10

# Monitor API rate limiting
railway logs | grep "rate limit" | tail -10

# Check SSL certificate status
echo | openssl s_client -connect your-app.railway.app:443 2>/dev/null | openssl x509 -noout -dates
```

#### **2. Data Integrity Checks**
```sql
-- Check for data inconsistencies
SELECT COUNT(*) as total_paints FROM paints;
SELECT COUNT(*) as paints_with_stock FROM paints WHERE stock > 0;
SELECT COUNT(*) as recent_updates FROM paints WHERE updated_at > NOW() - INTERVAL '24 hours';
```

### **📝 Log Analysis**

#### **1. Error Pattern Detection**
```bash
# Find frequent errors
railway logs | grep ERROR | awk '{print $NF}' | sort | uniq -c | sort -nr

# Check notification processing errors
railway logs | grep "notification.*error" | tail -20

# Monitor database connection errors
railway logs | grep "database.*connection.*error" | tail -10
```

#### **2. Performance Pattern Analysis**
```bash
# Find slow requests
railway logs | grep "slow" | tail -20

# Check notification processing times
railway logs | grep "notification.*processed.*[0-9]ms" | tail -10

# Monitor memory usage patterns
railway logs | grep "memory" | tail -20
```

---

## 📚 **REFERENCIAS RÁPIDAS**

### **🔗 URLs Importantes**
```bash
# Production URLs
WEB_APP="https://print-and-paint-studio-app-production.up.railway.app"
HEALTH_CHECK="$WEB_APP/health"
NOTIFICATION_STATUS="$WEB_APP/api/android-notify/status"
NOTIFICATION_DEBUG="$WEB_APP/api/android-notify/debug"

# API Endpoints
GET_NOTIFICATIONS="$WEB_APP/api/android-notify/get-notifications"
CONFIRM_PROCESSED="$WEB_APP/api/android-notify/confirm-processed"
CLEAR_NOTIFICATIONS="$WEB_APP/api/android-notify/clear"
```

### **📱 Android Package Info**
```bash
PACKAGE_NAME="com.paintscanner"
MAIN_ACTIVITY="$PACKAGE_NAME/.presentation.activities.MainActivity"
DATABASE_PATH="/data/data/$PACKAGE_NAME/databases/paint_database.db"
```

### **🌐 Railway Commands**
```bash
# Essential Railway commands
railway login
railway status
railway logs --tail
railway restart
railway variables
railway shell psql
```

---

## 🎯 **CHECKLIST DE TROUBLESHOOTING**

### **✅ Antes de Reportar un Bug:**
- [ ] ✅ Verificar logs de Android (adb logcat)
- [ ] ✅ Verificar logs de Web (railway logs)
- [ ] ✅ Ejecutar health check endpoints
- [ ] ✅ Verificar conectividad de red
- [ ] ✅ Comprobar estado de base de datos
- [ ] ✅ Verificar versiones de ambas aplicaciones
- [ ] ✅ Reproducir el problema paso a paso
- [ ] ✅ Documentar comportamiento esperado vs actual

### **🛠️ Durante la Resolución:**
- [ ] ✅ Identificar componente afectado (Android/Web/Database)
- [ ] ✅ Aislar el problema con testing específico
- [ ] ✅ Aplicar fix en directorio correcto
- [ ] ✅ Verificar no afecta otros componentes
- [ ] ✅ Testing completo antes de deploy
- [ ] ✅ Monitorear métricas post-fix
- [ ] ✅ Documentar solución para futuras referencias

### **📊 Después de la Resolución:**
- [ ] ✅ Confirmar que el problema está resuelto
- [ ] ✅ Verificar métricas de performance
- [ ] ✅ Actualizar documentación si es necesario
- [ ] ✅ Implementar prevención si aplica
- [ ] ✅ Comunicar solución al equipo

---

**🔧 Documentado por**: Claude Code Assistant  
**🎯 Objetivo**: Resolución rápida y efectiva de problemas  
**🔄 Mantenimiento**: Actualizar con nuevos problemas y soluciones  
**📞 Soporte**: Usar esta guía como primera referencia