import SwiftUI

struct GenrePicker: View {
    @Binding var selectedGenre: String
    @Binding var showPicker: Bool
    let genres: [String]
    
    var body: some View {
        Button(action: {
            showPicker = true
        }) {
            HStack {
                Text(selectedGenre)
                    .foregroundColor(.primary)
                Image(systemName: "chevron.down")
                    .foregroundColor(.gray)
            }
            .padding(8)
            .frame(maxWidth: .infinity)
            .background(Color(.systemGray6))
            .cornerRadius(8)
        }
        .sheet(isPresented: $showPicker) {
            NavigationView {
                List {
                    ForEach(genres, id: \.self) { genre in
                        Button(action: {
                            selectedGenre = genre
                            showPicker = false
                        }) {
                            HStack {
                                Text(genre)
                                    .foregroundColor(.primary)
                                Spacer()
                                if genre == selectedGenre {
                                    Image(systemName: "checkmark")
                                        .foregroundColor(.pecanRed)
                                }
                            }
                        }
                    }
                }
                .navigationTitle("Select Genre")
                .navigationBarItems(trailing: Button("Done") {
                    showPicker = false
                })
            }
        }
    }
}

#Preview {
    GenrePicker(
        selectedGenre: .constant("All Genres"),
        showPicker: .constant(false),
        genres: ["All Genres", "Action", "Comedy", "Drama"]
    )
} 