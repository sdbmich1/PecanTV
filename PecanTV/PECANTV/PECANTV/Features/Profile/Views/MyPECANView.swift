import SwiftUI

struct MyPECANView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                if let user = authViewModel.currentUser {
                    Image("pecantv_logo")
                        .resizable()
                        .scaledToFit()
                        .frame(width: 200, height: 100)
                        .padding(.top, 50)
                    
                    VStack(spacing: 16) {
                        Text("Welcome, \(user.firstName)!")
                            .font(.title)
                            .fontWeight(.bold)
                        
                        Text("You're now part of the PECAN TV community")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .padding()
                    
                    VStack(spacing: 12) {
                        Text("Your Profile")
                            .font(.headline)
                            .padding(.top)
                        
                        HStack {
                            Text("Name:")
                                .foregroundColor(.secondary)
                            Text("\(user.firstName) \(user.lastName)")
                        }
                        
                        HStack {
                            Text("Email:")
                                .foregroundColor(.secondary)
                            Text(user.email)
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(10)
                    .padding(.horizontal)
                    
                    Spacer()
                    
                    Button {
                        authViewModel.signOut()
                    } label: {
                        Text("Sign Out")
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.pecanRed)
                            .cornerRadius(10)
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 30)
                } else {
                    ProgressView("Loading profile...")
                }
            }
            .navigationTitle("My PECAN")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview {
    MyPECANView()
        .environmentObject(AuthViewModel())
} 