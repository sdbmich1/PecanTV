import SwiftUI

struct SearchBar: View {
    @Binding var text: String
    let placeholder: String
    
    init(text: Binding<String>, placeholder: String = "Search") {
        self._text = text
        self.placeholder = placeholder
    }
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.gray)
                .font(.system(size: 18)) // Larger for iPad
                .frame(width: 44, height: 44) // Larger touch target for iPad
                .contentShape(Rectangle())
            
            TextField(placeholder, text: $text)
                .textFieldStyle(PlainTextFieldStyle())
                .foregroundColor(.black)
                .font(.system(size: 18)) // Larger font for iPad
                .frame(minHeight: 44)
                .contentShape(Rectangle())
            
            if !text.isEmpty {
                Button {
                    text = ""
                } label: {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.gray)
                        .font(.system(size: 20)) // Larger for iPad
                }
                .buttonStyle(PlainButtonStyle())
                .frame(width: 44, height: 44) // Larger touch target for iPad
                .contentShape(Rectangle())
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color.gray.opacity(0.1))
        .cornerRadius(25)
        .frame(minHeight: 56) // Larger minimum height for iPad
        .contentShape(Rectangle())
    }
}

#Preview {
    VStack(spacing: 20) {
        SearchBar(text: .constant(""), placeholder: "Search movies and shows...")
        SearchBar(text: .constant("test"), placeholder: "Search movies and shows...")
    }
    .padding()
} 