import Foundation
import UIKit

class ImagePerformanceMonitor: ObservableObject {
    static let shared = ImagePerformanceMonitor()
    
    // Performance data
    private var loadTimes: [String: [TimeInterval]] = [:]
    private var successRates: [String: SuccessRate] = [:]
    private var cacheHitRates: [String: CacheRate] = [:]
    
    // Configuration
    private let maxDataPoints = 100
    private let performanceThreshold: TimeInterval = 2.0 // 2 seconds
    
    private init() {
        loadPerformanceData()
    }
    
    // MARK: - Public Methods
    
    /// Track image load performance
    func trackImageLoad(
        url: String,
        loadTime: TimeInterval,
        success: Bool,
        cacheHit: Bool = false
    ) {
        // Track load times
        if loadTimes[url] == nil {
            loadTimes[url] = []
        }
        loadTimes[url]?.append(loadTime)
        
        // Limit data points
        if let times = loadTimes[url], times.count > maxDataPoints {
            loadTimes[url] = Array(times.suffix(maxDataPoints))
        }
        
        // Track success rates
        if successRates[url] == nil {
            successRates[url] = SuccessRate(success: 0, total: 0)
        }
        let currentSuccess = successRates[url]!
        successRates[url] = SuccessRate(success: currentSuccess.success + (success ? 1 : 0), total: currentSuccess.total + 1)
        
        // Track cache performance
        if cacheHitRates[url] == nil {
            cacheHitRates[url] = CacheRate(hits: 0, misses: 0)
        }
        let currentCache = cacheHitRates[url]!
        if cacheHit {
            cacheHitRates[url] = CacheRate(hits: currentCache.hits + 1, misses: currentCache.misses)
        } else {
            cacheHitRates[url] = CacheRate(hits: currentCache.hits, misses: currentCache.misses + 1)
        }
        
        // Log performance issues
        if loadTime > performanceThreshold {
            print("⚠️  Slow image load: \(url) took \(String(format: "%.2f", loadTime))s")
        }
        
        // Save data periodically
        if shouldSaveData() {
            savePerformanceData()
        }
    }
    
    /// Get performance statistics for a specific URL
    func getPerformanceStats(for url: String) -> ImagePerformanceStats? {
        guard let times = loadTimes[url], !times.isEmpty else { return nil }
        
        let avgLoadTime = times.reduce(0, +) / Double(times.count)
        let minLoadTime = times.min() ?? 0
        let maxLoadTime = times.max() ?? 0
        
        let successRate = successRates[url]
        let cacheRate = cacheHitRates[url]
        
        let successRateValue = successRate?.total ?? 0 > 0 ? Double(successRate?.success ?? 0) / Double(successRate?.total ?? 1) : 0
        let cacheHitRateValue = (cacheRate?.hits ?? 0) + (cacheRate?.misses ?? 0) > 0 ? Double(cacheRate?.hits ?? 0) / Double((cacheRate?.hits ?? 0) + (cacheRate?.misses ?? 1)) : 0
        
        return ImagePerformanceStats(
            url: url,
            averageLoadTime: avgLoadTime,
            minLoadTime: minLoadTime,
            maxLoadTime: maxLoadTime,
            totalLoads: times.count,
            successRate: successRateValue,
            cacheHitRate: cacheHitRateValue
        )
    }
    
    /// Get overall performance statistics
    func getOverallPerformanceStats() -> OverallPerformanceStats {
        let allTimes = loadTimes.values.flatMap { $0 }
        let avgLoadTime = allTimes.isEmpty ? 0 : allTimes.reduce(0, +) / Double(allTimes.count)
        
        let totalSuccess = successRates.values.reduce(0) { $0 + $1.success }
        let totalRequests = successRates.values.reduce(0) { $0 + $1.total }
        let overallSuccessRate = totalRequests > 0 ? Double(totalSuccess) / Double(totalRequests) : 0
        
        let totalCacheHits = cacheHitRates.values.reduce(0) { $0 + $1.hits }
        let totalCacheRequests = cacheHitRates.values.reduce(0) { $0 + $1.hits + $1.misses }
        let overallCacheHitRate = totalCacheRequests > 0 ? Double(totalCacheHits) / Double(totalCacheRequests) : 0
        
        let slowLoads = allTimes.filter { $0 > performanceThreshold }.count
        let slowLoadRate = allTimes.isEmpty ? 0 : Double(slowLoads) / Double(allTimes.count)
        
        return OverallPerformanceStats(
            averageLoadTime: avgLoadTime,
            totalImages: loadTimes.count,
            totalLoads: allTimes.count,
            overallSuccessRate: overallSuccessRate,
            overallCacheHitRate: overallCacheHitRate,
            slowLoadRate: slowLoadRate,
            performanceGrade: getPerformanceGrade(avgLoadTime: avgLoadTime, successRate: overallSuccessRate)
        )
    }
    
    /// Get slowest loading images
    func getSlowestImages(limit: Int = 10) -> [ImagePerformanceStats] {
        let stats = loadTimes.keys.compactMap { getPerformanceStats(for: $0) }
        return stats.sorted { $0.averageLoadTime > $1.averageLoadTime }.prefix(limit).map { $0 }
    }
    
    /// Get images with lowest success rates
    func getProblematicImages(limit: Int = 10) -> [ImagePerformanceStats] {
        let stats = loadTimes.keys.compactMap { getPerformanceStats(for: $0) }
        return stats.sorted { $0.successRate < $1.successRate }.prefix(limit).map { $0 }
    }
    
    /// Clear performance data
    func clearPerformanceData() {
        loadTimes.removeAll()
        successRates.removeAll()
        cacheHitRates.removeAll()
        savePerformanceData()
    }
    
    /// Generate performance report
    func generatePerformanceReport() -> String {
        let overall = getOverallPerformanceStats()
        let slowest = getSlowestImages(limit: 5)
        let problematic = getProblematicImages(limit: 5)
        
        var report = "📊 Image Performance Report\n"
        report += "=" * 50 + "\n\n"
        
        report += "Overall Performance:\n"
        report += "  Average Load Time: \(String(format: "%.2f", overall.averageLoadTime))s\n"
        report += "  Success Rate: \(String(format: "%.1f", overall.overallSuccessRate * 100))%\n"
        report += "  Cache Hit Rate: \(String(format: "%.1f", overall.overallCacheHitRate * 100))%\n"
        report += "  Performance Grade: \(overall.performanceGrade)\n"
        report += "  Total Images: \(overall.totalImages)\n"
        report += "  Total Loads: \(overall.totalLoads)\n\n"
        
        if !slowest.isEmpty {
            report += "Slowest Loading Images:\n"
            for (index, stat) in slowest.enumerated() {
                report += "  \(index + 1). \(stat.url)\n"
                report += "     Average: \(String(format: "%.2f", stat.averageLoadTime))s\n"
                report += "     Success Rate: \(String(format: "%.1f", stat.successRate * 100))%\n"
            }
            report += "\n"
        }
        
        if !problematic.isEmpty {
            report += "Problematic Images (Low Success Rate):\n"
            for (index, stat) in problematic.enumerated() {
                report += "  \(index + 1). \(stat.url)\n"
                report += "     Success Rate: \(String(format: "%.1f", stat.successRate * 100))%\n"
                report += "     Average Load Time: \(String(format: "%.2f", stat.averageLoadTime))s\n"
            }
        }
        
        return report
    }
    
    // MARK: - Private Methods
    
    private func shouldSaveData() -> Bool {
        let totalRequests = successRates.values.reduce(0) { $0 + $1.total }
        return totalRequests % 50 == 0 // Save every 50 requests
    }
    
    private func savePerformanceData() {
        // Save to UserDefaults for persistence
        if let data = try? JSONEncoder().encode(loadTimes) {
            UserDefaults.standard.set(data, forKey: "ImageLoadTimes")
        }
        
        if let data = try? JSONEncoder().encode(successRates) {
            UserDefaults.standard.set(data, forKey: "ImageSuccessRates")
        }
        
        if let data = try? JSONEncoder().encode(cacheHitRates) {
            UserDefaults.standard.set(data, forKey: "ImageCacheHitRates")
        }
    }
    
    private func loadPerformanceData() {
        // Load from UserDefaults
        if let data = UserDefaults.standard.data(forKey: "ImageLoadTimes"),
           let times = try? JSONDecoder().decode([String: [TimeInterval]].self, from: data) {
            loadTimes = times
        }
        
        if let data = UserDefaults.standard.data(forKey: "ImageSuccessRates"),
           let rates = try? JSONDecoder().decode([String: SuccessRate].self, from: data) {
            successRates = rates
        }
        
        if let data = UserDefaults.standard.data(forKey: "ImageCacheHitRates"),
           let rates = try? JSONDecoder().decode([String: CacheRate].self, from: data) {
            cacheHitRates = rates
        }
    }
    
    private func getPerformanceGrade(avgLoadTime: TimeInterval, successRate: Double) -> String {
        if avgLoadTime < 0.5 && successRate > 0.95 {
            return "A+"
        } else if avgLoadTime < 1.0 && successRate > 0.90 {
            return "A"
        } else if avgLoadTime < 1.5 && successRate > 0.85 {
            return "B"
        } else if avgLoadTime < 2.0 && successRate > 0.80 {
            return "C"
        } else {
            return "D"
        }
    }
}

// MARK: - Performance Statistics

struct SuccessRate: Codable {
    let success: Int
    let total: Int
}

struct CacheRate: Codable {
    let hits: Int
    let misses: Int
}

struct ImagePerformanceStats {
    let url: String
    let averageLoadTime: TimeInterval
    let minLoadTime: TimeInterval
    let maxLoadTime: TimeInterval
    let totalLoads: Int
    let successRate: Double
    let cacheHitRate: Double
}

struct OverallPerformanceStats {
    let averageLoadTime: TimeInterval
    let totalImages: Int
    let totalLoads: Int
    let overallSuccessRate: Double
    let overallCacheHitRate: Double
    let slowLoadRate: Double
    let performanceGrade: String
}

// MARK: - Extensions

extension String {
    static func * (left: String, right: Int) -> String {
        return String(repeating: left, count: right)
    }
} 