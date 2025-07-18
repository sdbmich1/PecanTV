import SwiftUI
import MessageUI

struct ContactUsView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var showingMailComposer = false
    @State private var showingPhoneAlert = false
    @State private var showingAddressAlert = false
    @State private var showingFeedbackForm = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 24) {
                    // Header
                    VStack(spacing: 12) {
                        Image(systemName: "envelope.circle.fill")
                            .font(.system(size: 60))
                            .foregroundColor(.pecanRed)
                        
                        Text("Contact Pecan TV")
                            .font(.title)
                            .fontWeight(.bold)
                        
                        Text("We're here to help! Choose your preferred way to get in touch.")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                            .padding(.horizontal)
                    }
                    .padding(.top)
                    
                    // Contact Options
                    VStack(spacing: 16) {
                        // Email Support
                        ContactOptionCard(
                            icon: "envelope.fill",
                            title: "Email Support",
                            subtitle: "Get help via email",
                            description: "Send us a detailed message and we'll respond within 24 hours.",
                            action: {
                                showingMailComposer = true
                            }
                        )
                        
                        // Phone Support
                        ContactOptionCard(
                            icon: "phone.fill",
                            title: "Phone Support",
                            subtitle: "Call us directly",
                            description: "Speak with our support team during business hours.",
                            action: {
                                showingPhoneAlert = true
                            }
                        )
                        
                        // Physical Address
                        ContactOptionCard(
                            icon: "location.fill",
                            title: "Visit Us",
                            subtitle: "Our office location",
                            description: "Stop by our San Francisco office during business hours.",
                            action: {
                                showingAddressAlert = true
                            }
                        )
                        
                        // Feedback Form
                        ContactOptionCard(
                            icon: "square.and.pencil",
                            title: "Send Feedback",
                            subtitle: "Share your thoughts",
                            description: "Help us improve by sharing your experience and suggestions.",
                            action: {
                                showingFeedbackForm = true
                            }
                        )
                    }
                    
                    // Business Hours
                    BusinessHoursCard()
                    
                    // FAQ Link
                    FAQLinkCard()
                }
                .padding()
            }
            .navigationTitle("Contact Us")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
            .sheet(isPresented: $showingMailComposer) {
                MailComposerView()
            }
            .sheet(isPresented: $showingFeedbackForm) {
                FeedbackFormView()
            }
            .alert("Call Support", isPresented: $showingPhoneAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Call (415) 409-8863") {
                    if let url = URL(string: "tel:4154098863") {
                        UIApplication.shared.open(url)
                    }
                }
            } message: {
                Text("Call our support team at (415) 409-8863 during business hours: Monday-Friday, 9 AM - 6 PM PST")
            }
            .alert("Visit Our Office", isPresented: $showingAddressAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Open in Maps") {
                    if let url = URL(string: "https://maps.apple.com/?address=3450+Sacramento+St,+San+Francisco,+CA+94118") {
                        UIApplication.shared.open(url)
                    }
                }
            } message: {
                Text("Pecan TV\n3450 Sacramento St., Ste 401\nSan Francisco, CA 94118\n\nBusiness Hours: Monday-Friday, 9 AM - 6 PM PST")
            }
        }
    }
}

// MARK: - Supporting Views
struct ContactOptionCard: View {
    let icon: String
    let title: String
    let subtitle: String
    let description: String
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.pecanRed)
                    .frame(width: 32)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    Text(subtitle)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.pecanRed)
                    
                    Text(description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.leading)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

struct BusinessHoursCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "clock.fill")
                    .foregroundColor(.pecanRed)
                Text("Business Hours")
                    .font(.headline)
                    .fontWeight(.semibold)
            }
            
            VStack(alignment: .leading, spacing: 8) {
                BusinessHourRow(day: "Monday - Friday", hours: "9:00 AM - 6:00 PM PST")
                BusinessHourRow(day: "Saturday", hours: "10:00 AM - 4:00 PM PST")
                BusinessHourRow(day: "Sunday", hours: "Closed")
            }
            
            Text("For urgent technical issues outside business hours, please email us and we'll respond as soon as possible.")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

struct BusinessHourRow: View {
    let day: String
    let hours: String
    
    var body: some View {
        HStack {
            Text(day)
                .font(.subheadline)
                .fontWeight(.medium)
                .foregroundColor(.primary)
            
            Spacer()
            
            Text(hours)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }
}

struct FAQLinkCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "questionmark.circle.fill")
                    .foregroundColor(.pecanRed)
                Text("Frequently Asked Questions")
                    .font(.headline)
                    .fontWeight(.semibold)
            }
            
            Text("Find quick answers to common questions in our Help Center.")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            Button("Visit Help Center") {
                // This would navigate to Help Center
            }
            .font(.subheadline)
            .fontWeight(.medium)
            .foregroundColor(.pecanRed)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

// MARK: - Mail Composer
struct MailComposerView: UIViewControllerRepresentable {
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let composer = MFMailComposeViewController()
        composer.mailComposeDelegate = context.coordinator
                        composer.setToRecipients(["help@pecantv.com"])
        composer.setSubject("Pecan TV Support Request")
        composer.setMessageBody("""
        Hello Pecan TV Support Team,
        
        I'm reaching out for help with the following issue:
        
        [Please describe your issue here]
        
        Device: [Your device model]
        App Version: [App version if known]
        iOS Version: [Your iOS version]
        
        Thank you,
        [Your name]
        """, isHTML: false)
        return composer
    }
    
    func updateUIViewController(_ uiViewController: MFMailComposeViewController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let parent: MailComposerView
        
        init(_ parent: MailComposerView) {
            self.parent = parent
        }
        
        func mailComposeController(_ controller: MFMailComposeViewController, didFinishWith result: MFMailComposeResult, error: Error?) {
            parent.dismiss()
        }
    }
}

// MARK: - Feedback Form
struct FeedbackFormView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var feedbackType = "General"
    @State private var feedbackText = ""
    @State private var email = ""
    @State private var showingThankYou = false
    
    let feedbackTypes = ["General", "Bug Report", "Feature Request", "Content Request", "Other"]
    
    var body: some View {
        NavigationView {
            Form {
                Section("Feedback Type") {
                    Picker("Type", selection: $feedbackType) {
                        ForEach(feedbackTypes, id: \.self) { type in
                            Text(type).tag(type)
                        }
                    }
                    .pickerStyle(MenuPickerStyle())
                }
                
                Section("Your Feedback") {
                    TextEditor(text: $feedbackText)
                        .frame(minHeight: 120)
                }
                
                Section("Contact Information (Optional)") {
                    TextField("Email", text: $email)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                }
                
                Section {
                    Button("Submit Feedback") {
                        submitFeedback()
                    }
                    .disabled(feedbackText.isEmpty)
                }
            }
            .navigationTitle("Send Feedback")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert("Thank You!", isPresented: $showingThankYou) {
                Button("OK") {
                    dismiss()
                }
            } message: {
                Text("Your feedback has been submitted. We appreciate your input!")
            }
        }
    }
    
    private func submitFeedback() {
        // Here you would typically send the feedback to your backend
        // For now, we'll just show a thank you message
        showingThankYou = true
    }
}

#Preview {
    ContactUsView()
} 