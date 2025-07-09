import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var showingSignOutAlert = false
    @State private var showingDeleteAccountAlert = false
    
    // Settings state
    @AppStorage("autoPlay") private var autoPlay = true
    @AppStorage("streamingQuality") private var streamingQuality = "High"
    @AppStorage("downloadQuality") private var downloadQuality = "Standard"
    @AppStorage("notifications") private var notifications = true
    @AppStorage("dataUsage") private var dataUsage = "Auto"
    
    var body: some View {
        NavigationView {
            List {
                // Account Section
                Section("Account") {
                    SettingsRow(
                        icon: "person.circle.fill",
                        title: "Account Details",
                        subtitle: "Manage your account information"
                    ) {
                        // Navigate to account details
                    }
                    
                    SettingsRow(
                        icon: "creditcard.fill",
                        title: "Billing & Payments",
                        subtitle: "Manage subscription and payment methods"
                    ) {
                        // Navigate to billing
                    }
                    
                    SettingsRow(
                        icon: "iphone.fill",
                        title: "Device Management",
                        subtitle: "Manage connected devices"
                    ) {
                        // Navigate to device management
                    }
                }
                
                // Preferences Section
                Section("Preferences") {
                    SettingsRow(
                        icon: "play.circle.fill",
                        title: "Auto-Play",
                        subtitle: "Automatically play next episode",
                        action: {
                            // Toggle auto-play
                        },
                        trailing: {
                            AnyView(
                                Toggle("", isOn: $autoPlay)
                                    .labelsHidden()
                            )
                        }
                    )
                    
                    SettingsRow(
                        icon: "wifi",
                        title: "Streaming Quality",
                        subtitle: "Choose your preferred quality",
                        action: {
                            // Show quality picker
                        },
                        trailing: {
                            AnyView(
                                Text(streamingQuality)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            )
                        }
                    )
                    
                    SettingsRow(
                        icon: "arrow.down.circle.fill",
                        title: "Download Quality",
                        subtitle: "Quality for offline viewing",
                        action: {
                            // Show download quality picker
                        },
                        trailing: {
                            AnyView(
                                Text(downloadQuality)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            )
                        }
                    )
                    
                    SettingsRow(
                        icon: "bell.fill",
                        title: "Notifications",
                        subtitle: "Get notified about new content",
                        action: {
                            // Toggle notifications
                        },
                        trailing: {
                            AnyView(
                                Toggle("", isOn: $notifications)
                                    .labelsHidden()
                            )
                        }
                    )
                }
                
                // Data & Storage Section
                Section("Data & Storage") {
                    SettingsRow(
                        icon: "network",
                        title: "Data Usage",
                        subtitle: "Control data consumption",
                        action: {
                            // Show data usage options
                        },
                        trailing: {
                            AnyView(
                                Text(dataUsage)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            )
                        }
                    )
                    
                    SettingsRow(
                        icon: "externaldrive.fill",
                        title: "Storage",
                        subtitle: "Manage downloaded content",
                        action: {
                            // Navigate to storage management
                        }
                    )
                }
                
                // Support Section
                Section("Support") {
                    SettingsRow(
                        icon: "questionmark.circle.fill",
                        title: "Help Center",
                        subtitle: "Get help and support",
                        action: {
                            // Navigate to help center
                        }
                    )
                    
                    SettingsRow(
                        icon: "envelope.fill",
                        title: "Contact Us",
                        subtitle: "Send us feedback",
                        action: {
                            // Open contact form
                        }
                    )
                    
                    SettingsRow(
                        icon: "doc.text.fill",
                        title: "Terms of Service",
                        subtitle: "Read our terms and conditions",
                        action: {
                            // Show terms of service
                        }
                    )
                    
                    SettingsRow(
                        icon: "hand.raised.fill",
                        title: "Privacy Policy",
                        subtitle: "How we protect your data",
                        action: {
                            // Show privacy policy
                        }
                    )
                }
                
                // Danger Zone Section
                Section {
                    SettingsRow(
                        icon: "rectangle.portrait.and.arrow.right",
                        title: "Sign Out",
                        subtitle: "Sign out of your account",
                        color: .orange,
                        action: {
                            showingSignOutAlert = true
                        }
                    )
                    
                    SettingsRow(
                        icon: "trash.fill",
                        title: "Delete Account",
                        subtitle: "Permanently delete your account",
                        color: .red,
                        action: {
                            showingDeleteAccountAlert = true
                        }
                    )
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .alert("Sign Out", isPresented: $showingSignOutAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Sign Out", role: .destructive) {
                    authViewModel.signOut()
                    dismiss()
                }
            } message: {
                Text("Are you sure you want to sign out?")
            }
            .alert("Delete Account", isPresented: $showingDeleteAccountAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Delete", role: .destructive) {
                    // Handle account deletion
                }
            } message: {
                Text("This action cannot be undone. All your data will be permanently deleted.")
            }
        }
    }
}

// MARK: - Supporting Views
struct SettingsRow: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    let action: () -> Void
    let trailing: (() -> AnyView)?
    
    init(
        icon: String,
        title: String,
        subtitle: String,
        color: Color = .pecanRed,
        action: @escaping () -> Void,
        trailing: (() -> AnyView)? = nil
    ) {
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.color = color
        self.action = action
        self.trailing = trailing
    }
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 12) {
                Image(systemName: icon)
                    .foregroundColor(color)
                    .frame(width: 24)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(title)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    Text(subtitle)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if let trailing = trailing {
                    trailing()
                } else {
                    Image(systemName: "chevron.right")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.vertical, 4)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Quality Picker Views
struct StreamingQualityPicker: View {
    @Binding var selectedQuality: String
    @Environment(\.dismiss) private var dismiss
    
    let qualities = ["Auto", "Low", "Medium", "High", "Ultra HD"]
    
    var body: some View {
        NavigationView {
            List {
                ForEach(qualities, id: \.self) { quality in
                    Button(action: {
                        selectedQuality = quality
                        dismiss()
                    }) {
                        HStack {
                            Text(quality)
                                .foregroundColor(.primary)
                            
                            Spacer()
                            
                            if quality == selectedQuality {
                                Image(systemName: "checkmark")
                                    .foregroundColor(.pecanRed)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Streaming Quality")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
    }
}

#Preview {
    SettingsView()
        .environmentObject(AuthViewModel())
}
