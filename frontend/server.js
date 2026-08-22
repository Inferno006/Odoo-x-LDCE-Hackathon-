const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files (images, assets etc) relative to frontend directory root
app.use(express.static(path.join(__dirname)));

// Clean routing mapping to the various code.html pages
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'explore_globetrotter', 'code.html'));
});

app.get('/explore', (req, res) => {
    res.sendFile(path.join(__dirname, 'explore_globetrotter', 'code.html'));
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'login_globetrotter', 'code.html'));
});

app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, 'register_globetrotter', 'code.html'));
});

app.get('/my-journeys', (req, res) => {
    res.sendFile(path.join(__dirname, 'my_journeys_globetrotter', 'code.html'));
});

app.get('/plan-trip', (req, res) => {
    res.sendFile(path.join(__dirname, 'plan_a_trip_globetrotter', 'code.html'));
});

app.get('/itinerary-budget', (req, res) => {
    res.sendFile(path.join(__dirname, 'itinerary_budget_globetrotter', 'code.html'));
});

app.get('/itinerary-builder', (req, res) => {
    res.sendFile(path.join(__dirname, 'itinerary_builder_globetrotter', 'code.html'));
});

app.get('/profile', (req, res) => {
    res.sendFile(path.join(__dirname, 'profile_globetrotter', 'code.html'));
});

app.get('/search', (req, res) => {
    res.sendFile(path.join(__dirname, 'search_globetrotter', 'code.html'));
});

app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'admin_panel_globetrotter', 'code.html'));
});

app.get('/community', (req, res) => {
    res.sendFile(path.join(__dirname, 'community_globetrotter', 'code.html'));
});

app.listen(PORT, () => {
    console.log(`GlobeTrotter frontend app listening at http://localhost:${PORT}`);
});
