import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.black.edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 20) {
                    // Profile Image
                    Image(systemName: "person.circle.fill")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 100, height: 100)
                        .foregroundColor(.gray)
                    
                    // User Info
                    Text(authViewModel.currentUser?.email ?? "Guest")
                        .font(.title2)
                        .foregroundColor(.white)
                    
                    // Sign Out Button
                    Button(action: {
                        authViewModel.signOut()
                    }) {
                        Text("Sign Out")
                            .foregroundColor(.white)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(Color.pecanRed)
                            .cornerRadius(8)
                    }
                    .padding(.horizontal)
                }
                .padding()
            }
            .navigationTitle("Profile")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview {
    ProfileView()
        .environmentObject(AuthViewModel())
} 