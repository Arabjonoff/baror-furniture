document.addEventListener('DOMContentLoaded', function () {
    function showToast(text) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = text;
        document.body.appendChild(toast);
        requestAnimationFrame(function () {
            toast.classList.add('visible');
        });
        setTimeout(function () {
            toast.classList.remove('visible');
            setTimeout(function () {
                toast.remove();
            }, 300);
        }, 2500);
    }

    function updateCartCount(count) {
        const cartCountEl = document.getElementById('cart-count');
        if (cartCountEl) {
            cartCountEl.textContent = count;
        }
    }

    document.querySelectorAll('.ajax-add-to-cart-form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const formData = new FormData(form);
            const button = form.querySelector('button[type="submit"]');
            const originalText = button ? button.textContent : '';

            if (button) {
                button.disabled = true;
                button.classList.add('is-loading');
                button.textContent = "Qo'shilmoqda...";
            }

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (data.ok) {
                        updateCartCount(data.cart_count);
                        showToast(data.message || "Savatga qo'shildi");
                    }
                })
                .catch(function () {
                    showToast("Xatolik yuz berdi, qayta urinib ko'ring.");
                })
                .finally(function () {
                    if (button) {
                        button.disabled = false;
                        button.classList.remove('is-loading');
                        button.textContent = originalText;
                    }
                });
        });
    });

    // Sevimlilar: yurakcha tugmasi AJAX orqali qo'shadi/o'chiradi
    document.querySelectorAll('.ajax-wishlist-form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const button = form.querySelector('.wishlist-btn');

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (!data.ok) {
                        return;
                    }
                    const wishlistCountEl = document.getElementById('wishlist-count');
                    if (wishlistCountEl) {
                        wishlistCountEl.textContent = data.wishlist_count;
                    }
                    if (button) {
                        button.classList.toggle('is-active', data.added);
                        button.setAttribute('aria-pressed', data.added ? 'true' : 'false');
                        button.setAttribute('aria-label', data.added ? "Sevimlilardan o'chirish" : "Sevimlilarga qo'shish");
                        if (data.added) {
                            button.classList.add('is-popping');
                            setTimeout(function () {
                                button.classList.remove('is-popping');
                            }, 400);
                        }
                    }
                    showToast(data.message);

                    // Sevimlilar sahifasida o'chirilgan mahsulot kartochkasini yo'qotamiz
                    if (!data.added && window.location.pathname.indexOf('/sevimlilar') === 0) {
                        const card = form.closest('.product-card');
                        if (card) {
                            card.remove();
                        }
                        if (data.wishlist_count === 0) {
                            window.location.reload();
                        }
                    }
                })
                .catch(function () {
                    showToast("Xatolik yuz berdi, qayta urinib ko'ring.");
                });
        });
    });

    const savedAddressSelect = document.getElementById('id_saved_address');
    if (savedAddressSelect) {
        savedAddressSelect.addEventListener('change', function () {
            const selected = savedAddressSelect.options[savedAddressSelect.selectedIndex];
            const regionField = document.getElementById('id_region');
            const districtField = document.getElementById('id_district');
            const addressField = document.getElementById('id_address');

            if (regionField && selected.dataset.region) {
                regionField.value = selected.dataset.region;
            }
            if (districtField && selected.dataset.district) {
                districtField.value = selected.dataset.district;
            }
            if (addressField && selected.dataset.street) {
                addressField.value = selected.dataset.street;
            }
        });
    }

    document.querySelectorAll('.color-swatches').forEach(function (swatchGroup) {
        const form = swatchGroup.closest('.product-info').querySelector('.selected-color-input');
        swatchGroup.querySelectorAll('.color-swatch').forEach(function (swatch) {
            swatch.addEventListener('click', function () {
                swatchGroup.querySelectorAll('.color-swatch').forEach(function (s) {
                    s.classList.remove('selected');
                });
                swatch.classList.add('selected');
                if (form) {
                    form.value = swatch.dataset.colorName;
                }
            });
        });
    });

    // Mahsulot galereyasi: kichik rasm almashtirish + to'liq ekranda ko'rish (lightbox)
    const mainImage = document.getElementById('mainImage');
    const lightbox = document.getElementById('lightbox');
    if (mainImage && lightbox) {
        const thumbs = Array.from(document.querySelectorAll('.product-gallery-thumbs .thumb'));
        const images = thumbs.length ? thumbs.map(function (thumb) { return thumb.src; }) : [mainImage.src];
        const lightboxImage = document.getElementById('lightboxImage');
        const lightboxPrev = document.getElementById('lightboxPrev');
        const lightboxNext = document.getElementById('lightboxNext');
        const lightboxClose = document.getElementById('lightboxClose');
        let currentImageIndex = 0;

        function openLightbox(index) {
            if (!images.length || !images[0]) {
                return;
            }
            currentImageIndex = index;
            lightboxImage.src = images[currentImageIndex];
            lightbox.classList.add('is-open');
            document.body.style.overflow = 'hidden';
        }

        function closeLightbox() {
            lightbox.classList.remove('is-open');
            document.body.style.overflow = '';
        }

        function showRelativeImage(delta) {
            currentImageIndex = (currentImageIndex + delta + images.length) % images.length;
            lightboxImage.src = images[currentImageIndex];
        }

        mainImage.addEventListener('click', function () {
            const index = images.indexOf(mainImage.src);
            openLightbox(index >= 0 ? index : 0);
        });

        thumbs.forEach(function (thumb, index) {
            thumb.addEventListener('click', function () {
                mainImage.src = thumb.src;
                thumbs.forEach(function (t) {
                    t.classList.remove('is-active');
                });
                thumb.classList.add('is-active');
            });
        });

        if (lightboxClose) {
            lightboxClose.addEventListener('click', closeLightbox);
        }
        if (lightboxPrev) {
            lightboxPrev.addEventListener('click', function () {
                showRelativeImage(-1);
            });
        }
        if (lightboxNext) {
            lightboxNext.addEventListener('click', function () {
                showRelativeImage(1);
            });
        }
        if (images.length <= 1) {
            if (lightboxPrev) lightboxPrev.style.display = 'none';
            if (lightboxNext) lightboxNext.style.display = 'none';
        }

        lightbox.addEventListener('click', function (event) {
            if (event.target === lightbox) {
                closeLightbox();
            }
        });

        document.addEventListener('keydown', function (event) {
            if (!lightbox.classList.contains('is-open')) {
                return;
            }
            if (event.key === 'Escape') {
                closeLightbox();
            } else if (event.key === 'ArrowLeft') {
                showRelativeImage(-1);
            } else if (event.key === 'ArrowRight') {
                showRelativeImage(1);
            }
        });
    }

    // Mobil hamburger menyu
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const mainNav = document.getElementById('mainNav');
    if (hamburgerBtn && mainNav) {
        hamburgerBtn.addEventListener('click', function () {
            const isOpen = mainNav.classList.toggle('is-open');
            hamburgerBtn.classList.toggle('is-active', isOpen);
            hamburgerBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
    }

    // Bosh sahifa banner/slayder
    const heroSlider = document.getElementById('heroSlider');
    if (heroSlider) {
        const slides = heroSlider.querySelectorAll('.hero-slide');
        const dots = heroSlider.querySelectorAll('.hero-dot');
        const prevBtn = document.getElementById('heroPrev');
        const nextBtn = document.getElementById('heroNext');
        let currentIndex = 0;
        let autoplayTimer = null;

        function goToSlide(index) {
            slides[currentIndex].classList.remove('is-active');
            dots[currentIndex].classList.remove('is-active');
            currentIndex = (index + slides.length) % slides.length;
            slides[currentIndex].classList.add('is-active');
            dots[currentIndex].classList.add('is-active');
        }

        function startAutoplay() {
            autoplayTimer = setInterval(function () {
                goToSlide(currentIndex + 1);
            }, 5000);
        }

        function resetAutoplay() {
            clearInterval(autoplayTimer);
            startAutoplay();
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                goToSlide(currentIndex - 1);
                resetAutoplay();
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                goToSlide(currentIndex + 1);
                resetAutoplay();
            });
        }
        dots.forEach(function (dot, index) {
            dot.addEventListener('click', function () {
                goToSlide(index);
                resetAutoplay();
            });
        });

        if (slides.length > 1) {
            startAutoplay();
        }
    }
});
