async function createLocation(event) {
    event.preventDefault();

    const button = document.getElementById('create-location-button');
    const buttonOriginalText = button.textContent;

    const name = document.getElementById('add-location-name').value.trim();
    const description = document.getElementById('add-location-description').value.trim();
    const latitude = parseFloat(document.getElementById('add-location-latitude').value);
    const longitude = parseFloat(document.getElementById('add-location-longitude').value);

    if (!name || !description) {
        alert('Please fill in all fields correctly.');
        return;
    }

    try {
        button.disabled = true;
        button.textContent = button.getAttribute('data-loading') || '+ CREATING...';

        const response = await fetch('/locations/add', {
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


async function editLocation(event) {
    event.preventDefault();

    const button = document.getElementById('save-location-button');
    const buttonOriginalText = button.textContent;

    const locationId = parseInt(document.getElementById('edit-location-id').value);
    const name = document.getElementById('edit-location-name').value.trim();
    const description = document.getElementById('edit-location-description').value.trim();
    const latitude = parseFloat(document.getElementById('edit-location-latitude').value);
    const longitude = parseFloat(document.getElementById('edit-location-longitude').value);

    if (!name || !description) {
        alert('Please fill in all fields correctly.');
        return;
    }

    try {
        button.disabled = true;
        button.textContent = button.getAttribute('data-loading') || 'SAVING...';

        const response = await fetch(`/locations/edit/${locationId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, description, latitude, longitude }),
        });

        if (response.ok) {
            alert('Location updated successfully!');
            window.location.reload();
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.error}`);
        }

    } catch (error) {
        console.error('Error updating location:', error);
        alert('An error occurred while updating the location.');

    } finally {
        button.disabled = false;
        button.textContent = buttonOriginalText;
    }
}


async function deleteLocation(locationId, locationName) {
    if (!confirm(`Are you sure you want to delete "${locationName}"?`)) {
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


async function toggleAllowRegistration() {
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


let currentDeleteHandler = null;


function showLocationList() {
    const formContainer = document.getElementById('edit-location-container');
    const listContainer = document.getElementById('location-list-container');

    if (formContainer) formContainer.style.display = 'none';
    if (listContainer) listContainer.style.display = 'flex';
}


function showEditLocationForm(location) {
    const formContainer = document.getElementById('edit-location-container');
    if (!formContainer) return;

    // populate form fields
    document.getElementById('edit-location-id').value = location.id || '';
    document.getElementById('edit-location-name').value = location.name || '';
    document.getElementById('edit-location-description').value = location.description || '';
    document.getElementById('edit-location-latitude').value = parseFloat(location.latitude);
    document.getElementById('edit-location-longitude').value = parseFloat(location.longitude);

    // remove any existing event listeners first to prevent duplicates
    const saveButton = document.getElementById('save-location-button');
    const cancelButton = document.getElementById('cancel-edit-location-button');
    const deleteButton = document.getElementById('delete-location-button');

    if (saveButton) saveButton.removeEventListener('click', editLocation);
    if (cancelButton) cancelButton.removeEventListener('click', showLocationList);
    if (deleteButton && currentDeleteHandler) {
        deleteButton.removeEventListener('click', currentDeleteHandler);
        currentDeleteHandler = null;
    }

    // create new delete handler function
    currentDeleteHandler = () => {
        deleteLocation(location.id, location.name);
    };

    // set up new event listeners
    saveButton.addEventListener('click', editLocation);
    cancelButton.addEventListener('click', showLocationList);
    deleteButton.addEventListener('click', currentDeleteHandler);

    // hide location list, show form
    document.getElementById('location-list-container').style.display = 'none';
    formContainer.style.display = 'block';
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

document.getElementById('allow-registration').addEventListener('change', toggleAllowRegistration);
document.getElementById('add-location-form').addEventListener('submit', createLocation);
document.querySelectorAll('.edit-location-button').forEach(button => {
    button.addEventListener('click', async () => {
        try {
            const response = await fetch(`/locations/get/${button.getAttribute('data-location-id')}`);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const location = await response.json();
            showEditLocationForm(location);
        } catch (error) {
            console.error('Error fetching location data:', error);
            alert('An error occurred while fetching location data.');
        }
    });
});
document.querySelectorAll('.delete-location-button').forEach(button => {
    button.addEventListener('click', () => {
        const locationId = parseInt(button.attributes.getNamedItem('data-location-id').value);
        const locationName = button.attributes.getNamedItem('data-location-name').value;
        deleteLocation(locationId, locationName);
    });
});

if (nextButton) nextButton.addEventListener('click', goToNextPage);
if (prevButton) prevButton.addEventListener('click', goToPrevPage);
