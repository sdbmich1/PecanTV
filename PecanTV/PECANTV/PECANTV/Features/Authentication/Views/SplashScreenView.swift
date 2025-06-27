import SwiftUI

struct SplashScreenView: View {
    @State private var isActive = false
    @State private var size = 0.8
    @State private var opacity = 0.5
    @State private var logoLoaded = false
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
                        withAnimation(.easeIn(duration: 1.5)) {
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
                    // Check API health during splash screen
                    healthChecker.checkAPIHealth()
                    
                    // Show splash screen for at least 3 seconds
                    DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
                        withAnimation(.easeOut(duration: 0.5)) {
                            self.isActive = true
                        }
                    }
                }
            }
        }
    }
}

#Preview {
    SplashScreenView()
        .environmentObject(AuthViewModel())
        .environmentObject(ContentViewModel())
} 