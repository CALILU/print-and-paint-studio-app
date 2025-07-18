# Troubleshooting and Monitoring Guide

## Overview

Comprehensive guide for monitoring, debugging, and troubleshooting performance issues in the Paint and Print Studio application. This document provides tools, techniques, and procedures for maintaining optimal system performance.

## Monitoring Infrastructure

### Performance Metrics Dashboard

#### Key Performance Indicators (KPIs)
```javascript
const PERFORMANCE_THRESHOLDS = {
    // Response Time Metrics
    page_load_time: { warning: 3000, critical: 5000 },      // milliseconds
    api_response_time: { warning: 2000, critical: 5000 },   // milliseconds
    database_query_time: { warning: 1000, critical: 3000 }, // milliseconds
    
    // Resource Utilization
    memory_usage: { warning: 80, critical: 90 },            // percentage
    cpu_usage: { warning: 70, critical: 85 },               // percentage
    connection_pool_usage: { warning: 70, critical: 85 },   // percentage
    
    // Error Rates
    http_error_rate: { warning: 1, critical: 5 },           // percentage
    database_error_rate: { warning: 0.5, critical: 2 },     // percentage
    image_load_error_rate: { warning: 5, critical: 10 },    // percentage
    
    // Business Metrics
    concurrent_users: { warning: 50, critical: 100 },       // count
    cache_hit_rate: { warning: 70, critical: 50 },          // percentage (lower is worse)
    lazy_loading_efficiency: { warning: 80, critical: 60 }   // percentage
};
```

#### Real-time Monitoring Implementation
```javascript
class ApplicationMonitor {
    constructor() {
        this.metrics = new Map();
        this.alerts = [];
        this.isMonitoring = false;
        this.monitoringInterval = 30000; // 30 seconds
    }
    
    start() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.collectMetrics();
        
        setInterval(() => {
            if (this.isMonitoring) {
                this.collectMetrics();
            }
        }, this.monitoringInterval);
        
        console.log('📊 Application monitoring started');
    }
    
    async collectMetrics() {
        const timestamp = Date.now();
        
        try {
            // Performance metrics
            const performanceMetrics = this.getPerformanceMetrics();
            
            // Resource metrics
            const resourceMetrics = await this.getResourceMetrics();
            
            // Business metrics
            const businessMetrics = this.getBusinessMetrics();
            
            // Combine all metrics
            const allMetrics = {
                timestamp,
                performance: performanceMetrics,
                resources: resourceMetrics,
                business: businessMetrics
            };
            
            this.metrics.set(timestamp, allMetrics);
            this.checkThresholds(allMetrics);
            this.cleanupOldMetrics();
            
        } catch (error) {
            console.error('❌ Error collecting metrics:', error);
        }
    }
    
    getPerformanceMetrics() {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paintEntries = performance.getEntriesByType('paint');
        
        return {
            page_load_time: navigation ? navigation.loadEventEnd - navigation.fetchStart : null,
            dom_content_loaded: navigation ? navigation.domContentLoadedEventEnd - navigation.fetchStart : null,
            first_paint: paintEntries.find(entry => entry.name === 'first-paint')?.startTime || null,
            largest_contentful_paint: this.getLCP(),
            cumulative_layout_shift: this.getCLS()
        };
    }
    
    async getResourceMetrics() {
        if ('memory' in performance) {
            const memInfo = performance.memory;
            return {
                used_memory: memInfo.usedJSHeapSize,
                total_memory: memInfo.totalJSHeapSize,
                memory_limit: memInfo.jsHeapSizeLimit,
                memory_usage_percent: (memInfo.usedJSHeapSize / memInfo.jsHeapSizeLimit) * 100
            };
        }
        
        return {
            memory_usage_percent: null // Not available in all browsers
        };
    }
    
    getBusinessMetrics() {
        const lazyImages = document.querySelectorAll('.lazy-load');
        const loadedImages = document.querySelectorAll('.lazy-load:not([data-src])');
        
        return {
            total_images: lazyImages.length,
            loaded_images: loadedImages.length,
            lazy_loading_efficiency: lazyImages.length > 0 ? (loadedImages.length / lazyImages.length) * 100 : 100,
            cache_hits: this.getCacheHits(),
            active_requests: this.getActiveRequests()
        };
    }
    
    checkThresholds(metrics) {
        const alerts = [];
        
        // Check performance thresholds
        if (metrics.performance.page_load_time > PERFORMANCE_THRESHOLDS.page_load_time.critical) {
            alerts.push({
                level: 'critical',
                metric: 'page_load_time',
                value: metrics.performance.page_load_time,
                threshold: PERFORMANCE_THRESHOLDS.page_load_time.critical,
                message: `Page load time (${metrics.performance.page_load_time}ms) exceeds critical threshold`
            });
        }
        
        // Check memory usage
        if (metrics.resources.memory_usage_percent > PERFORMANCE_THRESHOLDS.memory_usage.critical) {
            alerts.push({
                level: 'critical',
                metric: 'memory_usage',
                value: metrics.resources.memory_usage_percent,
                threshold: PERFORMANCE_THRESHOLDS.memory_usage.critical,
                message: `Memory usage (${metrics.resources.memory_usage_percent.toFixed(1)}%) exceeds critical threshold`
            });
        }
        
        // Process alerts
        alerts.forEach(alert => this.handleAlert(alert));
    }
    
    handleAlert(alert) {
        console.warn(`🚨 ${alert.level.toUpperCase()}: ${alert.message}`);
        this.alerts.push({ ...alert, timestamp: Date.now() });
        
        // Trigger alert notifications
        if (alert.level === 'critical') {
            this.sendCriticalAlert(alert);
        }
    }
    
    sendCriticalAlert(alert) {
        // In production, this would send notifications
        // For now, just log to console and show user notification
        
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
        notification.innerHTML = `
            <strong>Performance Alert:</strong> ${alert.message}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }
    
    getMetricsSummary(timeRange = 300000) { // 5 minutes
        const cutoff = Date.now() - timeRange;
        const recentMetrics = Array.from(this.metrics.entries())
            .filter(([timestamp]) => timestamp >= cutoff)
            .map(([, metrics]) => metrics);
        
        if (recentMetrics.length === 0) return null;
        
        return {
            count: recentMetrics.length,
            averages: this.calculateAverages(recentMetrics),
            trends: this.calculateTrends(recentMetrics),
            alerts: this.alerts.filter(alert => alert.timestamp >= cutoff)
        };
    }
    
    calculateAverages(metrics) {
        const sum = (arr, key) => arr.reduce((acc, item) => {
            const value = this.getNestedValue(item, key);
            return value !== null ? acc + value : acc;
        }, 0);
        
        const avg = (arr, key) => {
            const values = arr.map(item => this.getNestedValue(item, key)).filter(v => v !== null);
            return values.length > 0 ? sum(arr, key) / values.length : null;
        };
        
        return {
            page_load_time: avg(metrics, 'performance.page_load_time'),
            memory_usage: avg(metrics, 'resources.memory_usage_percent'),
            lazy_loading_efficiency: avg(metrics, 'business.lazy_loading_efficiency')
        };
    }
    
    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => current?.[key], obj);
    }
    
    exportMetrics() {
        const summary = this.getMetricsSummary();
        const exportData = {
            timestamp: new Date().toISOString(),
            summary,
            thresholds: PERFORMANCE_THRESHOLDS,
            alerts: this.alerts
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `performance-metrics-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
    
    stop() {
        this.isMonitoring = false;
        console.log('📊 Application monitoring stopped');
    }
}

// Initialize global monitor
const appMonitor = new ApplicationMonitor();

// Auto-start monitoring in production
if (window.location.hostname !== 'localhost') {
    appMonitor.start();
}

// Expose for manual control
window.appMonitor = appMonitor;
```

### Backend Monitoring

#### Database Performance Monitor
```python
import time
import psutil
import logging
from collections import deque, defaultdict
from functools import wraps

class DatabaseMonitor:
    def __init__(self):
        self.query_times = deque(maxlen=1000)  # Last 1000 queries
        self.connection_stats = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.slow_query_threshold = 1.0  # seconds
        
    def monitor_query(self, func):
        """Decorator to monitor database query performance"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            query_id = f"{func.__name__}_{id(func)}"
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record query performance
                self.query_times.append({
                    'query_id': query_id,
                    'execution_time': execution_time,
                    'timestamp': start_time,
                    'success': True
                })
                
                # Log slow queries
                if execution_time > self.slow_query_threshold:
                    logging.warning(f"🐌 Slow query detected: {query_id} took {execution_time:.3f}s")
                
                print(f"📊 Query {query_id}: {execution_time:.3f}s")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                self.error_counts[query_id] += 1
                
                # Record failed query
                self.query_times.append({
                    'query_id': query_id,
                    'execution_time': execution_time,
                    'timestamp': start_time,
                    'success': False,
                    'error': str(e)
                })
                
                logging.error(f"❌ Query failed: {query_id} after {execution_time:.3f}s - {str(e)}")
                raise
                
        return wrapper
    
    def get_connection_pool_status(self):
        """Get current connection pool statistics"""
        try:
            engine = db.engine
            pool = engine.pool
            
            status = {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid(),
                'utilization': (pool.checkedout() / (pool.size() + pool.overflow())) * 100
            }
            
            self.connection_stats['timestamp'].append(time.time())
            self.connection_stats['utilization'].append(status['utilization'])
            
            return status
            
        except Exception as e:
            logging.error(f"Error getting connection pool status: {e}")
            return None
    
    def get_query_statistics(self, time_window=300):  # 5 minutes
        """Get query performance statistics"""
        cutoff_time = time.time() - time_window
        recent_queries = [q for q in self.query_times if q['timestamp'] >= cutoff_time]
        
        if not recent_queries:
            return None
        
        successful_queries = [q for q in recent_queries if q['success']]
        failed_queries = [q for q in recent_queries if not q['success']]
        
        execution_times = [q['execution_time'] for q in successful_queries]
        
        return {
            'total_queries': len(recent_queries),
            'successful_queries': len(successful_queries),
            'failed_queries': len(failed_queries),
            'error_rate': (len(failed_queries) / len(recent_queries)) * 100,
            'avg_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'max_execution_time': max(execution_times) if execution_times else 0,
            'min_execution_time': min(execution_times) if execution_times else 0,
            'slow_queries': len([t for t in execution_times if t > self.slow_query_threshold])
        }
    
    def get_system_metrics(self):
        """Get system resource metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            }
        }
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        pool_status = self.get_connection_pool_status()
        query_stats = self.get_query_statistics()
        system_metrics = self.get_system_metrics()
        
        health_score = self.calculate_health_score(pool_status, query_stats, system_metrics)
        
        return {
            'timestamp': time.time(),
            'health_score': health_score,
            'connection_pool': pool_status,
            'query_performance': query_stats,
            'system_resources': system_metrics,
            'alerts': self.get_current_alerts(pool_status, query_stats, system_metrics)
        }
    
    def calculate_health_score(self, pool_status, query_stats, system_metrics):
        """Calculate overall system health score (0-100)"""
        score = 100
        
        # Connection pool health (30% weight)
        if pool_status and pool_status['utilization'] > 80:
            score -= 30
        elif pool_status and pool_status['utilization'] > 60:
            score -= 15
        
        # Query performance health (40% weight)
        if query_stats:
            if query_stats['error_rate'] > 5:
                score -= 40
            elif query_stats['error_rate'] > 1:
                score -= 20
            
            if query_stats['avg_execution_time'] > 2:
                score -= 20
            elif query_stats['avg_execution_time'] > 1:
                score -= 10
        
        # System resources health (30% weight)
        if system_metrics:
            if system_metrics['memory']['percent'] > 90:
                score -= 30
            elif system_metrics['memory']['percent'] > 80:
                score -= 15
            
            if system_metrics['cpu_percent'] > 85:
                score -= 15
        
        return max(0, score)
    
    def get_current_alerts(self, pool_status, query_stats, system_metrics):
        """Get current system alerts"""
        alerts = []
        
        # Connection pool alerts
        if pool_status and pool_status['utilization'] > 85:
            alerts.append({
                'level': 'critical',
                'type': 'connection_pool',
                'message': f"Connection pool utilization is {pool_status['utilization']:.1f}%"
            })
        
        # Query performance alerts
        if query_stats:
            if query_stats['error_rate'] > 5:
                alerts.append({
                    'level': 'critical',
                    'type': 'query_errors',
                    'message': f"Query error rate is {query_stats['error_rate']:.1f}%"
                })
            
            if query_stats['avg_execution_time'] > 2:
                alerts.append({
                    'level': 'warning',
                    'type': 'slow_queries',
                    'message': f"Average query time is {query_stats['avg_execution_time']:.3f}s"
                })
        
        # System resource alerts
        if system_metrics:
            if system_metrics['memory']['percent'] > 90:
                alerts.append({
                    'level': 'critical',
                    'type': 'memory',
                    'message': f"Memory usage is {system_metrics['memory']['percent']:.1f}%"
                })
        
        return alerts

# Global database monitor
db_monitor = DatabaseMonitor()

# Apply monitoring to database functions
@db_monitor.monitor_query
def get_paint(paint_id):
    return db.session.query(Paint).filter_by(id=paint_id).first()

# Health check endpoint
@app.route('/health')
def health_check():
    """System health check endpoint"""
    try:
        report = db_monitor.generate_health_report()
        
        status_code = 200
        if report['health_score'] < 70:
            status_code = 503  # Service Unavailable
        elif report['health_score'] < 85:
            status_code = 206  # Partial Content (degraded)
        
        return jsonify(report), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'health_score': 0
        }), 500
```

## Troubleshooting Procedures

### Common Performance Issues

#### Issue 1: High Response Times
```bash
# Symptoms
- API responses > 5 seconds
- User interface freezing
- Database connection timeouts

# Diagnostic Steps
1. Check connection pool utilization
2. Analyze slow query log
3. Monitor system resources
4. Review application logs

# Resolution
- Optimize database queries
- Increase connection pool size
- Add query caching
- Scale infrastructure
```

#### Issue 2: Memory Leaks
```javascript
// Detection script
function detectMemoryLeaks() {
    const initial = performance.memory?.usedJSHeapSize || 0;
    
    setTimeout(() => {
        const current = performance.memory?.usedJSHeapSize || 0;
        const increase = current - initial;
        
        if (increase > 50 * 1024 * 1024) { // 50MB increase
            console.warn(`🧠 Potential memory leak detected: ${(increase / 1024 / 1024).toFixed(1)}MB increase`);
            
            // Analyze potential causes
            const listeners = getEventListenerCount();
            const observers = getObserverCount();
            const caches = getCacheSize();
            
            console.log('Memory leak analysis:', {
                eventListeners: listeners,
                observers: observers,
                cacheSize: caches
            });
        }
    }, 60000); // Check after 1 minute
}

function getEventListenerCount() {
    // Count event listeners (approximate)
    const elements = document.querySelectorAll('*');
    let count = 0;
    
    elements.forEach(element => {
        if (element._listeners) {
            count += Object.keys(element._listeners).length;
        }
    });
    
    return count;
}

// Run memory leak detection
detectMemoryLeaks();
```

#### Issue 3: Database Connection Pool Exhaustion
```python
# Diagnostic function
def diagnose_connection_issues():
    """Diagnose database connection problems"""
    pool_status = db_monitor.get_connection_pool_status()
    
    print("🔍 Connection Pool Diagnosis:")
    print(f"  Pool Size: {pool_status['pool_size']}")
    print(f"  Checked Out: {pool_status['checked_out']}")
    print(f"  Checked In: {pool_status['checked_in']}")
    print(f"  Overflow: {pool_status['overflow']}")
    print(f"  Utilization: {pool_status['utilization']:.1f}%")
    
    if pool_status['utilization'] > 80:
        print("🚨 High pool utilization detected!")
        print("Recommendations:")
        print("  1. Check for connection leaks")
        print("  2. Increase pool size")
        print("  3. Optimize query performance")
        print("  4. Add connection monitoring")
    
    # Check for long-running queries
    active_connections = db.session.execute("""
        SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
        FROM pg_stat_activity 
        WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
    """).fetchall()
    
    if active_connections:
        print("🐌 Long-running queries detected:")
        for conn in active_connections:
            print(f"  PID {conn.pid}: {conn.duration} - {conn.query[:100]}...")
```

### Performance Debugging Tools

#### Browser Performance Profiler
```javascript
class PerformanceProfiler {
    constructor() {
        this.profiles = [];
        this.isRecording = false;
    }
    
    startProfiling(name) {
        if (this.isRecording) {
            console.warn('Profiling already in progress');
            return;
        }
        
        this.isRecording = true;
        this.currentProfile = {
            name,
            startTime: performance.now(),
            marks: [],
            measures: []
        };
        
        performance.mark(`${name}-start`);
        console.log(`🎯 Started profiling: ${name}`);
    }
    
    mark(label) {
        if (!this.isRecording) return;
        
        const markName = `${this.currentProfile.name}-${label}`;
        performance.mark(markName);
        
        this.currentProfile.marks.push({
            label,
            timestamp: performance.now(),
            markName
        });
        
        console.log(`📍 Mark: ${label} at ${performance.now().toFixed(2)}ms`);
    }
    
    measure(name, startMark, endMark) {
        if (!this.isRecording) return;
        
        const measureName = `${this.currentProfile.name}-${name}`;
        performance.measure(measureName, startMark, endMark);
        
        const measure = performance.getEntriesByName(measureName)[0];
        this.currentProfile.measures.push({
            name,
            duration: measure.duration,
            startTime: measure.startTime
        });
        
        console.log(`📏 Measure: ${name} took ${measure.duration.toFixed(2)}ms`);
    }
    
    stopProfiling() {
        if (!this.isRecording) return;
        
        const endTime = performance.now();
        this.currentProfile.endTime = endTime;
        this.currentProfile.totalDuration = endTime - this.currentProfile.startTime;
        
        performance.mark(`${this.currentProfile.name}-end`);
        performance.measure(
            `${this.currentProfile.name}-total`,
            `${this.currentProfile.name}-start`,
            `${this.currentProfile.name}-end`
        );
        
        this.profiles.push({ ...this.currentProfile });
        this.isRecording = false;
        
        console.log(`🏁 Finished profiling: ${this.currentProfile.name} (${this.currentProfile.totalDuration.toFixed(2)}ms)`);
        this.printProfileSummary(this.currentProfile);
        
        return this.currentProfile;
    }
    
    printProfileSummary(profile) {
        console.group(`📊 Profile Summary: ${profile.name}`);
        console.log(`Total Duration: ${profile.totalDuration.toFixed(2)}ms`);
        
        if (profile.marks.length > 0) {
            console.log('Marks:');
            profile.marks.forEach(mark => {
                console.log(`  ${mark.label}: ${(mark.timestamp - profile.startTime).toFixed(2)}ms`);
            });
        }
        
        if (profile.measures.length > 0) {
            console.log('Measures:');
            profile.measures.forEach(measure => {
                console.log(`  ${measure.name}: ${measure.duration.toFixed(2)}ms`);
            });
        }
        
        console.groupEnd();
    }
    
    exportProfiles() {
        const data = {
            timestamp: new Date().toISOString(),
            profiles: this.profiles,
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `performance-profile-${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
}

// Global profiler
const profiler = new PerformanceProfiler();

// Usage example
profiler.startProfiling('paint-loading');
profiler.mark('data-fetch-start');
// ... fetch data ...
profiler.mark('data-fetch-end');
profiler.mark('render-start');
// ... render UI ...
profiler.mark('render-end');
profiler.measure('data-fetch', 'paint-loading-data-fetch-start', 'paint-loading-data-fetch-end');
profiler.measure('render', 'paint-loading-render-start', 'paint-loading-render-end');
profiler.stopProfiling();
```

#### Database Query Analyzer
```python
class QueryAnalyzer:
    def __init__(self):
        self.query_log = []
        self.explain_cache = {}
    
    def analyze_query(self, query, params=None):
        """Analyze a database query performance"""
        try:
            # Execute EXPLAIN ANALYZE
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            
            if params:
                result = db.session.execute(text(explain_query), params)
            else:
                result = db.session.execute(text(explain_query))
            
            explain_data = result.fetchone()[0][0]
            
            analysis = {
                'query': query,
                'execution_time': explain_data.get('Execution Time', 0),
                'planning_time': explain_data.get('Planning Time', 0),
                'total_cost': explain_data['Plan'].get('Total Cost', 0),
                'rows': explain_data['Plan'].get('Actual Rows', 0),
                'loops': explain_data['Plan'].get('Actual Loops', 1),
                'node_type': explain_data['Plan'].get('Node Type', 'Unknown'),
                'buffers': explain_data['Plan'].get('Shared Hit Blocks', 0),
                'recommendations': []
            }
            
            # Generate recommendations
            analysis['recommendations'] = self.generate_recommendations(analysis)
            
            self.query_log.append(analysis)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing query: {e}")
            return None
    
    def generate_recommendations(self, analysis):
        """Generate performance recommendations"""
        recommendations = []
        
        # High execution time
        if analysis['execution_time'] > 1000:  # 1 second
            recommendations.append("Consider adding indexes or optimizing WHERE clauses")
        
        # High cost
        if analysis['total_cost'] > 1000:
            recommendations.append("Query has high cost - review join conditions and filtering")
        
        # Sequential scans
        if 'Seq Scan' in analysis['node_type']:
            recommendations.append("Sequential scan detected - consider adding appropriate indexes")
        
        # High buffer usage
        if analysis['buffers'] > 10000:
            recommendations.append("High buffer usage - consider query optimization")
        
        return recommendations
    
    def get_slow_queries(self, threshold=1000):
        """Get queries slower than threshold (ms)"""
        return [q for q in self.query_log if q['execution_time'] > threshold]
    
    def get_query_report(self):
        """Generate comprehensive query performance report"""
        if not self.query_log:
            return "No queries analyzed yet"
        
        total_queries = len(self.query_log)
        avg_execution_time = sum(q['execution_time'] for q in self.query_log) / total_queries
        slow_queries = self.get_slow_queries()
        
        report = f"""
Query Performance Report
========================
Total Queries Analyzed: {total_queries}
Average Execution Time: {avg_execution_time:.2f}ms
Slow Queries (>1s): {len(slow_queries)}

Top 5 Slowest Queries:
"""
        
        # Sort by execution time and get top 5
        sorted_queries = sorted(self.query_log, key=lambda q: q['execution_time'], reverse=True)[:5]
        
        for i, query in enumerate(sorted_queries, 1):
            report += f"""
{i}. Execution Time: {query['execution_time']:.2f}ms
   Query: {query['query'][:100]}...
   Recommendations: {', '.join(query['recommendations']) if query['recommendations'] else 'None'}
"""
        
        return report

# Global query analyzer
query_analyzer = QueryAnalyzer()

# Decorator to automatically analyze queries
def analyze_db_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # This would need to be integrated with actual query execution
        # For now, it's a placeholder for the concept
        result = func(*args, **kwargs)
        return result
    return wrapper
```

### Error Recovery Procedures

#### Automated Recovery Scripts
```python
class AutoRecovery:
    def __init__(self):
        self.recovery_actions = {
            'high_memory_usage': self.handle_memory_issue,
            'connection_pool_exhaustion': self.handle_connection_issue,
            'slow_queries': self.handle_slow_queries,
            'cache_miss_rate': self.handle_cache_issues
        }
    
    def handle_memory_issue(self, alert):
        """Handle high memory usage"""
        print("🧠 Handling memory issue...")
        
        # Clear caches
        if hasattr(cache_manager, 'clear'):
            cache_manager.clear()
            print("  ✅ Cleared application cache")
        
        # Force garbage collection
        import gc
        collected = gc.collect()
        print(f"  ✅ Garbage collected {collected} objects")
        
        # Restart if memory usage is critical
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 95:
            print("  🔄 Critical memory usage - requesting restart")
            self.request_restart("Critical memory usage")
    
    def handle_connection_issue(self, alert):
        """Handle connection pool issues"""
        print("🔌 Handling connection pool issue...")
        
        # Close idle connections
        try:
            db.engine.dispose()
            print("  ✅ Disposed connection pool")
        except Exception as e:
            print(f"  ❌ Error disposing connections: {e}")
        
        # Reset connection pool
        try:
            db.engine.pool._reset_pooled()
            print("  ✅ Reset connection pool")
        except Exception as e:
            print(f"  ❌ Error resetting pool: {e}")
    
    def handle_slow_queries(self, alert):
        """Handle slow query issues"""
        print("🐌 Handling slow query issue...")
        
        # Enable query logging temporarily
        app.config['SQLALCHEMY_ECHO'] = True
        
        # Clear query cache if exists
        if hasattr(cache_manager, 'invalidate'):
            cache_manager.invalidate()
            print("  ✅ Cleared query cache")
        
        # Schedule query analysis
        self.schedule_query_analysis()
    
    def handle_cache_issues(self, alert):
        """Handle cache performance issues"""
        print("📦 Handling cache issue...")
        
        # Warm up cache with most common queries
        self.warm_cache()
        
        # Adjust cache TTL
        if hasattr(cache_manager, 'adjust_ttl'):
            cache_manager.adjust_ttl(increase=True)
            print("  ✅ Increased cache TTL")
    
    def request_restart(self, reason):
        """Request application restart"""
        print(f"🔄 Restart requested: {reason}")
        
        # In production, this would trigger a graceful restart
        # For now, just log the request
        logging.critical(f"Application restart requested: {reason}")
        
        # Could integrate with Docker/Kubernetes for automatic restart
        # os.system("touch /tmp/restart_required")
    
    def warm_cache(self):
        """Warm up application cache"""
        print("🔥 Warming up cache...")
        
        try:
            # Pre-load common data
            popular_paints = db.session.query(Paint).limit(100).all()
            print(f"  ✅ Pre-loaded {len(popular_paints)} popular paints")
            
        except Exception as e:
            print(f"  ❌ Error warming cache: {e}")

# Global auto-recovery instance
auto_recovery = AutoRecovery()

# Integration with monitoring
def handle_system_alert(alert):
    """Handle system alerts with automated recovery"""
    alert_type = alert.get('type')
    
    if alert_type in auto_recovery.recovery_actions:
        auto_recovery.recovery_actions[alert_type](alert)
    else:
        print(f"⚠️ No automated recovery for alert type: {alert_type}")
```

### Log Analysis Tools

#### Log Parser and Analyzer
```python
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class LogAnalyzer:
    def __init__(self, log_file_path=None):
        self.log_file_path = log_file_path
        self.parsed_logs = []
        self.error_patterns = [
            r'ERROR:',
            r'CRITICAL:',
            r'TimeoutError',
            r'ConnectionError',
            r'OperationalError'
        ]
        
    def parse_logs(self, time_window_hours=24):
        """Parse application logs for analysis"""
        if not self.log_file_path:
            return
        
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        try:
            with open(self.log_file_path, 'r') as f:
                for line in f:
                    log_entry = self.parse_log_line(line)
                    if log_entry and log_entry['timestamp'] >= cutoff_time:
                        self.parsed_logs.append(log_entry)
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file_path}")
    
    def parse_log_line(self, line):
        """Parse individual log line"""
        # Basic log format: [TIMESTAMP] LEVEL: MESSAGE
        pattern = r'\[([^\]]+)\]\s+(\w+):\s+(.*)'
        match = re.match(pattern, line.strip())
        
        if match:
            timestamp_str, level, message = match.groups()
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                return {
                    'timestamp': timestamp,
                    'level': level,
                    'message': message,
                    'raw': line
                }
            except ValueError:
                pass
        
        return None
    
    def analyze_errors(self):
        """Analyze error patterns in logs"""
        errors = [log for log in self.parsed_logs if log['level'] in ['ERROR', 'CRITICAL']]
        
        if not errors:
            return "No errors found in log analysis period"
        
        # Group errors by message pattern
        error_groups = defaultdict(list)
        for error in errors:
            # Simplify error message for grouping
            simplified = re.sub(r'\d+', 'N', error['message'])  # Replace numbers
            simplified = re.sub(r'[a-f0-9]{8,}', 'HASH', simplified)  # Replace hashes
            error_groups[simplified].append(error)
        
        analysis = {
            'total_errors': len(errors),
            'error_types': Counter(error['level'] for error in errors),
            'error_groups': {
                pattern: {
                    'count': len(group),
                    'first_occurrence': min(error['timestamp'] for error in group),
                    'last_occurrence': max(error['timestamp'] for error in group),
                    'example': group[0]['message']
                }
                for pattern, group in error_groups.items()
            }
        }
        
        return analysis
    
    def get_performance_trends(self):
        """Analyze performance trends from logs"""
        # Look for performance-related log entries
        perf_logs = [
            log for log in self.parsed_logs 
            if any(keyword in log['message'].lower() 
                  for keyword in ['took', 'seconds', 'ms', 'performance', 'slow'])
        ]
        
        # Extract timing information
        timings = []
        for log in perf_logs:
            # Look for timing patterns like "took 1.23s" or "123ms"
            timing_match = re.search(r'(\d+\.?\d*)\s*(ms|seconds?|s)\b', log['message'])
            if timing_match:
                value, unit = timing_match.groups()
                # Convert to milliseconds
                if unit.startswith('s'):
                    ms_value = float(value) * 1000
                else:
                    ms_value = float(value)
                
                timings.append({
                    'timestamp': log['timestamp'],
                    'value_ms': ms_value,
                    'message': log['message']
                })
        
        if not timings:
            return "No performance data found in logs"
        
        # Calculate trends
        avg_time = sum(t['value_ms'] for t in timings) / len(timings)
        max_time = max(t['value_ms'] for t in timings)
        slow_operations = [t for t in timings if t['value_ms'] > 5000]  # > 5 seconds
        
        return {
            'total_operations': len(timings),
            'average_time_ms': avg_time,
            'max_time_ms': max_time,
            'slow_operations': len(slow_operations),
            'trends': self.calculate_time_trends(timings)
        }
    
    def calculate_time_trends(self, timings):
        """Calculate performance trends over time"""
        # Group by hour
        hourly_data = defaultdict(list)
        for timing in timings:
            hour_key = timing['timestamp'].replace(minute=0, second=0, microsecond=0)
            hourly_data[hour_key].append(timing['value_ms'])
        
        # Calculate hourly averages
        hourly_averages = {
            hour: sum(values) / len(values)
            for hour, values in hourly_data.items()
        }
        
        # Determine trend direction
        if len(hourly_averages) > 1:
            hours = sorted(hourly_averages.keys())
            first_half = sum(hourly_averages[h] for h in hours[:len(hours)//2])
            second_half = sum(hourly_averages[h] for h in hours[len(hours)//2:])
            
            if second_half > first_half * 1.1:
                trend = "deteriorating"
            elif second_half < first_half * 0.9:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            'direction': trend,
            'hourly_averages': hourly_averages
        }
    
    def generate_report(self):
        """Generate comprehensive log analysis report"""
        error_analysis = self.analyze_errors()
        performance_trends = self.get_performance_trends()
        
        report = f"""
Log Analysis Report
==================
Analysis Period: Last 24 hours
Total Log Entries: {len(self.parsed_logs)}

Error Analysis:
{self.format_error_analysis(error_analysis)}

Performance Trends:
{self.format_performance_analysis(performance_trends)}
"""
        return report
    
    def format_error_analysis(self, analysis):
        """Format error analysis for report"""
        if isinstance(analysis, str):
            return analysis
        
        output = f"Total Errors: {analysis['total_errors']}\n"
        
        for error_type, count in analysis['error_types'].items():
            output += f"{error_type}: {count}\n"
        
        output += "\nTop Error Patterns:\n"
        sorted_groups = sorted(
            analysis['error_groups'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:5]
        
        for pattern, info in sorted_groups:
            output += f"  {info['count']} occurrences: {info['example'][:100]}...\n"
        
        return output
    
    def format_performance_analysis(self, analysis):
        """Format performance analysis for report"""
        if isinstance(analysis, str):
            return analysis
        
        return f"""
Total Operations: {analysis['total_operations']}
Average Time: {analysis['average_time_ms']:.2f}ms
Max Time: {analysis['max_time_ms']:.2f}ms
Slow Operations: {analysis['slow_operations']}
Trend: {analysis['trends']['direction']}
"""

# Usage
log_analyzer = LogAnalyzer('/path/to/application.log')
log_analyzer.parse_logs()
report = log_analyzer.generate_report()
print(report)
```

This comprehensive troubleshooting and monitoring guide provides the tools and procedures necessary to maintain optimal performance and quickly identify and resolve issues in the Paint and Print Studio application.