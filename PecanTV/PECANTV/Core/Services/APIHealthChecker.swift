import Foundation

class APIHealthChecker {
    func checkHealth() {
        guard let url = URL(string: "https://77b9-192-69-240-171.ngrok-free.app/health") else {
            print("Invalid URL")
            return
        }

        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                print("Error: \(error.localizedDescription)")
                return
            }

            if let data = data {
                do {
                    let json = try JSONSerialization.jsonObject(with: data, options: [])
                    if let dict = json as? [String: Any] {
                        if let status = dict["status"] as? String {
                            print("Health check status: \(status)")
                        }
                    }
                } catch {
                    print("Error parsing JSON: \(error.localizedDescription)")
                }
            }
        }

        task.resume()
    }
} 