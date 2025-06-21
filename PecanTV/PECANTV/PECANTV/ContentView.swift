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
    @StateObject private var authViewModel = AuthViewModel()
    @StateObject private var contentViewModel = ContentViewModel()
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .environmentObject(contentViewModel)
                .tabItem {
                    Label("Home", systemImage: "house")
                }
                .tag(0)
            
            FavoritesView(allContent: contentViewModel.films + contentViewModel.tvSeries)
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
        .onAppear {
            // Set up authentication success callback
            authViewModel.onAuthenticationSuccess = {
                print("🎉 Authentication successful, loading content...")
                contentViewModel.loadContent()
            }
        }
    }
}

#Preview {
    ContentView()
}
