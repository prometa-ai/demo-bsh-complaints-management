// Show/hide follow-up notes section based on checkbox
document.addEventListener('DOMContentLoaded', function() {
    // Handle follow-up checkbox for technical notes
    const followUpCheckbox = document.getElementById('followUpRequired');
    if (followUpCheckbox) {
        followUpCheckbox.addEventListener('change', function() {
            const followUpSection = document.getElementById('followUpNotesSection');
            if (followUpSection) {
                followUpSection.style.display = this.checked ? 'block' : 'none';
            }
        });
    }

    // Handle has notes checkbox on complaint listing page
    const hasNotesCheck = document.getElementById('hasNotesCheck');
    if (hasNotesCheck) {
        hasNotesCheck.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            
            // Preserve page parameter if it exists but reset to 1 when filter changes
            if (currentUrl.searchParams.has('page')) {
                currentUrl.searchParams.set('page', '1');
            }
            
            // Set or remove has_notes parameter
            if (this.checked) {
                currentUrl.searchParams.set('has_notes', 'true');
            } else {
                currentUrl.searchParams.delete('has_notes');
            }
            
            // Ensure all other parameters are maintained
            // No need to explicitly handle: country, status, warranty, brand, ai_category, search, time_period
            // as they're already in the URL and are not being modified
            
            window.location.href = currentUrl.toString();
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Add safe event listeners to view buttons
    document.querySelectorAll('a[href*="/complaints/"]').forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('View button clicked:', this.href);
            // No return value to avoid Promise issues
        });
    });
});

// Global error handler for unhandled promises
window.addEventListener('unhandledrejection', function(event) {
    console.log('Handled unresolved promise:', event.reason);
    event.preventDefault();
}); 