import SwiftUI
// import FirebaseAuth

struct SignInView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var authViewModel: AuthViewModel
    @State private var email = ""
    @State private var password = ""
    @State private var firstName = ""
    @State private var lastName = ""
    @State private var isSignUp = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    // Local storage keys
    private let storedEmailKey = "stored_email"
    private let storedPasswordKey = "stored_password"
    private let storedFirstNameKey = "stored_first_name"
    private let storedLastNameKey = "stored_last_name"
    private let rememberCredentialsKey = "remember_credentials"
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Logo at the top
                Image("pecantv_logo")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 200, height: 100)
                    .padding(.top, 20)
                
                Text(isSignUp ? "Create Account" : "Sign In")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                VStack(spacing: 15) {
                    if isSignUp {
                        TextField("First Name", text: $firstName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .textContentType(.givenName)
                            .autocapitalization(.words)
                            .onSubmit {
                                // Move to next field
                            }
                        
                        TextField("Last Name", text: $lastName)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .textContentType(.familyName)
                            .autocapitalization(.words)
                            .onSubmit {
                                // Move to email field
                            }
                    }
                    
                    TextField("Email", text: $email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .textContentType(.emailAddress)
                        .autocapitalization(.none)
                        .onSubmit {
                            // Move to password field
                        }
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .textContentType(isSignUp ? .newPassword : .password)
                        .onSubmit {
                            // Submit form when enter is pressed and both fields are filled
                            if !email.isEmpty && !password.isEmpty {
                                submitForm()
                            }
                        }
                }
                .padding(.horizontal)
                
                // Remember credentials toggle (only for sign in)
                if !isSignUp {
                    Toggle("Remember my credentials", isOn: .constant(true))
                        .font(.caption)
                        .padding(.horizontal)
                }
                
                Button(action: submitForm) {
                    HStack {
                        if authViewModel.isLoading {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Text(isSignUp ? "Sign Up" : "Sign In")
                                .fontWeight(.semibold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.pecanRed)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                .buttonStyle(PlainButtonStyle())
                .padding(.horizontal)
                .disabled(authViewModel.isLoading || email.isEmpty || password.isEmpty)
                .contentShape(Rectangle())
                
                Button(action: {
                    isSignUp.toggle()
                    // Load appropriate stored credentials when switching modes
                    loadStoredCredentials()
                }) {
                    Text(isSignUp ? "Already have an account? Sign In" : "Don't have an account? Sign Up")
                        .foregroundColor(.blue)
                }
                
                Spacer()
            }
            .padding()
            .navigationBarItems(trailing: Button("Cancel") {
                dismiss()
            })
            .alert("Error", isPresented: $showError) {
                Button("OK") { }
            } message: {
                Text(errorMessage)
            }
            .onReceive(authViewModel.$error) { error in
                if let error = error {
                    errorMessage = error.localizedDescription
                    showError = true
                }
            }
            .onReceive(authViewModel.$isAuthenticated) { isAuthenticated in
                if isAuthenticated {
                    // Save credentials if authentication successful
                    saveCredentials()
                    dismiss()
                }
            }
            .onAppear {
                loadStoredCredentials()
            }
        }
    }
    
    private func submitForm() {
        Task {
            if isSignUp {
                // Validate signup fields
                guard !firstName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    errorMessage = "First name is required"
                    showError = true
                    return
                }
                
                guard !lastName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    errorMessage = "Last name is required"
                    showError = true
                    return
                }
                
                guard !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    errorMessage = "Email is required"
                    showError = true
                    return
                }
                
                guard !password.isEmpty else {
                    errorMessage = "Password is required"
                    showError = true
                    return
                }
                
                await authViewModel.signUp(
                    email: email.trimmingCharacters(in: .whitespacesAndNewlines),
                    password: password,
                    firstName: firstName.trimmingCharacters(in: .whitespacesAndNewlines),
                    lastName: lastName.trimmingCharacters(in: .whitespacesAndNewlines)
                )
            } else {
                // Validate signin fields
                guard !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    errorMessage = "Email is required"
                    showError = true
                    return
                }
                
                guard !password.isEmpty else {
                    errorMessage = "Password is required"
                    showError = true
                    return
                }
                
                await authViewModel.signIn(
                    email: email.trimmingCharacters(in: .whitespacesAndNewlines),
                    password: password
                )
            }
        }
    }
    
    private func saveCredentials() {
        UserDefaults.standard.set(email, forKey: storedEmailKey)
        UserDefaults.standard.set(password, forKey: storedPasswordKey)
        if isSignUp {
            UserDefaults.standard.set(firstName, forKey: storedFirstNameKey)
            UserDefaults.standard.set(lastName, forKey: storedLastNameKey)
        }
        UserDefaults.standard.set(true, forKey: rememberCredentialsKey)
    }
    
    private func loadStoredCredentials() {
        // Always load the last entered email
        email = UserDefaults.standard.string(forKey: storedEmailKey) ?? ""
        
        // Load password if remember credentials is enabled
        if UserDefaults.standard.bool(forKey: rememberCredentialsKey) {
            password = UserDefaults.standard.string(forKey: storedPasswordKey) ?? ""
        }
        
        // Load name fields for sign up
        if isSignUp {
            firstName = UserDefaults.standard.string(forKey: storedFirstNameKey) ?? ""
            lastName = UserDefaults.standard.string(forKey: storedLastNameKey) ?? ""
        }
    }
}

#Preview {
    SignInView()
} 