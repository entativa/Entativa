use tonic::transport::Server;
use tracing_subscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();
    
    let addr = "0.0.0.0:50051".parse()?;
    
    tracing::info!("Server listening on {}", addr);
    
    Server::builder()
        .add_service(service_impl())
        .serve(addr)
        .await?;
    
    Ok(())
}

fn service_impl() -> impl tonic::codegen::Service<
    http::Request<tonic::body::BoxBody>,
    Response = http::Response<tonic::body::BoxBody>,
> {
    // Placeholder
    todo!()
}
