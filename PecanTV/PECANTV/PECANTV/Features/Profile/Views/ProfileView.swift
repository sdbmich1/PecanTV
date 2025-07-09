import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @Binding var selectedTab: Int
    @State private var showingSettings = false
    @State private var showingSubscriptionDetails = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Profile Header
                    profileHeader
                    
                    // Subscription Status
                    subscriptionSection
                    
                    // Quick Actions
                    quickActionsSection
                    
                    // Account Info
                    accountInfoSection
                    
                    Spacer(minLength: 100)
                }
                .padding(.horizontal, 20)
            }
            .background(Color(.systemBackground))
            .navigationTitle("Profile")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingSettings = true }) {
                        Image(systemName: "gearshape.fill")
                            .foregroundColor(.primary)
                    }
                }
            }
            .sheet(isPresented: $showingSettings) {
                SettingsView()
            }
            .sheet(isPresented: $showingSubscriptionDetails) {
                SubscriptionDetailsView()
            }
        }
    }
    
    // MARK: - Profile Header
    private var profileHeader: some View {
        VStack(spacing: 16) {
            // Profile Avatar
            ZStack {
                Circle()
                    .fill(LinearGradient(
                        colors: [.pecanRed, .orange],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ))
                    .frame(width: 120, height: 120)
                
                Text(authViewModel.currentUser?.firstName.prefix(1).uppercased() ?? "U")
                    .font(.system(size: 48, weight: .bold))
                    .foregroundColor(.white)
            }
            
            // User Name
            Text(authViewModel.currentUser?.fullName ?? "Guest User")
                .font(.title2)
                .fontWeight(.semibold)
                .foregroundColor(.primary)
            
            // Email
            Text(authViewModel.currentUser?.email ?? "guest@pecantv.com")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding(.top, 20)
    }
    
    // MARK: - Subscription Section
    private var subscriptionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Subscription")
                    .font(.headline)
                    .fontWeight(.semibold)
                
                Spacer()
                
                Button("Manage") {
                    showingSubscriptionDetails = true
                }
                .font(.subheadline)
                .foregroundColor(.pecanRed)
            }
            
            HStack {
                Image(systemName: "crown.fill")
                    .foregroundColor(.yellow)
                    .font(.title2)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text("Premium Plan")
                        .font(.subheadline)
                        .fontWeight(.medium)
                    
                    Text("Active until Dec 31, 2024")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                Text("$14.99/month")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
    }
    
    // MARK: - Quick Actions
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Quick Actions")
                .font(.headline)
                .fontWeight(.semibold)
            
            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 12) {
                QuickActionCard(
                    title: "My List",
                    icon: "heart.fill",
                    color: .red
                ) {
                    // Navigate to favorites tab
                    selectedTab = 1
                }
                
                QuickActionCard(
                    title: "Watch History",
                    icon: "clock.fill",
                    color: .blue
                ) {
                    // Navigate to history
                }
                
                QuickActionCard(
                    title: "Downloads",
                    icon: "arrow.down.circle.fill",
                    color: .green
                ) {
                    // Navigate to downloads
                }
                
                QuickActionCard(
                    title: "Help & Support",
                    icon: "questionmark.circle.fill",
                    color: .orange
                ) {
                    // Navigate to support
                }
            }
        }
    }
    
    // MARK: - Account Info
    private var accountInfoSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Account")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(spacing: 0) {
                AccountInfoRow(
                    title: "Email",
                    value: authViewModel.currentUser?.email ?? "Not set",
                    icon: "envelope.fill"
                )
                
                Divider()
                
                AccountInfoRow(
                    title: "Member Since",
                    value: "June 2024",
                    icon: "calendar.fill"
                )
                
                Divider()
                
                AccountInfoRow(
                    title: "Device Limit",
                    value: "2/4 devices",
                    icon: "iphone.fill"
                )
            }
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
    }
}

// MARK: - Supporting Views
struct QuickActionCard: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct AccountInfoRow: View {
    let title: String
    let value: String
    let icon: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.pecanRed)
                .frame(width: 20)
            
            Text(title)
                .font(.subheadline)
                .foregroundColor(.primary)
            
            Spacer()
            
            Text(value)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
    }
}

#Preview {
    ProfileView(selectedTab: .constant(2))
        .environmentObject(AuthViewModel())
} 