import SwiftUI

struct SplashScreenView: View {
    @State private var isActive = false
    @State private var size = 0.8
    @State private var opacity = 0.5
    @State private var logoLoaded = false
    @State private var apiCheckComplete = false
    @EnvironmentObject private var authViewModel: AuthViewModel
    @EnvironmentObject private var contentViewModel: ContentViewModel
    @StateObject private var healthChecker = APIHealthChecker.shared
    
    var body: some View {
        if isActive {
            if authViewModel.isAuthenticated {
                ContentView()
                    .environmentObject(authViewModel)
                    .environmentObject(contentViewModel)
                    .environmentObject(healthChecker)
            } else {
                SignInView()
                    .environmentObject(authViewModel)
                    .environmentObject(healthChecker)
            }
        } else {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 20) {
                    // Logo with fallback
                    Group {
                        if logoLoaded {
                            Image("pecantv_logo")
                                .resizable()
                                .scaledToFit()
                                .frame(width: 250, height: 125)
                                .scaleEffect(size)
                                .opacity(opacity)
                        } else {
                            // Fallback text if logo doesn't load
                            Text("PECAN TV")
                                .font(.system(size: 48, weight: .bold, design: .rounded))
                                .foregroundColor(.white)
                                .scaleEffect(size)
                                .opacity(opacity)
                        }
                    }
                    .onAppear {
                        // Try to load the logo
                        logoLoaded = true
                        
                        // Animate the logo
                        withAnimation(.easeIn(duration: 0.8)) {
                            self.size = 1.0
                            self.opacity = 1.0
                        }
                    }
                    
                    // Loading indicator
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        .scaleEffect(1.2)
                        .opacity(opacity)
                }
                .onAppear {
                    print("🚀 SplashScreen: Starting initialization...")
                    
                    // Check API health during splash screen
                    Task {
                        await healthChecker.checkAPIHealth()
                        await MainActor.run {
                            apiCheckComplete = true
                            print("✅ SplashScreen: API health check complete")
                            checkReadyToProceed()
                        }
                    }
                    
                    // Show splash screen for minimum 1.5 seconds (reduced from 3.0)
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                        print("⏰ SplashScreen: Minimum display time reached")
                        checkReadyToProceed()
                    }
                }
            }
        }
    }
    
    private func checkReadyToProceed() {
        // Only proceed if both minimum time has passed AND API check is complete
        guard apiCheckComplete else {
            print("⏳ SplashScreen: Waiting for API check to complete...")
            return
        }
        
        // Add a small delay to ensure smooth transition
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.2) {
            print("✅ SplashScreen: Proceeding to main app")
            withAnimation(.easeOut(duration: 0.3)) {
                self.isActive = true
            }
        }
    }
}

#Preview {
    SplashScreenView()
        .environmentObject(AuthViewModel())
        .environmentObject(ContentViewModel())
} 