import SwiftUI

struct GoogleDriveTestView: View {
    @State private var imageTestResult: String = ""
    @State private var trailerTestResult: String = ""
    @State private var isTesting = false
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Google Drive Access Test")
                .font(.title)
                .padding()
            
            VStack(alignment: .leading, spacing: 10) {
                Text("Test Image Access")
                    .font(.headline)
                
                Button(action: testImageAccess) {
                    Text("Test Image")
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(8)
                }
                .disabled(isTesting)
                
                Text(imageTestResult)
                    .foregroundColor(imageTestResult.contains("Success") ? .green : .red)
            }
            .padding()
            
            VStack(alignment: .leading, spacing: 10) {
                Text("Test Trailer Access")
                    .font(.headline)
                
                Button(action: testTrailerAccess) {
                    Text("Test Trailer")
                        .foregroundColor(.white)
                        .padding()
                        .background(Color.blue)
                        .cornerRadius(8)
                }
                .disabled(isTesting)
                
                Text(trailerTestResult)
                    .foregroundColor(trailerTestResult.contains("Success") ? .green : .red)
            }
            .padding()
        }
        .padding()
    }
    
    private func testImageAccess() {
        isTesting = true
        imageTestResult = "Testing..."
        
        guard let url = GoogleDriveConfig.getTitleImageURL(for: "getchristielove") else {
            imageTestResult = "Error: Invalid URL"
            isTesting = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    imageTestResult = "Error: \(error.localizedDescription)"
                } else if let httpResponse = response as? HTTPURLResponse {
                    if httpResponse.statusCode == 200 {
                        imageTestResult = "Success: Image accessible"
                    } else {
                        imageTestResult = "Error: HTTP \(httpResponse.statusCode)"
                    }
                }
                isTesting = false
            }
        }.resume()
    }
    
    private func testTrailerAccess() {
        isTesting = true
        trailerTestResult = "Testing..."
        
        guard let url = GoogleDriveConfig.getTrailerURL(for: "getchristielove") else {
            trailerTestResult = "Error: Invalid URL"
            isTesting = false
            return
        }
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            DispatchQueue.main.async {
                if let error = error {
                    trailerTestResult = "Error: \(error.localizedDescription)"
                } else if let httpResponse = response as? HTTPURLResponse {
                    if httpResponse.statusCode == 200 {
                        trailerTestResult = "Success: Trailer accessible"
                    } else {
                        trailerTestResult = "Error: HTTP \(httpResponse.statusCode)"
                    }
                }
                isTesting = false
            }
        }.resume()
    }
}

#Preview {
    GoogleDriveTestView()
} 