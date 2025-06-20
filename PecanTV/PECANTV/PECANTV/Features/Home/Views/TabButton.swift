import SwiftUI

struct TabButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .foregroundColor(isSelected ? .white : .gray)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
                .background(isSelected ? Color.pecanRed : Color.clear)
                .cornerRadius(8)
        }
    }
}

#Preview {
    TabButton(title: "Sample", isSelected: true) {}
} 