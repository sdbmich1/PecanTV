//
//  ContentView.swift
//  PECANTV
//
//  Created by Sean Brown on 5/20/25.
//

import SwiftUI
// import FirebaseCore
// import FirebaseAuth

struct ContentView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @EnvironmentObject private var contentViewModel: ContentViewModel
    @StateObject private var favoritesManager = FavoritesManager()
    @StateObject private var healthChecker = APIHealthChecker.shared
    @State private var selectedTab = 0
    @State private var showAPIErrorAlert = false
    
    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                TabView(selection: $selectedTab) {
                    HomeView()
                        .tabItem {
                            Label("Home", systemImage: "house")
                        }
                        .tag(0)
                    
                    FavoritesView(allContent: contentViewModel.films + contentViewModel.tvSeries)
                        .environmentObject(favoritesManager)
                        .tabItem {
                            Label("My Favs", systemImage: "heart")
                        }
                        .tag(1)
                    
                    ProfileView()
                        .tabItem {
                            Label("My PECAN", systemImage: "person")
                        }
                        .tag(2)
                }
            } else if !healthChecker.isAPIAvailable {
                VStack(spacing: 20) {
                    Image(systemName: "wifi.slash")
                        .font(.system(size: 60))
                        .foregroundColor(.red)
                    
                    Text("Server Unavailable")
                        .font(.title)
                        .fontWeight(.bold)
                    
                    Text("Unable to connect to PecanTV server. Please check your connection and try again.")
                        .multilineTextAlignment(.center)
                        .foregroundColor(.secondary)
                        .padding(.horizontal)
                    
                    Button("Retry Connection") {
                        healthChecker.checkAPIHealth()
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding()
            } else {
                SignInView()
                    .environmentObject(authViewModel)
            }
        }
        .onAppear {
            // Check API health on app launch
            healthChecker.checkAPIHealth { isAvailable in
                if isAvailable {
                    // Set up authentication success callback
                    authViewModel.onAuthenticationSuccess = {
                        print("🎉 Authentication successful, loading content...")
                        contentViewModel.loadContent()
                    }
                }
            }
        }
        .onChange(of: healthChecker.isAPIAvailable) { isAvailable in
            if !isAvailable {
                showAPIErrorAlert = true
            }
        }
        .alert("Server Unavailable", isPresented: $showAPIErrorAlert) {
            Button("Retry") {
                healthChecker.checkAPIHealth()
            }
            Button("Cancel", role: .cancel) { }
        } message: {
            Text("The PecanTV server is currently unavailable. Please check your connection or try again later.")
        }
    }
}

#Preview {
    ContentView()
}
