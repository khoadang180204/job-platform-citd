document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.style.display = 'none';
            });
        }

        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });

    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const menu = this.nextElementSibling;
            if (menu && menu.classList.contains('dropdown-menu')) {
                menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });

    document.addEventListener('click', function(event) {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            if (!dropdown.parentElement.contains(event.target)) {
                dropdown.style.display = 'none';
            }
        });
    });
});


document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            document.querySelector(href).scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Kiểm tra form
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#dc3545';
            isValid = false;
        } else {
            input.style.borderColor = '';
        }
    });

    return isValid;
}

// Lưu job vào danh sách yêu thích (client-side)
function saveJob(jobId) {
    let saved = JSON.parse(localStorage.getItem('savedJobs')) || [];
    
    if (saved.includes(jobId)) {
        saved = saved.filter(id => id !== jobId);
    } else {
        saved.push(jobId);
    }
    
    localStorage.setItem('savedJobs', JSON.stringify(saved));
    
    // Update UI
    const btn = event.target;
    btn.classList.toggle('saved');
    btn.textContent = saved.includes(jobId) ? '💾 Saved' : '💾 Save';
}

// Kiểm tra job đã lưu chưa
function isSaved(jobId) {
    const saved = JSON.parse(localStorage.getItem('savedJobs')) || [];
    return saved.includes(jobId);
}

// Định dạng tiền tệ
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}