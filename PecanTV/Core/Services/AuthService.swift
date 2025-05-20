import Foundation
import Combine

protocol AuthServiceProtocol {
    func signIn(email: String, password: String) -> AnyPublisher<User, Error>
    func signUp(email: String, password: String) -> AnyPublisher<User, Error>
    func signOut()
}

class AuthService: AuthServiceProtocol {
    private let networkManager: NetworkManager
    
    init(networkManager: NetworkManager = .shared) {
        self.networkManager = networkManager
    }
    
    func signIn(email: String, password: String) -> AnyPublisher<User, Error> {
        let credentials = ["email": email, "password": password]
        return networkManager.request(Config.Endpoints.signIn(), method: "POST", body: credentials)
    }
    
    func signUp(email: String, password: String) -> AnyPublisher<User, Error> {
        let credentials = ["email": email, "password": password]
        return networkManager.request(Config.Endpoints.signUp(), method: "POST", body: credentials)
    }
    
    func signOut() {
        UserDefaults.standard.removeObject(forKey: Config.UserDefaultsKeys.authToken)
        UserDefaults.standard.removeObject(forKey: Config.UserDefaultsKeys.currentUser)
    }
} 