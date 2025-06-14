import SwiftUI

struct ProfileView: View {
    @State private var isLoggedIn = false
    @State private var username = ""
    @State private var email = ""
    
    var body: some View {
        NavigationView {
            if isLoggedIn {
                ScrollView {
                    VStack(spacing: 20) {
                        // Profile Header
                        VStack(spacing: 16) {
                            Image(systemName: "person.circle.fill")
                                .font(.system(size: 80))
                                .foregroundColor(.blue)
                            
                            Text(username)
                                .font(.title2)
                                .fontWeight(.bold)
                            
                            Text(email)
                                .font(.subheadline)
                                .foregroundColor(.gray)
                        }
                        .padding()
                        
                        // Account Settings
                        VStack(alignment: .leading, spacing: 16) {
                            Text("Account Settings")
                                .font(.headline)
                                .padding(.horizontal)
                            
                            Button(action: {
                                // Handle edit profile
                            }) {
                                HStack {
                                    Image(systemName: "person.fill")
                                    Text("Edit Profile")
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                }
                                .foregroundColor(.primary)
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(10)
                            }
                            
                            Button(action: {
                                // Handle notifications
                            }) {
                                HStack {
                                    Image(systemName: "bell.fill")
                                    Text("Notifications")
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                }
                                .foregroundColor(.primary)
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(10)
                            }
                            
                            Button(action: {
                                // Handle privacy
                            }) {
                                HStack {
                                    Image(systemName: "lock.fill")
                                    Text("Privacy")
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                }
                                .foregroundColor(.primary)
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(10)
                            }
                        }
                        .padding(.horizontal)
                        
                        // Sign Out Button
                        Button(action: {
                            isLoggedIn = false
                        }) {
                            Text("Sign Out")
                                .foregroundColor(.red)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color(.systemGray6))
                                .cornerRadius(10)
                        }
                        .padding(.horizontal)
                    }
                    .padding(.vertical)
                }
                .navigationTitle("Profile")
                .navigationBarTitleDisplayMode(.inline)
            } else {
                VStack(spacing: 20) {
                    Image(systemName: "person.circle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.blue)
                    
                    Text("Welcome to PecanTV")
                        .font(.title2)
                        .fontWeight(.bold)
                    
                    Text("Sign in to access your profile and watch history")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                    
                    Button(action: {
                        // Handle sign in
                        isLoggedIn = true
                        username = "John Doe"
                        email = "john.doe@example.com"
                    }) {
                        Text("Sign In")
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                }
                .padding()
                .navigationTitle("Profile")
                .navigationBarTitleDisplayMode(.inline)
            }
        }
    }
}

#Preview {
    ProfileView()
} 