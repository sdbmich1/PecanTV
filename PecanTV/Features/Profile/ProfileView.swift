import SwiftUI

struct ProfileView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    
    var body: some View {
        NavigationView {
            List {
                if let user = authViewModel.currentUser {
                    Section {
                        HStack {
                            if let imageURL = user.profileImageURL {
                                AsyncImage(url: imageURL) { image in
                                    image
                                        .resizable()
                                        .aspectRatio(contentMode: .fill)
                                } placeholder: {
                                    Circle()
                                        .fill(Color.gray.opacity(0.3))
                                }
                                .frame(width: 60, height: 60)
                                .clipShape(Circle())
                            } else {
                                Image(systemName: "person.circle.fill")
                                    .resizable()
                                    .frame(width: 60, height: 60)
                                    .foregroundColor(.gray)
                            }
                            
                            VStack(alignment: .leading) {
                                Text(user.displayName ?? user.email)
                                    .font(.headline)
                                Text(user.email)
                                    .font(.subheadline)
                                    .foregroundColor(.gray)
                            }
                        }
                        .padding(.vertical, 8)
                    }
                    
                    Section("Watchlist") {
                        if user.watchlist.isEmpty {
                            Text("Your watchlist is empty")
                                .foregroundColor(.gray)
                        } else {
                            ForEach(user.watchlist, id: \.self) { contentId in
                                Text(contentId) // Replace with actual content title
                            }
                        }
                    }
                    
                    Section("Watch History") {
                        if user.watchHistory.isEmpty {
                            Text("No watch history")
                                .foregroundColor(.gray)
                        } else {
                            ForEach(user.watchHistory, id: \.self) { contentId in
                                Text(contentId) // Replace with actual content title
                            }
                        }
                    }
                }
                
                Section {
                    Button(role: .destructive, action: {
                        authViewModel.signOut()
                    }) {
                        HStack {
                            Text("Sign Out")
                            Spacer()
                            Image(systemName: "arrow.right.square")
                        }
                    }
                }
            }
            .navigationTitle("Profile")
        }
    }
}

#Preview {
    ProfileView()
        .environmentObject(AuthViewModel())
} 