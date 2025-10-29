import SwiftUI

struct BooCard: View {
    let boo: Boo
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(boo.username)
                    .font(.headline)
                Spacer()
                CountdownTimer(expiresAt: boo.expiresAt)
            }
            
            Text(boo.content)
                .font(.body)
            
            HStack(spacing: 20) {
                MetricButton(icon: "flame.fill", count: boo.fireCount)
                MetricButton(icon: "bubble.right", count: boo.replyCount)
                MetricButton(icon: "heart", count: boo.saveCount)
                MetricButton(icon: "arrow.turn.up.right", count: boo.duetCount)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}
