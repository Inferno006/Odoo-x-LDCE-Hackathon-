(function() {
    const originalFetch = window.fetch;
    
    // Persistent Session Storage for Mock Posts (shared across page refreshes)
    let mockPosts = JSON.parse(sessionStorage.getItem('mock_posts') || 'null');
    if (!mockPosts) {
        mockPosts = [
            {
                id: 1,
                user_name: "Aarav Sharma",
                user_avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
                destination: "Delhi",
                content: "Spent the day exploring the historical lanes of Chandni Chowk! The Paranthe Wali Gali breakfast was incredible. Definitely recommend visiting the Red Fort at sunset.",
                created_at: new Date(Date.now() - 3600000).toISOString(),
                likes: 24
            },
            {
                id: 2,
                user_name: "Ananya Iyer",
                user_avatar: "https://lh3.googleusercontent.com/aida-public/AB6AXuDumwbhlOUMegHHqN7pOujIAR79QXNa2cqcymgdiw6LfcZRA9b_YiEN7FDQbOuZam6sdHkZ6anijKHf7VlR04-_Zw0hk8GybBiJk2s_dC-2WeFMxj5xN-Ow0BVib5vRPSiXL0bhgMHOD4y21R4RytKfRPLBdzostR6nKLG9jCNAlL8cGvOH9Dh3Iphj2CZIh6-3JDz0MGRI0Xi9Pwqxqm25h8mN3xCKjKNXlZSldzkXz9VXViJu-RSD",
                destination: "Munnar",
                content: "Mist-covered tea gardens and pleasant weather! Munnar is absolute bliss in the morning. Stayed in a lovely local homestay.",
                created_at: new Date(Date.now() - 7200000).toISOString(),
                likes: 42
            },
            {
                id: 3,
                user_name: "Rahul Verma",
                user_avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
                destination: "Goa",
                content: "Perfect sunset at Baga Beach! Water is clean, crowds are light, and beach shacks are serving amazing local fish curry.",
                created_at: new Date(Date.now() - 86400000).toISOString(),
                likes: 85
            }
        ];
        sessionStorage.setItem('mock_posts', JSON.stringify(mockPosts));
    }

    window.fetch = async function(url, options) {
        const urlStr = typeof url === 'string' ? url : (url && url.url) || '';
        
        if (urlStr.includes('127.0.0.1:8000') || urlStr.includes('localhost:8000')) {
            try {
                // Attempt real call
                const response = await originalFetch(url, options);
                return response;
            } catch (error) {
                console.warn(`[Mock API] Backend not reachable. Falling back to local mock data for: ${urlStr}`);
                return handleMock(urlStr, options);
            }
        }
        
        return originalFetch(url, options);
    };

    function handleMock(url, options) {
        let status = 200;
        let data = {};

        if (url.includes('/api/auth/login')) {
            let email = "";
            try {
                if (options && options.body) {
                    const body = JSON.parse(options.body);
                    email = body.email || body.username || "";
                }
            } catch (e) {}
            const role = email === 'admin@globetrotter.dev' ? 'admin' : 'user';
            data = { access_token: `mock-session-token-${role}` };
        } else if (url.includes('/api/auth/me')) {
            const token = (options && options.headers && options.headers['Authorization']) || '';
            const role = token.includes('admin') ? 'admin' : 'user';
            data = {
                id: role === 'admin' ? 99 : 1,
                name: role === 'admin' ? "System Administrator" : "Ananya Iyer",
                email: role === 'admin' ? "admin@globetrotter.dev" : "ananya@globetrotter.dev",
                avatar_url: role === 'admin' ? "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150" : "https://lh3.googleusercontent.com/aida-public/AB6AXuDumwbhlOUMegHHqN7pOujIAR79QXNa2cqcymgdiw6LfcZRA9b_YiEN7FDQbOuZam6sdHkZ6anijKHf7VlR04-_Zw0hk8GybBiJk2s_dC-2WeFMxj5xN-Ow0BVib5vRPSiXL0bhgMHOD4y21R4RytKfRPLBdzostR6nKLG9jCNAlL8cGvOH9Dh3Iphj2CZIh6-3JDz0MGRI0Xi9Pwqxqm25h8mN3xCKjKNXlZSldzkXz9VXViJu-RSD",
                role: role
            };
        } else if (url.includes('/api/auth/register')) {
            data = { id: 1, name: "Ananya Iyer", email: "ananya@globetrotter.dev", role: "user" };
        } else if (url.includes('/api/users')) {
            data = [
                { id: 1, name: "Aarav Sharma", email: "aarav@globetrotter.dev", role: "user", avatar_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150" },
                { id: 2, name: "Ananya Iyer", email: "ananya@globetrotter.dev", role: "user", avatar_url: "https://lh3.googleusercontent.com/aida-public/AB6AXuDumwbhlOUMegHHqN7pOujIAR79QXNa2cqcymgdiw6LfcZRA9b_YiEN7FDQbOuZam6sdHkZ6anijKHf7VlR04-_Zw0hk8GybBiJk2s_dC-2WeFMxj5xN-Ow0BVib5vRPSiXL0bhgMHOD4y21R4RytKfRPLBdzostR6nKLG9jCNAlL8cGvOH9Dh3Iphj2CZIh6-3JDz0MGRI0Xi9Pwqxqm25h8mN3xCKjKNXlZSldzkXz9VXViJu-RSD" },
                { id: 99, name: "System Administrator", email: "admin@globetrotter.dev", role: "admin", avatar_url: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150" }
            ];
        } else if (url.includes('/api/admin/stats')) {
            data = {
                user_count: 24592,
                trip_count: 1843,
                post_count: mockPosts.length,
                revenue: 36888000
            };
        } else if (url.includes('/api/posts')) {
            if (options && options.method === 'POST') {
                const body = JSON.parse(options.body || '{}');
                const currentUser = JSON.parse(localStorage.getItem('user') || '{"name":"Anonymous","avatar_url":"https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"}');
                const newPost = {
                    id: mockPosts.length + 1,
                    user_name: currentUser.name || "Anonymous",
                    user_avatar: currentUser.avatar_url || currentUser.avatar || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
                    destination: body.destination || "General",
                    content: body.content,
                    created_at: new Date().toISOString(),
                    likes: 0
                };
                mockPosts.unshift(newPost);
                sessionStorage.setItem('mock_posts', JSON.stringify(mockPosts));
                data = newPost;
            } else {
                // GET request, support filter
                const urlObj = new URL(url, window.location.origin);
                const dest = urlObj.searchParams.get('destination');
                if (dest) {
                    data = mockPosts.filter(p => p.destination.toLowerCase() === dest.toLowerCase());
                } else {
                    data = mockPosts;
                }
            }
        } else if (url.includes('/api/trips')) {
            const match = url.match(/\/api\/trips\/(\d+)/);
            if (match) {
                data = getMockTrip(parseInt(match[1]));
            } else {
                data = [getMockTrip(1), getMockTrip(2)];
            }
        } else if (url.includes('/api/ai-generate-trip')) {
            data = getMockTrip(1);
        } else if (url.includes('/activities') && options && options.method === 'POST') {
            const body = JSON.parse(options.body || '{}');
            data = {
                id: Math.floor(Math.random() * 1000) + 100,
                stop_id: 1,
                title: body.title,
                activity_time: body.activity_time,
                cost: body.cost,
                category: body.category
            };
        } else {
            status = 404;
            data = { detail: "Endpoint not mocked" };
        }

        const responseInit = {
            status: status,
            statusText: status === 200 ? "OK" : "Not Found",
            headers: { 'Content-Type': 'application/json' }
        };

        return Promise.resolve(new Response(JSON.stringify(data), responseInit));
    }

    function getMockTrip(id) {
        if (id === 2) {
            return {
                "id": 2,
                "title": "Kerala Backwaters Tour",
                "total_budget": 58000,
                "stay_budget": 28000,
                "meals_budget": 12000,
                "transport_budget": 18000,
                "share_code": "IN-KERALA",
                "cover_image": "/goa_beach.jpg",
                "stops": [
                  {
                    "city": "Kochi",
                    "start_date": "2026-07-10",
                    "end_date": "2026-07-12",
                    "activities": [
                      {
                        "title": "Fort Kochi & Chinese Fishing Nets Stroll",
                        "activity_time": "2026-07-10T14:00:00",
                        "category": "Sightseeing",
                        "cost": 500
                      }
                    ]
                  },
                  {
                    "city": "Munnar",
                    "start_date": "2026-07-12",
                    "end_date": "2026-07-15",
                    "activities": [
                      {
                        "title": "Tea Garden Safari in Munnar",
                        "activity_time": "2026-07-13T11:00:00",
                        "category": "Outdoors",
                        "cost": 1500
                      },
                      {
                        "title": "Athirappilly Waterfalls Stop",
                        "activity_time": "2026-07-14T09:00:00",
                        "category": "Outdoors",
                        "cost": 0
                      }
                    ]
                  }
                ]
            };
        }
        
        return {
            "id": 1,
            "title": "Golden Triangle Tour",
            "total_budget": 75000,
            "stay_budget": 35000,
            "meals_budget": 15000,
            "transport_budget": 25000,
            "share_code": "IN-GOLDEN",
            "cover_image": "/red_fort.jpg",
            "stops": [
              {
                "city": "Delhi",
                "start_date": "2026-04-02",
                "end_date": "2026-04-05",
                "activities": [
                  {
                    "title": "Red Fort & Chandni Chowk Walk",
                    "activity_time": "2026-04-02T09:30:00",
                    "category": "Sightseeing",
                    "cost": 0
                  },
                  {
                    "title": "Paranthe Wali Gali Breakfast",
                    "activity_time": "2026-04-03T07:00:00",
                    "category": "Food",
                    "cost": 1200
                  }
                ]
              },
              {
                "city": "Agra",
                "start_date": "2026-04-05",
                "end_date": "2026-04-08",
                "activities": [
                  {
                    "title": "Taj Mahal Sunrise View",
                    "activity_time": "2026-04-06T05:45:00",
                    "category": "Sightseeing",
                    "cost": 500
                  },
                  {
                    "title": "Mughlai Feast in Agra",
                    "activity_time": "2026-04-07T19:00:00",
                    "category": "Food",
                    "cost": 4500
                  }
                ]
              }
            ]
        };
    }

    // Role-Based Authorization Guards
    function checkPageAuth() {
        const path = window.location.pathname;
        const user = JSON.parse(localStorage.getItem('user') || 'null');
        
        // Protect /admin routes
        if (path.startsWith('/admin') || path.includes('admin_panel')) {
            if (!user) {
                alert("Authentication Required: Please log in first.");
                window.location.href = '/login';
            } else if (user.role !== 'admin') {
                alert("Access Denied: Admins Only.");
                window.location.href = '/my-journeys';
            }
        }
        
        // Protect other dashboard routes from logged-out users
        const protectedPaths = ['/my-journeys', '/plan-trip', '/itinerary-budget', '/itinerary-builder', '/profile'];
        const isProtected = protectedPaths.some(p => path.startsWith(p) || path.includes(p.substring(1).replace('-', '_')));
        if (isProtected && !user) {
            alert("Session Expired: Please log in to continue.");
            window.location.href = '/login';
        }
    }

    // Navigation Calendar Widget
    let currentMonth = new Date().getMonth();
    let currentYear = new Date().getFullYear();

    async function fetchTripsForCalendar() {
        const user = JSON.parse(localStorage.getItem('user') || 'null');
        const userIdParam = user ? `?user_id=${user.id}` : '';
        try {
            const res = await originalFetch(`http://127.0.0.1:8000/api/trips${userIdParam}`);
            if (res.ok) {
                return await res.json();
            }
        } catch (e) {}
        return [getMockTrip(1), getMockTrip(2)];
    }

    function renderCalendar(trips) {
        const calDays = document.getElementById('cal-days');
        const calMonthYear = document.getElementById('cal-month-year');
        if (!calDays || !calMonthYear) return;

        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        calMonthYear.textContent = `${monthNames[currentMonth]} ${currentYear}`;
        
        calDays.innerHTML = '';
        
        const firstDay = new Date(currentYear, currentMonth, 1).getDay();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        
        for (let i = 0; i < firstDay; i++) {
            const emptyCell = document.createElement('div');
            emptyCell.className = 'py-1 text-transparent';
            calDays.appendChild(emptyCell);
        }
        
        for (let d = 1; d <= daysInMonth; d++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'py-1.5 text-xs font-semibold relative flex items-center justify-center cursor-pointer hover:bg-surface-dim rounded-full transition-all text-primary';
            dayCell.textContent = d;
            
            const dateObj = new Date(currentYear, currentMonth, d);
            
            const matchingTrip = trips.find(trip => {
                if (!trip.stops || trip.stops.length === 0) return false;
                
                let minDate = null;
                let maxDate = null;
                trip.stops.forEach(stop => {
                    const sD = new Date(stop.start_date);
                    const eD = new Date(stop.end_date);
                    if (!minDate || sD < minDate) minDate = sD;
                    if (!maxDate || eD > maxDate) maxDate = eD;
                });
                
                const checkDate = new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate());
                const tripStart = new Date(minDate.getFullYear(), minDate.getMonth(), minDate.getDate());
                const tripEnd = new Date(maxDate.getFullYear(), maxDate.getMonth(), maxDate.getDate());
                
                return checkDate >= tripStart && checkDate <= tripEnd;
            });
            
            if (matchingTrip) {
                dayCell.className = 'py-1.5 text-xs font-bold relative flex items-center justify-center cursor-pointer bg-secondary text-cloud-white rounded-full shadow-sm hover:opacity-90';
                dayCell.title = `${matchingTrip.title} (Active Trip)`;
                
                const dot = document.createElement('span');
                dot.className = 'absolute bottom-1 w-1 h-1 bg-cloud-white rounded-full';
                dayCell.appendChild(dot);
            }
            
            calDays.appendChild(dayCell);
        }
    }

    function toggleCalendarModal(linkEl) {
        let modal = document.getElementById('calendar-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'calendar-modal';
            modal.className = 'fixed top-16 right-4 md:right-16 z-[100] w-72 bg-cloud-white rounded-xl shadow-[0_8px_30px_rgba(0,0,0,0.12)] border border-outline-variant p-4 transition-all duration-300 opacity-0 -translate-y-2 pointer-events-none';
            modal.style.backgroundColor = '#ffffff';
            
            modal.innerHTML = `
                <div class="flex justify-between items-center mb-4">
                    <button id="cal-prev" class="p-1.5 hover:bg-surface-container rounded-md transition-colors text-primary flex items-center justify-center border border-outline-variant rounded">
                        <span class="material-symbols-outlined text-[18px]" style="font-variation-settings: 'FILL' 0, 'wght' 600;">chevron_left</span>
                    </button>
                    <h4 id="cal-month-year" class="font-bold text-sm text-primary" style="font-family: 'Hanken Grotesk', sans-serif;"></h4>
                    <button id="cal-next" class="p-1.5 hover:bg-surface-container rounded-md transition-colors text-primary flex items-center justify-center border border-outline-variant rounded">
                        <span class="material-symbols-outlined text-[18px]" style="font-variation-settings: 'FILL' 0, 'wght' 600;">chevron_right</span>
                    </button>
                </div>
                <div class="grid grid-cols-7 gap-1 text-center text-[11px] font-bold text-on-surface-variant mb-2" style="font-family: 'Hanken Grotesk', sans-serif;">
                    <div>Su</div><div>Mo</div><div>Tu</div><div>We</div><div>Th</div><div>Fr</div><div>Sa</div>
                </div>
                <div id="cal-days" class="grid grid-cols-7 gap-1 text-center" style="font-family: 'Hanken Grotesk', sans-serif;">
                </div>
            `;
            document.body.appendChild(modal);
            
            document.getElementById('cal-prev').addEventListener('click', async (e) => {
                e.stopPropagation();
                currentMonth--;
                if (currentMonth < 0) {
                    currentMonth = 11;
                    currentYear--;
                }
                const trips = await fetchTripsForCalendar();
                renderCalendar(trips);
            });
            
            document.getElementById('cal-next').addEventListener('click', async (e) => {
                e.stopPropagation();
                currentMonth++;
                if (currentMonth > 11) {
                    currentMonth = 0;
                    currentYear++;
                }
                const trips = await fetchTripsForCalendar();
                renderCalendar(trips);
            });
            
            document.addEventListener('click', (e) => {
                if (!modal.contains(e.target) && e.target !== linkEl && !linkEl.contains(e.target)) {
                    modal.classList.add('opacity-0', '-translate-y-2', 'pointer-events-none');
                }
            });
        }
        
        const isHidden = modal.classList.contains('pointer-events-none');
        if (isHidden) {
            fetchTripsForCalendar().then(trips => {
                if (trips && trips.length > 0 && trips[0].stops && trips[0].stops.length > 0) {
                    const tripDate = new Date(trips[0].stops[0].start_date);
                    currentMonth = tripDate.getMonth();
                    currentYear = tripDate.getFullYear();
                }
                renderCalendar(trips);
                modal.classList.remove('opacity-0', '-translate-y-2', 'pointer-events-none');
            });
        } else {
            modal.classList.add('opacity-0', '-translate-y-2', 'pointer-events-none');
        }
    }

    function initGlobalHooks() {
        // Run auth checks
        checkPageAuth();

        // Bind calendar link
        const links = document.querySelectorAll('a');
        links.forEach(link => {
            const text = link.textContent.trim().toLowerCase();
            if (text === 'calendar') {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    toggleCalendarModal(link);
                });
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initGlobalHooks);
    } else {
        initGlobalHooks();
    }
})();
