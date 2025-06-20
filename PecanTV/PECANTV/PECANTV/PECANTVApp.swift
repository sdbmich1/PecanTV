//
//  PECANTVApp.swift
//  PECANTV
//
//  Created by Sean Brown on 5/20/25.
//

import SwiftUI
// import FirebaseCore

@main
struct PECANTVApp: App {
    // @UIApplicationDelegateAdaptor(AppDelegate.self) var delegate
    
    var body: some Scene {
        WindowGroup {
            SplashScreenView()
                .environmentObject(AuthViewModel())
                .environmentObject(ContentViewModel())
        }
    }
}

// class AppDelegate: NSObject, UIApplicationDelegate {
//     func application(_ application: UIApplication,
//                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
//         FirebaseApp.configure()
//         return true
//     }
// }
