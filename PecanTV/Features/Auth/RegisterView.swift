import SwiftUI

struct RegisterView: View {
    @State private var email = ""
    @State private var username = ""
    @State private var password = ""
    @State private var errorMessage: String?
    @State private var isRegistered = false

    var body: some View {
        VStack {
            TextField("Email", text: $email)
                .autocapitalization(.none)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            TextField("Username", text: $username)
                .autocapitalization(.none)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            SecureField("Password", text: $password)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            if let error = errorMessage {
                Text(error).foregroundColor(.red)
            }
            Button("Register") {
                register(email: email, username: username, password: password) { success in
                    DispatchQueue.main.async {
                        if success {
                            isRegistered = true
                        } else {
                            errorMessage = "Registration failed"
                        }
                    }
                }
            }
            .padding()
        }
        .padding()
        .navigationTitle("Register")
        .alert(isPresented: $isRegistered) {
            Alert(title: Text("Success"), message: Text("Registration successful!"), dismissButton: .default(Text("OK")))
        }
    }
} 