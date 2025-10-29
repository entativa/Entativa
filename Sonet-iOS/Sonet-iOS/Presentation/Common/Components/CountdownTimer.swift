import SwiftUI

struct CountdownTimer: View {
    let expiresAt: Date
    @State private var timeRemaining: TimeInterval
    
    init(expiresAt: Date) {
        self.expiresAt = expiresAt
        self._timeRemaining = State(initialValue: expiresAt.timeIntervalSinceNow)
    }
    
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: "flame.fill")
                .font(.caption2)
            Text(formattedTime)
                .font(.caption.monospacedDigit())
        }
        .foregroundColor(timeColor)
        .onReceive(Timer.publish(every: 1, on: .main, in: .common).autoconnect()) { _ in
            timeRemaining = expiresAt.timeIntervalSinceNow
        }
    }
    
    private var formattedTime: String {
        let hours = Int(timeRemaining) / 3600
        let minutes = (Int(timeRemaining) % 3600) / 60
        return "\(hours)h \(minutes)m"
    }
    
    private var timeColor: Color {
        timeRemaining < 3600 ? .red : timeRemaining < 10800 ? .orange : .secondary
    }
}
