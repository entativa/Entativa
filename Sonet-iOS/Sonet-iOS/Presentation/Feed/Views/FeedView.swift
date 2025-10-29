import SwiftUI

struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVStack(spacing: 16) {
                    ForEach(viewModel.boos) { boo in
                        BooCard(boo: boo)
                    }
                }
                .padding()
            }
            .navigationTitle("Feed")
            .refreshable {
                await viewModel.refresh()
            }
        }
        .task {
            await viewModel.loadFeed()
        }
    }
}
