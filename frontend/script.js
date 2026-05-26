/* ═══════════════════════════════════════
   ReviewMind AI — Landing Page Scripts
   Scroll animations & interactions
   ═══════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    // ── Navbar scroll effect ──
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.scrollY;
        if (currentScroll > 40) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        lastScroll = currentScroll;
    }, { passive: true });

    // ── Mobile menu toggle ──
    const mobileToggle = document.getElementById('mobile-toggle');
    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            const links = document.querySelector('.navbar__links');
            links.style.display = links.style.display === 'flex' ? 'none' : 'flex';
            links.style.flexDirection = 'column';
            links.style.position = 'absolute';
            links.style.top = '100%';
            links.style.left = '0';
            links.style.right = '0';
            links.style.padding = '20px';
            links.style.background = 'rgba(10, 10, 15, 0.95)';
            links.style.backdropFilter = 'blur(20px)';
            links.style.borderBottom = '1px solid rgba(255,255,255,0.08)';
        });
    }

    // ── Scroll-triggered animations ──
    const observerOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -60px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                // Stagger animation for grid items
                const delay = entry.target.closest('.features__grid')
                    ? Array.from(entry.target.parentNode.children).indexOf(entry.target) * 100
                    : 0;

                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, delay);

                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe all animatable elements
    document.querySelectorAll('.feature-card, .step, .demo__card, [data-aos]').forEach(el => {
        observer.observe(el);
    });

    // ── Counter animation for stats ──
    const counters = document.querySelectorAll('[data-count]');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-count'));
                let current = 0;
                const increment = target / 30;
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        el.textContent = target;
                        clearInterval(timer);
                    } else {
                        el.textContent = Math.ceil(current);
                    }
                }, 40);
                counterObserver.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(c => counterObserver.observe(c));

    // ── Smooth scroll for anchor links ──
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ── Typing effect for hero badge ──
    const badge = document.querySelector('.hero__badge');
    if (badge) {
        badge.style.opacity = '0';
        setTimeout(() => {
            badge.style.transition = 'opacity 0.6s ease';
            badge.style.opacity = '1';
        }, 200);
    }

});
