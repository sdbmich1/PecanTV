import SwiftUI

struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    @State private var errorMessage: String?
    @State private var isLoggedIn = false
    @State private var showRegister = false

    var body: some View {
        NavigationView {
            VStack {
                Image("pecantv_logo")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 200, height: 80)
                TextField("Email", text: $email)
                    .autocapitalization(.none)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                SecureField("Password", text: $password)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                if let error = errorMessage {
                    Text(error).foregroundColor(.red)
                }
                Button("Login") {
                    login(email: email, password: password) { token in
                        DispatchQueue.main.async {
                            if token != nil {
                                isLoggedIn = true
                            } else {
                                errorMessage = "Login failed"
                            }
                        }
                    }
                }
                .padding()
                Button("Register") {
                    showRegister = true
                }
                .padding(.bottom)
                NavigationLink("", destination: RegisterView(), isActive: $showRegister).hidden()
            }
            .padding()
            .navigationTitle("Login")
            .fullScreenCover(isPresented: $isLoggedIn) {
                Text("Logged in!") // Replace with your main app view
            }
        }
    }
} 