import SwiftUI

struct HomePreview: View {
    @StateObject private var viewModel = DemoHomeViewModel()
    var body: some View {
        HomeView()
            .environmentObject(viewModel)
    }
}

#Preview {
    HomePreview()
} 