import SwiftUI

struct ContentView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @State private var showSplash = false
    @State private var splashActive = true
    
    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                if splashActive {
                    SplashScreenView(isActive: $splashActive)
                } else {
                    MainTabView()
                }
            } else {
                AuthenticationView()
            }
        }
        .onChange(of: authViewModel.isAuthenticated) { isAuthenticated in
            if isAuthenticated {
                splashActive = true
            }
        }
    }
}

struct MainTabView: View {
    var body: some View {
        TabView {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
            
            SearchView()
                .tabItem {
                    Label("Search", systemImage: "magnifyingglass")
                }
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person.fill")
                }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AuthViewModel())
} 