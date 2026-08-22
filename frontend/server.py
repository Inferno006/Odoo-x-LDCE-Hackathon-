import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Normalize path
        path = self.path.split('?')[0].rstrip('/')
        
        # Routing table for clean routes
        routes = {
            "": "/explore_globetrotter/code.html",
            "/explore": "/explore_globetrotter/code.html",
            "/login": "/login_globetrotter/code.html",
            "/register": "/register_globetrotter/code.html",
            "/my-journeys": "/my_journeys_globetrotter/code.html",
            "/plan-trip": "/plan_a_trip_globetrotter/code.html",
            "/itinerary-budget": "/itinerary_budget_globetrotter/code.html",
            "/itinerary-builder": "/itinerary_builder_globetrotter/code.html",
            "/profile": "/profile_globetrotter/code.html",
            "/search": "/search_globetrotter/code.html",
            "/admin": "/admin_panel_globetrotter/code.html",
            "/community": "/community_globetrotter/code.html",
        }
        
        if path in routes:
            self.path = routes[path]
            return super().do_GET()
            
        return super().do_GET()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"GlobeTrotter frontend serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
