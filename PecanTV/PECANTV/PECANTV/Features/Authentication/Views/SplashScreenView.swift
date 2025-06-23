import SwiftUI

struct SplashScreenView: View {
    @State private var isActive = false
    @State private var size = 0.8
    @State private var opacity = 0.5
    @StateObject private var authViewModel = AuthViewModel()
    @StateObject private var contentViewModel = ContentViewModel()
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
                
                VStack {
                    Image("pecantv_logo")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 200, height: 200)
                        .scaleEffect(size)
                        .opacity(opacity)
                        .onAppear {
                            withAnimation(.easeIn(duration: 1.2)) {
                                self.size = 1.0
                                self.opacity = 1.0
                            }
                        }
                }
                .onAppear {
                    // Check API health during splash screen
                    healthChecker.checkAPIHealth()
                    
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                        withAnimation {
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
} 