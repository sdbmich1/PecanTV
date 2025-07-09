import SwiftUI

struct SubscriptionDetailsView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var showingCancelAlert = false
    @State private var showingUpgradeAlert = false
    
    // Mock subscription data - in real app, this would come from API
    @State private var subscription = SubscriptionDetails(
        plan: "Premium",
        price: "$14.99",
        billingCycle: "Monthly",
        nextBillingDate: "December 31, 2024",
        status: "Active",
        features: [
            "4K Ultra HD streaming",
            "Watch on 4 devices",
            "Download on 4 devices",
            "No ads"
        ]
    )
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Current Plan Section
                    currentPlanSection
                    
                    // Billing Information
                    billingSection
                    
                    // Plan Features
                    featuresSection
                    
                    // Action Buttons
                    actionButtonsSection
                    
                    Spacer(minLength: 100)
                }
                .padding(.horizontal, 20)
            }
            .background(Color(.systemBackground))
            .navigationTitle("Subscription")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .alert("Cancel Subscription", isPresented: $showingCancelAlert) {
                Button("Keep Subscription", role: .cancel) { }
                Button("Cancel Subscription", role: .destructive) {
                    // Handle subscription cancellation
                }
            } message: {
                Text("Your subscription will remain active until the end of your current billing period.")
            }
            .alert("Upgrade Plan", isPresented: $showingUpgradeAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Upgrade") {
                    // Handle plan upgrade
                }
            } message: {
                Text("Would you like to upgrade to the Family plan for $19.99/month?")
            }
        }
    }
    
    // MARK: - Current Plan Section
    private var currentPlanSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Current Plan")
                .font(.headline)
                .fontWeight(.semibold)
            
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    Text(subscription.plan)
                        .font(.title2)
                        .fontWeight(.bold)
                        .foregroundColor(.pecanRed)
                    
                    Text(subscription.price + "/" + subscription.billingCycle.lowercased())
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                StatusBadge(status: subscription.status)
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
    }
    
    // MARK: - Billing Section
    private var billingSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Billing Information")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(spacing: 0) {
                BillingRow(
                    title: "Next Billing Date",
                    value: subscription.nextBillingDate,
                    icon: "calendar"
                )
                
                Divider()
                
                BillingRow(
                    title: "Payment Method",
                    value: "•••• •••• •••• 1234",
                    icon: "creditcard"
                )
                
                Divider()
                
                BillingRow(
                    title: "Billing Cycle",
                    value: subscription.billingCycle,
                    icon: "repeat"
                )
            }
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
    }
    
    // MARK: - Features Section
    private var featuresSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Plan Features")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(spacing: 12) {
                ForEach(subscription.features, id: \.self) { feature in
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                            .font(.subheadline)
                        
                        Text(feature)
                            .font(.subheadline)
                            .foregroundColor(.primary)
                        
                        Spacer()
                    }
                }
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
    }
    
    // MARK: - Action Buttons
    private var actionButtonsSection: some View {
        VStack(spacing: 12) {
            Button(action: { showingUpgradeAlert = true }) {
                HStack {
                    Image(systemName: "arrow.up.circle.fill")
                    Text("Upgrade Plan")
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.pecanRed)
                .cornerRadius(12)
            }
            
            Button(action: { showingCancelAlert = true }) {
                HStack {
                    Image(systemName: "xmark.circle.fill")
                    Text("Cancel Subscription")
                }
                .foregroundColor(.red)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
            }
        }
    }
}

// MARK: - Supporting Views
struct StatusBadge: View {
    let status: String
    
    var body: some View {
        Text(status)
            .font(.caption)
            .fontWeight(.medium)
            .foregroundColor(.white)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(status == "Active" ? Color.green : Color.orange)
            .cornerRadius(8)
    }
}

struct BillingRow: View {
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

// MARK: - Models
struct SubscriptionDetails {
    let plan: String
    let price: String
    let billingCycle: String
    let nextBillingDate: String
    let status: String
    let features: [String]
}

#Preview {
    SubscriptionDetailsView()
} 