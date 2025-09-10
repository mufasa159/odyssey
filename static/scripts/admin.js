async function createLocation(event) {
    event.preventDefault();

    const button = document.getElementById('create-location-button');
    const buttonOriginalText = button.textContent;

    const name = document.getElementById('location-name').value.trim();
    const description = document.getElementById('location-description').value.trim();
    const latitude = parseFloat(document.getElementById('location-latitude').value);
    const longitude = parseFloat(document.getElementById('location-longitude').value);

    if (!name || !description) {
        alert('Please fill in all fields correctly.');
        return;
    }

    try {
        button.disabled = true;
        button.textContent = button.getAttribute('data-loading') || '+ CREATING...';

        const response = await fetch('/locations/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description, latitude, longitude }),
        });

        if (response.ok) {
            alert('Location added successfully!');
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.error}`);
        }

    } catch (error) {
        console.error('Error adding location:', error);
        alert('An error occurred while adding the location.');

    } finally {
        button.disabled = false;
        button.textContent = buttonOriginalText;
    }
}


async function deleteLocation(locationId) {
    if (!confirm('Are you sure you want to delete this location?')) {
        return;
    }

    try {
        const response = await fetch(`/locations/delete/${locationId}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            alert('Location deleted successfully!');
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error deleting location:', error);
        alert('An error occurred while deleting the location.');
    }
}


async function toggleRegistration() {
    const checkbox = document.getElementById('allow-registration');
    try {
        const response = await fetch('/config/allow-registration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ allow: checkbox.checked }),
        });

        if (response.ok) {
            const data = await response.json();
            alert(`Registration is now ${data.allow_registration ? 'enabled' : 'disabled'}.`);

        } else {
            checkbox.checked = !checkbox.checked;
            const errorData = await response.json();
            alert(`Error: ${errorData.error}`);
        }

    } catch (error) {
        checkbox.checked = !checkbox.checked;
        console.error('Error toggling registration:', error);
        alert('An error occurred while updating the registration setting.');
    }
}

// ---- Pagination Logic ---- //

const nextButton = document.getElementById('locations-pagination-next');
const prevButton = document.getElementById('locations-pagination-prev');

let currentPage = 1;
let totalPages = 0;

function initializePagination() {
    const pages = document.querySelectorAll('.location-list');
    totalPages = pages.length;
    currentPage = 1;

    updatePaginationButtons();
}

function updatePaginationButtons() {
    if (prevButton) {
        prevButton.disabled = currentPage <= 1;
    }
    if (nextButton) {
        nextButton.disabled = currentPage >= totalPages;
    }
}

function openLocationListPage(pageNum) {
    if (pageNum < 1 || pageNum > totalPages) {
        return;
    }

    // hide all pages
    const allPages = document.querySelectorAll('.location-list');
    allPages.forEach(page => {
        page.style.display = 'none';
    });

    // show the target page
    const targetPage = document.querySelector(`.location-list[data-page="${pageNum}"]`);
    if (targetPage) {
        targetPage.style.display = 'block';
        currentPage = pageNum;
        updatePaginationButtons();
    }
}

function goToNextPage() {
    if (currentPage < totalPages) {
        openLocationListPage(currentPage + 1);
    }
}

function goToPrevPage() {
    if (currentPage > 1) {
        openLocationListPage(currentPage - 1);
    }
}

initializePagination();


// ---- All Event Listeners ---- //

document.getElementById('allow-registration').addEventListener('change', toggleRegistration);
document.getElementById('add-location-form').addEventListener('submit', createLocation);
document.querySelectorAll('.delete-location-button').forEach(button => {
    button.addEventListener('click', () => {
        const locationId = parseInt(button.attributes.getNamedItem('data-location-id').value);
        deleteLocation(locationId);
    });
});

if (nextButton) nextButton.addEventListener('click', goToNextPage);
if (prevButton) prevButton.addEventListener('click', goToPrevPage);
