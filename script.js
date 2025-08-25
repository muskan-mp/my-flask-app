document.addEventListener('DOMContentLoaded', function() {
    // Copy to clipboard functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('fa-copy') || e.target.classList.contains('copy-btn')) {
            const copyBtn = e.target.closest('.copy-btn');
            const url = copyBtn.getAttribute('data-url');
            
            navigator.clipboard.writeText(url).then(() => {
                const originalHTML = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                copyBtn.style.color = '#28a745';
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalHTML;
                    copyBtn.style.color = '';
                }, 2000);
            });
        }
    });
    
    // Form validation
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const longUrl = document.getElementById('long_url');
            if (!longUrl.value) {
                e.preventDefault();
                alert('Please enter a URL');
                longUrl.focus();
            }
        });
    }
    
    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});