import Foundation
import Combine

class AuthViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var error: String?
    
    private var cancellables = Set<AnyCancellable>()
    private let authService: AuthServiceProtocol
    
    init(authService: AuthServiceProtocol = AuthService()) {
        self.authService = authService
    }
    
    func signIn(email: String, password: String) {
        authService.signIn(email: email, password: password)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                if case .failure(let error) = completion {
                    self?.error = error.localizedDescription
                }
            } receiveValue: { [weak self] user in
                self?.currentUser = user
                self?.isAuthenticated = true
                self?.error = nil
            }
            .store(in: &cancellables)
    }
    
    func signUp(email: String, password: String) {
        authService.signUp(email: email, password: password)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                if case .failure(let error) = completion {
                    self?.error = error.localizedDescription
                }
            } receiveValue: { [weak self] user in
                self?.currentUser = user
                self?.isAuthenticated = true
                self?.error = nil
            }
            .store(in: &cancellables)
    }
    
    func signOut() {
        authService.signOut()
        currentUser = nil
        isAuthenticated = false
    }
} 