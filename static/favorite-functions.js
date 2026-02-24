/**
 * Favorite functionality for the shop
 * Handles AJAX requests for adding/removing products from favorites
 */

/**
 * Update the header favorite icon color based on favorites count
 * @param {number} favoritesCount - The current number of favorite products
 */
function updateHeaderFavoriteIcon(favoritesCount) {
    // Find the header favorite icon - target the path element inside the SVG
    const headerFavoriteIcon = document.querySelector('.u-header-icons .u-favorite-icon .u-svg-content path');

    if (headerFavoriteIcon) {
        // Update icon color based on actual favorites count
        if (favoritesCount > 0) {
            headerFavoriteIcon.style.fill = '#ff4444';
        } else {
            headerFavoriteIcon.style.fill = '#d47a17';
        }

        console.log('Header favorite icon updated. Favorites count:', favoritesCount);
    } else {
        console.warn('Header favorite icon not found');
    }
}

/**
 * Fetch the current favorites count from the server
 * @returns {Promise<number>} The current favorites count
 */
function fetchFavoritesCount() {
    return fetch('/shop/api/favorites/count/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            return data.favorites_count || 0;
        })
        .catch(error => {
            console.error('Error fetching favorites count:', error);
            return 0;
        });
}

/**
 * Initialize header favorite icon color based on current favorites count
 */
function initializeHeaderFavoriteIcon() {
    // Fetch the current favorites count and set the icon color accordingly
    fetchFavoritesCount().then(favoritesCount => {
        updateHeaderFavoriteIcon(favoritesCount);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize header favorite icon color based on current state
    initializeHeaderFavoriteIcon();

    // Handle favorite toggle with AJAX
    document.querySelectorAll('.favorite-form').forEach(formElement => {
        formElement.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const form = e.target;
            const productSlug = form.getAttribute('data-product-slug');
            const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
            const favoriteIcon = form.querySelector('.favorite-icon');

            // Show loading state
            favoriteIcon.style.opacity = '0.7';
            favoriteIcon.style.transform = 'scale(0.9)';

            fetch(`/shop/favorite/${productSlug}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({})
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Debug: Log the server response
                console.log('Server response:', data);

                // Fix: Correctly handle the state change based on server response
                if (data.is_favorited) {
                    // If server says it's now favorited, add the class
                    favoriteIcon.classList.add('favorited');
                    console.log('Added favorited class to icon');
                } else {
                    // If server says it's no longer favorited, remove the class
                    favoriteIcon.classList.remove('favorited');
                    console.log('Removed favorited class from icon');
                }

                // Debug: Log current classes
                // console.log('Current icon classes:', favoriteIcon.classList);

                // Fetch the updated favorites count and update the header icon
                fetchFavoritesCount().then(favoritesCount => {
                    updateHeaderFavoriteIcon(favoritesCount);
                });

                // Reload the page to update the favorites list
                if (window.location.pathname === '/shop/favorites/') {
                    window.location.reload();
                }

                // Reset loading state
                setTimeout(() => {
                    favoriteIcon.style.opacity = '1';
                    favoriteIcon.style.transform = '';
                }, 300);
            })
            .catch(error => {
                console.error('Error:', error);
                // Reset loading state on error
                favoriteIcon.style.opacity = '1';
                favoriteIcon.style.transform = '';
                // Show error to user
                alert('Ошибка при обновлении избранного. Пожалуйста, попробуйте позже.');
            });
        });
    });
});
