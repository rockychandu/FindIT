// FindIT Interactive UI, Left Sidebar & Animated Splash Handler

document.addEventListener('DOMContentLoaded', function() {
    // 1. STRICT SPLASH ANIMATION CONTROL (Initial Visit, Signup, Logout ONLY)
    const splash = document.getElementById('findit-splash-screen');
    if (splash) {
        const urlParams = new URLSearchParams(window.location.search);
        const hasSplashParam = urlParams.get('splash') === 'true';
        const isFirstEntry = !sessionStorage.getItem('findit_visited');

        if (isFirstEntry || hasSplashParam) {
            // Mark initial visit as completed
            sessionStorage.setItem('findit_visited', 'true');
            splash.style.display = 'flex';

            // Automatically fade out after 2 seconds (2000 ms)
            setTimeout(function() {
                splash.classList.add('fade-out');
                setTimeout(function() {
                    splash.style.display = 'none';
                }, 500);
            }, 2000);
        } else {
            // STRICT RULE: Hide splash immediately for normal page navigation / clicks!
            splash.style.display = 'none';
        }
    }

    // Trigger Splash Screen Animation on Sign Up / Register Form Submit
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm && splash) {
        registerForm.addEventListener('submit', function() {
            splash.style.display = 'flex';
            splash.classList.remove('fade-out');
        });
    }

    // Trigger Splash Screen Animation on Logout Click
    const logoutBtns = document.querySelectorAll('.logout-btn, a[href*="logout"]');
    logoutBtns.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (splash) {
                e.preventDefault();
                const redirectUrl = this.href;
                splash.style.display = 'flex';
                splash.classList.remove('fade-out');
                setTimeout(function() {
                    window.location.href = redirectUrl;
                }, 1600);
            }
        });
    });

    // Profile & Logins Top-Right Dropdown Menu Toggle Handler
    const profileDropdownBtn = document.getElementById('profile-dropdown-btn');
    const profileDropdownMenu = document.getElementById('profile-dropdown-menu');
    if (profileDropdownBtn && profileDropdownMenu) {
        profileDropdownBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = profileDropdownMenu.style.display === 'block';
            profileDropdownMenu.style.display = isVisible ? 'none' : 'block';
        });

        document.addEventListener('click', function(e) {
            if (profileDropdownMenu.style.display === 'block' && !profileDropdownMenu.contains(e.target) && e.target !== profileDropdownBtn) {
                profileDropdownMenu.style.display = 'none';
            }
        });
    }

    // 2. LEFT SIDEBAR MENU TOGGLE HANDLER
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarMenu = document.getElementById('sidebar-menu');

    if (sidebarToggle && sidebarMenu) {
        sidebarToggle.addEventListener('click', function() {
            sidebarMenu.classList.toggle('collapsed');
            sidebarMenu.classList.toggle('active');
        });
    }

    // Highlight active link in sidebar
    const currentPath = window.location.pathname;
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // 3. DYNAMIC PRIVATE VERIFICATION QUESTIONS BUILDER FOR LOST ITEM REPORT
    const addQuestionBtn = document.getElementById('add-question-btn');
    const questionsContainer = document.getElementById('questions-container');

    if (addQuestionBtn && questionsContainer) {
        addQuestionBtn.addEventListener('click', function() {
            const questionIndex = questionsContainer.children.length + 1;
            const questionGroup = document.createElement('div');
            questionGroup.className = 'qa-box form-group';
            questionGroup.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <strong>Private Verification Question #${questionIndex}</strong>
                    <button type="button" class="btn btn-danger btn-sm remove-question-btn">Remove</button>
                </div>
                <div class="form-group">
                    <label class="form-label">Question (Publicly visible to claimant):</label>
                    <input type="text" name="question[]" class="form-control" placeholder="e.g. What sticker is on the back or what color is inside?" required>
                </div>
                <div class="form-group" style="margin-bottom:0;">
                    <label class="form-label">Private Expected Answer (STRICTLY HIDDEN from public view):</label>
                    <input type="text" name="answer[]" class="form-control" placeholder="e.g. Blue Marvel sticker / Red velvet lining" required>
                </div>
            `;
            questionsContainer.appendChild(questionGroup);

            // Bind remove button
            const removeBtn = questionGroup.querySelector('.remove-question-btn');
            removeBtn.addEventListener('click', function() {
                questionGroup.remove();
            });
        });
    }

    // 4. IMAGE UPLOAD PREVIEW HANDLER
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.style.display = 'none';
            }
        });
    }
});
