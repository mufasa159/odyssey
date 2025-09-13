const loadStartTime = Date.now();

// initialize map
const map = L.map('map', {
    center: [20, 0],
    zoom: 2,
    minZoom: 2,
    maxZoom: 18,
    worldCopyJump: true
});

// dark mode
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

// custom fallback marker icon
L.Marker.prototype.options.icon = L.icon({
    iconUrl: "static/leaflet-1.9.4/images/marker-icon.svg",
    shadowUrl: "static/leaflet-1.9.4/images/marker-shadow.png"
});

// custom marker icon (CSS-based)
const customIcon = L.divIcon({
    className: 'custom-marker',
    iconSize: [30, 30],
    iconAnchor: [15, 30],
    popupAnchor: [0, -30]
});

fetch('/locations')
    .then(response => response.json())
    .then(async data => {

        const allBounds = [];

        for (const location of data) {

            // create popup content
            const popupDiv = document.createElement('div');
            popupDiv.className = 'location-popup';

            const titleElement = document.createElement('h3');
            titleElement.textContent = location.name;
            popupDiv.appendChild(titleElement);

            if (location.description) {
                const descriptionElement = document.createElement('p');
                descriptionElement.innerHTML = location.description;
                popupDiv.appendChild(descriptionElement);
            }

            try {
                const geocoded = location.boundary;

                if (geocoded && geocoded.geojson) {
                    const polygon = L.geoJSON(geocoded.geojson, {
                        style: {
                            color: '#63FFDA',
                            weight: 3,
                            opacity: 0.8,
                            fillColor: '#63FFDA',
                            fillOpacity: 0.1
                        }
                    }).addTo(map);

                    polygon.bindPopup(popupDiv, { closeButton: false });
                    const bounds = polygon.getBounds();
                    allBounds.push(bounds.getCenter());

                } else if (location.latitude && location.longitude) {
                    const marker = L.marker([
                        parseFloat(location.latitude),
                        parseFloat(location.longitude)
                    ], {
                        icon: customIcon,
                        title: location.name
                    }).addTo(map);

                    marker.bindPopup(popupDiv, { closeButton: false });
                    allBounds.push([
                        parseFloat(location.latitude),
                        parseFloat(location.longitude)
                    ]);
                }

            } catch (error) {
                console.error(`Failed to geocode "${location.name}":`, error);
            }
        }

        // fit map to show all locations
        if (allBounds.length > 0) {
            const group = new L.featureGroup(allBounds.map(coords =>
                L.marker(coords)
            ));
            map.fitBounds(group.getBounds().pad(0.1));
        }

        const hidePreloader = () => {
            const preloader = document.getElementById('preloader');
            if (preloader) {
                preloader.style.display = 'none';
            }
        };

        // show loading screen for at least 1 second because it looks cool
        const elapsedTime = Date.now() - loadStartTime;
        const minDisplayTime = 1000;

        if (elapsedTime >= minDisplayTime) {
            hidePreloader();
        } else {
            setTimeout(hidePreloader, minDisplayTime - elapsedTime);
        }
    })
    .catch(error => {
        console.error('Error loading locations:', error);
        alert('An error occurred while loading locations.');
    });
