//
//  ContentView.swift
//  PECANTV
//
//  Created by Sean Brown on 5/20/25.
//

import SwiftUI
import SwiftData
import FirebaseCore
import FirebaseAuth
import AVKit
import AVFoundation

struct ContentView: View {
    @StateObject private var authViewModel = AuthViewModel()
    @State private var selectedTab = 0
    @State private var showAuth = false
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var isInitialized = false
    @StateObject private var homeViewModel = HomeViewModel()
    @State private var selectedContent: MediaContent?
    @State private var isPlayerPresented = false
    @State private var isTrailerPresented = false
    @State private var player: AVPlayer?
    @State private var isLoading = true
    @State private var error: Error?
    
    // MARK: - Content Data
    private let trendingContent: [MediaContent] = [
        MediaContent(
            id: 1,
            title: "Get Christie Love",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/getchristielove-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/getchristielove_trailer-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/getchristielove.mp4",
            description: "A groundbreaking crime drama series following the adventures of Christie Love, a stylish and intelligent undercover police detective in Los Angeles.",
            type: "SERIES",
            runtime: 60,
            genre: "Crime",
            ageRating: "TV-14"
        ),
        MediaContent(
            id: 2,
            title: "The Jeffersons",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/thejeffersons-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/thejeffersons_trailer-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/thejeffersons.mp4",
            description: "A classic sitcom about a successful African-American family who moves from Queens to Manhattan's Upper East Side.",
            type: "SERIES",
            runtime: 30,
            genre: "Comedy",
            ageRating: "TV-PG"
        ),
        MediaContent(
            id: 3,
            title: "Good Times",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/goodtimes-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/goodtimes_trailer-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/goodtimes.mp4",
            description: "A sitcom about a working-class African-American family living in a Chicago housing project.",
            type: "SERIES",
            runtime: 30,
            genre: "Comedy",
            ageRating: "TV-PG"
        ),
        MediaContent(
            id: 4,
            title: "Sanford and Son",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/sanfordandson-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/sanfordandson_trailer-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/sanfordandson.mp4",
            description: "A comedy series about a widowed junk dealer and his son living in the Watts neighborhood of Los Angeles.",
            type: "SERIES",
            runtime: 30,
            genre: "Comedy",
            ageRating: "TV-PG"
        ),
        MediaContent(
            id: 5,
            title: "What's Happening!!",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/whatshappening-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/whatshappening_trailer-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/whatshappening.mp4",
            description: "A sitcom about three high school friends and their misadventures in Los Angeles.",
            type: "SERIES",
            runtime: 30,
            genre: "Comedy",
            ageRating: "TV-PG"
        )
    ]
    
    private let continueWatchingContent: [MediaContent] = [
        MediaContent(
            id: 6,
            title: "The Jeffersons",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/thejeffersons-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/thejeffersons_trailer-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/thejeffersons.mp4",
            description: "A classic sitcom about a successful African-American family who moves from Queens to Manhattan's Upper East Side.",
            type: "SERIES",
            runtime: 30,
            genre: "Comedy",
            ageRating: "TV-PG"
        ),
        MediaContent(
            id: 7,
            title: "Good Times",
            posterURL: "https://storage.googleapis.com/pecantv_title_images/goodtimes-Feature-Img-16x9.png",
            trailerURL: "https://storage.googleapis.com/pecantv_trailers/goodtimes_trailer-60s.mp4",
            contentURL: "https://storage.googleapis.com/pecantv_content/goodtimes.mp4",
            description: "A sitcom about a working-class African-American family living in a Chicago housing project.",
            type: "SERIES",
            runtime: 30,
            genre: "Comedy",
            ageRating: "TV-PG"
        )
    ]
    
    var body: some View {
        Group {
            if !isInitialized {
                // Initial loading screen
                VStack {
                    Image("pecantv_logo")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 200, height: 200)
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle())
                        .scaleEffect(1.5)
                        .padding(.top, 20)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.black)
                .onAppear {
                    // Initialize app state
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
                        isInitialized = true
                    }
                }
            } else {
                // Main app content
                TabView(selection: $selectedTab) {
                    HomeView()
                        .tabItem {
                            Label("Home", systemImage: "house")
                        }
                        .tag(0)
                    
                    Text("My Favs")
                        .tabItem {
                            Label("My Favs", systemImage: "heart")
                        }
                        .tag(1)
                    
                    MyPecanView()
                        .tabItem {
                            Label("My PECAN", systemImage: "person")
                        }
                        .tag(2)
                }
                .overlay {
                    if !authViewModel.isAuthenticated {
                        Color.black.opacity(0.9)
                            .edgesIgnoringSafeArea(.all)
                            .overlay {
                                VStack {
                                    Image("pecantv_logo")
                                        .resizable()
                                        .scaledToFit()
                                        .frame(width: 200, height: 200)
                                        .padding(.bottom, 40)
                                    
                                    Text("Welcome to PECAN TV")
                                        .font(.title)
                                        .fontWeight(.bold)
                                        .foregroundColor(.white)
                                        .padding(.bottom, 20)
                                    
                                    Button(action: {
                                        showAuth = true
                                    }) {
                                        Text("Sign In / Sign Up")
                                            .font(.headline)
                                            .foregroundColor(.white)
                                            .frame(maxWidth: .infinity)
                                            .padding()
                                            .background(Color.blue)
                                            .cornerRadius(10)
                                    }
                                    .padding(.horizontal, 40)
                                }
                            }
                    }
                }
            }
        }
        .sheet(isPresented: $showAuth) {
            AuthenticationView()
        }
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
        }
        .onReceive(authViewModel.$error) { error in
            if let error = error {
                errorMessage = error.localizedDescription
                showError = true
            }
        }
    }
}

struct AuthenticationView: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var authViewModel = AuthViewModel()
    @State private var email = ""
    @State private var password = ""
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var isSignUp = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    var body: some View {
        NavigationView {
            Form {
                Section {
                    TextField("Email", text: $email)
                        .textContentType(.emailAddress)
                        .autocapitalization(.none)
                    
                    SecureField("Password", text: $password)
                        .textContentType(isSignUp ? .newPassword : .password)
                    
                    if isSignUp {
                        TextField("First Name", text: $firstName)
                            .textContentType(.givenName)
                        
                        TextField("Last Name", text: $lastName)
                            .textContentType(.familyName)
                    }
                }
                
                Section {
                    Button(action: {
                        Task {
                            if isSignUp {
                                await authViewModel.signUp(
                                    email: email,
                                    password: password,
                                    firstName: firstName,
                                    lastName: lastName
                                )
                            } else {
                                await authViewModel.signIn(
                                    email: email,
                                    password: password
                                )
                            }
                        }
                    }) {
                        if authViewModel.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle())
                        } else {
                            Text(isSignUp ? "Sign Up" : "Sign In")
                        }
                    }
                    .disabled(authViewModel.isLoading)
                    
                    Button(action: {
                        isSignUp.toggle()
                    }) {
                        Text(isSignUp ? "Already have an account? Sign In" : "Don't have an account? Sign Up")
                    }
                }
            }
            .navigationTitle(isSignUp ? "Sign Up" : "Sign In")
            .navigationBarItems(trailing: Button("Cancel") {
                dismiss()
            })
            .alert("Error", isPresented: $showError) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(errorMessage)
            }
            .onReceive(authViewModel.$error) { error in
                if let error = error {
                    errorMessage = error.localizedDescription
                    showError = true
                }
            }
        }
    }
}

struct MyFavsView: View {
    var body: some View {
        VStack {
            Text("My Favorites")
                .font(.largeTitle)
                .padding()
            Text("Your favorite movies and shows will appear here.")
                .foregroundColor(.gray)
            Spacer()
        }
        .navigationTitle("My Favs")
    }
}

struct MainTabView: View {
    @StateObject private var contentViewModel = ContentViewModel()
    @EnvironmentObject private var authViewModel: AuthViewModel
    
    var body: some View {
        TabView {
            NavigationView {
                HomeView()
                    .environmentObject(contentViewModel)
            }
            .tabItem {
                Label("Home", systemImage: "house.fill")
            }
            
            NavigationView {
                MyFavsView()
            }
            .tabItem {
                Label("My Favs", systemImage: "star.fill")
            }
            
            NavigationView {
                MyPECANView()
                    .environmentObject(authViewModel)
            }
            .tabItem {
                Label("My PECAN", systemImage: "person.crop.circle")
            }
        }
    }
}

struct ContentCarouselView: View {
    let title: String
    let contents: [MediaContent]
    @Binding var selectedContent: MediaContent?
    @Binding var showDetail: Bool
    @State private var imageLoadErrors: [String: Error] = [:]
    
    var body: some View {
        VStack(alignment: .leading) {
            Text(title)
                .font(.title2)
                .fontWeight(.bold)
                .padding(.horizontal)
            
            ScrollView(.horizontal, showsIndicators: false) {
                LazyHStack(spacing: 16) {
                    ForEach(contents) { content in
                        Button {
                            selectedContent = content
                            showDetail = true
                        } label: {
                            VStack(alignment: .leading) {
                                if let error = imageLoadErrors[content.posterURL] {
                                    // Show error state
                                    VStack {
                                        Image(systemName: "exclamationmark.triangle")
                                            .font(.largeTitle)
                                            .foregroundColor(.gray)
                                        Text("Image failed to load")
                                            .font(.caption)
                                            .foregroundColor(.gray)
                                    }
                                    .frame(width: 160, height: 240)
                                    .background(Color.gray.opacity(0.2))
                                    .cornerRadius(8)
                                } else {
                                    AsyncImage(url: URL(string: content.posterURL)) { phase in
                                        switch phase {
                                        case .empty:
                                            ProgressView()
                                                .frame(width: 160, height: 240)
                                        case .success(let image):
                                            image
                                                .resizable()
                                                .aspectRatio(contentMode: .fill)
                                                .frame(width: 160, height: 240)
                                                .clipped()
                                                .cornerRadius(8)
                                        case .failure(let error):
                                            VStack {
                                                Image(systemName: "exclamationmark.triangle")
                                                    .font(.largeTitle)
                                                    .foregroundColor(.gray)
                                                Text("Image failed to load")
                                                    .font(.caption)
                                                    .foregroundColor(.gray)
                                            }
                                            .frame(width: 160, height: 240)
                                            .background(Color.gray.opacity(0.2))
                                            .cornerRadius(8)
                                            .onAppear {
                                                imageLoadErrors[content.posterURL] = error
                                                print("Failed to load image for \(content.title): \(error.localizedDescription)")
                                            }
                                        @unknown default:
                                            EmptyView()
                                        }
                                    }
                                }
                                
                                Text(content.title)
                                    .font(.subheadline)
                                    .lineLimit(2)
                                    .frame(width: 160, alignment: .leading)
                            }
                        }
                    }
                }
                .padding(.horizontal)
            }
        }
    }
}

#Preview {
    ContentView()
}
