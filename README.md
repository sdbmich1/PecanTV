# PecanTV

A Netflix-style video streaming application for iOS built with Swift and SwiftUI.

## Features

- User authentication and profile management
- Dynamic content carousels
- Advanced search and filtering
- Detailed content pages
- Seamless video playback
- Offline viewing support (coming soon)

## Architecture

The app follows the MVVM (Model-View-ViewModel) architecture pattern:

- **Models**: Data structures and business logic
- **Views**: SwiftUI views and UI components
- **ViewModels**: Business logic and state management
- **Services**: Network, authentication, and data persistence

## Requirements

- iOS 16.0+
- Xcode 14.0+
- Swift 5.7+

## Setup

1. Clone the repository
2. Open `PecanTV.xcodeproj` in Xcode
3. Install dependencies using Swift Package Manager
4. Build and run the project

## Project Structure

```
PecanTV/
├── App/
│   ├── PecanTVApp.swift
│   └── AppDelegate.swift
├── Features/
│   ├── Authentication/
│   ├── Home/
│   ├── Search/
│   ├── ContentDetail/
│   └── VideoPlayer/
├── Core/
│   ├── Models/
│   ├── Services/
│   ├── Utils/
│   └── Extensions/
└── Resources/
    ├── Assets.xcassets
    └── Info.plist
```

## Dependencies

- SwiftUI
- Combine
- CoreData (for local caching)
- AVKit (for video playback)

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 