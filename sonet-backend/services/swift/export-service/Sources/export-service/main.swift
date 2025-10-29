import Vapor
import Logging

@main
struct Application {{
    static func main() async throws {{
        let app = Vapor.Application()
        defer {{ app.shutdown() }}
        
        try configure(app)
        try app.run()
    }}
}}

func configure(_ app: Vapor.Application) throws {{
    app.http.server.configuration.hostname = "0.0.0.0"
    app.http.server.configuration.port = 8080
    
    try routes(app)
}}

func routes(_ app: Vapor.Application) throws {{
    app.get("health") {{ req in
        return ["status": "ok"]
    }}
}}
