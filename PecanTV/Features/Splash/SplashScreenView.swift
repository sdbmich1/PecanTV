import SwiftUI

struct SplashScreenView: View {
    @Binding var isActive: Bool

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()
            Image("pecantv_logo")
                .resizable()
                .scaledToFit()
                .frame(width: 200, height: 200)
        }
        .onAppear {
            DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                isActive = false
            }
        }
    }
}

#Preview {
    SplashScreenView(isActive: .constant(true))
} 