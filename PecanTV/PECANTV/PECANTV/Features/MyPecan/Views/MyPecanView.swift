import SwiftUI

struct MyPecanView: View {
    @EnvironmentObject private var authViewModel: AuthViewModel
    @State private var showEditProfile = false
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var email = ""
    
    var body: some View {
        NavigationView {
            List {
                Section(header: Text("Account")) {
                    if let user = authViewModel.currentUser {
                        HStack {
                            Text("Name")
                            Spacer()
                            Text(user.fullName)
                                .foregroundColor(.gray)
                        }
                        
                        HStack {
                            Text("Email")
                            Spacer()
                            Text(user.email)
                                .foregroundColor(.gray)
                        }
                        
                        Button(action: {
                            // Load current user data
                            firstName = user.firstName
                            lastName = user.lastName
                            email = user.email
                            showEditProfile = true
                        }) {
                            Text("Edit Profile")
                                .foregroundColor(.blue)
                        }
                        
                        Button(action: {
                            authViewModel.signOut()
                        }) {
                            Text("Sign Out")
                                .foregroundColor(.pecanRed)
                        }
                    }
                }
                
                Section(header: Text("Preferences")) {
                    NavigationLink(destination: Text("Watch History")) {
                        Label("Watch History", systemImage: "clock")
                    }
                    
                    NavigationLink(destination: Text("Downloads")) {
                        Label("Downloads", systemImage: "arrow.down.circle")
                    }
                    
                    NavigationLink(destination: Text("Notifications")) {
                        Label("Notifications", systemImage: "bell")
                    }
                }
                
                Section(header: Text("Support")) {
                    NavigationLink(destination: Text("Help Center")) {
                        Label("Help Center", systemImage: "questionmark.circle")
                    }
                    
                    NavigationLink(destination: Text("Contact Us")) {
                        Label("Contact Us", systemImage: "envelope")
                    }
                    
                    NavigationLink(destination: Text("About")) {
                        Label("About", systemImage: "info.circle")
                    }
                }
            }
            .navigationTitle("My PECAN")
            .sheet(isPresented: $showEditProfile) {
                NavigationView {
                    Form {
                        Section(header: Text("Personal Information")) {
                            HStack {
                                Text("First Name")
                                    .frame(width: 100, alignment: .leading)
                                TextField("Enter first name", text: $firstName)
                            }
                            
                            HStack {
                                Text("Last Name")
                                    .frame(width: 100, alignment: .leading)
                                TextField("Enter last name", text: $lastName)
                            }
                            
                            HStack {
                                Text("Email")
                                    .frame(width: 100, alignment: .leading)
                                TextField("Email", text: $email)
                                    .disabled(true) // Email can't be changed
                            }
                        }
                    }
                    .navigationTitle("Edit Profile")
                    .navigationBarItems(
                        leading: Button("Cancel") {
                            showEditProfile = false
                        },
                        trailing: Button("Save") {
                            // Update local user data
                            if let user = authViewModel.currentUser {
                                authViewModel.currentUser = User(
                                    id: user.id,
                                    firstName: firstName,
                                    lastName: lastName,
                                    email: email
                                )
                                showEditProfile = false
                            }
                            showEditProfile = false
                        }
                    )
                }
            }
        }
    }
}

#Preview {
    MyPecanView()
        .environmentObject(AuthViewModel())
} 