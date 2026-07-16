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

    function getCsrfToken(scope) {
        const el = (scope || document).querySelector('input[name="csrfmiddlewaretoken"]');
        return el ? el.value : '';
    }

    function cartFetch(url, params, token) {
        const body = new URLSearchParams(params || {});
        if (token) body.append('csrfmiddlewaretoken', token);
        return fetch(url, {
            method: 'POST',
            body: body,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        }).then(function (r) { return r.json(); });
    }

    // Mahsulot kartochkasida "Savatga qo'shish" tugmasi <-> miqdor stepperi almashuvi
    function setCardState(control, inCart, quantity) {
        const form = control.querySelector('.product-card-form');
        const stepper = control.querySelector('.product-card-stepper');
        if (!form || !stepper) return;
        if (inCart) {
            if (typeof quantity !== 'undefined') {
                stepper.querySelector('.qty-input').value = quantity;
            }
            form.hidden = true;
            stepper.hidden = false;
        } else {
            form.hidden = false;
            stepper.hidden = true;
        }
    }

    document.querySelectorAll('.ajax-add-to-cart-form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const button = form.querySelector('button[type="submit"]');
            const control = form.closest('.product-card-cart');

            if (button) {
                button.disabled = true;
                button.classList.add('is-loading');
            }

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    if (!data.ok) return;
                    updateCartCount(data.cart_count);
                    if (control) {
                        // Kartochkada tugmani miqdor stepperiga aylantiramiz
                        setCardState(control, true, data.item_quantity || 1);
                    } else {
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
                    }
                });
        });
    });

    // Mahsulot kartochkasidagi miqdor stepperi (+/-); 1 dan pastga tushsa savatdan chiqadi
    document.querySelectorAll('.product-card-cart').forEach(function (control) {
        const stepper = control.querySelector('.product-card-stepper');
        if (!stepper) return;
        const input = stepper.querySelector('.qty-input');
        const stock = parseInt(control.dataset.stock, 10) || 1;
        const token = getCsrfToken(control);

        function setQuantity(quantity) {
            if (stepper.dataset.loading === 'true') return;
            quantity = Math.min(quantity, stock);
            stepper.dataset.loading = 'true';
            stepper.classList.add('is-loading');

            function done() {
                stepper.dataset.loading = 'false';
                stepper.classList.remove('is-loading');
            }

            if (quantity <= 0) {
                cartFetch(control.dataset.removeUrl, {}, token)
                    .then(function (data) {
                        if (data.ok) {
                            setCardState(control, false);
                            updateCartCount(data.cart_count);
                        }
                    })
                    .catch(function () { showToast("Xatolik yuz berdi, qayta urinib ko'ring."); })
                    .finally(done);
                return;
            }

            cartFetch(control.dataset.updateUrl, { quantity: quantity }, token)
                .then(function (data) {
                    if (data.ok && typeof data.quantity !== 'undefined') {
                        input.value = data.quantity;
                        updateCartCount(data.cart_count);
                    }
                })
                .catch(function () { showToast("Xatolik yuz berdi, qayta urinib ko'ring."); })
                .finally(done);
        }

        stepper.addEventListener('click', function (event) {
            const btn = event.target.closest('.qty-btn');
            if (!btn) return;
            const current = parseInt(input.value, 10) || 1;
            setQuantity(current + (btn.dataset.action === 'inc' ? 1 : -1));
        });
        input.addEventListener('change', function () {
            const v = parseInt(input.value, 10);
            setQuantity(isNaN(v) ? 1 : v);
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

    // Savat sahifasi: miqdor stepperi, o'chirish va jonli yig'indi (AJAX)
    const cartPage = document.getElementById('cartPage');
    if (cartPage) {
        const csrfInput = cartPage.querySelector('input[name="csrfmiddlewaretoken"]');
        const csrfToken = csrfInput ? csrfInput.value : '';

        function formatMoney(value) {
            const n = Math.round(Number(value) || 0);
            return n.toLocaleString('en-US').replace(/,/g, ' ');
        }

        function applySummary(data) {
            const subtotalEl = document.getElementById('cartSubtotal');
            const discountEl = document.getElementById('cartDiscount');
            const discountLine = document.getElementById('cartDiscountLine');
            const finalEl = document.getElementById('cartFinalTotal');
            const countEl = document.getElementById('cartItemsCount');

            if (subtotalEl) subtotalEl.textContent = formatMoney(data.subtotal) + " so'm";
            if (finalEl) finalEl.textContent = formatMoney(data.final_total);
            if (discountLine) {
                if (data.discount > 0) {
                    if (discountEl) discountEl.textContent = formatMoney(data.discount);
                    discountLine.hidden = false;
                } else {
                    discountLine.hidden = true;
                }
            }
            if (countEl) countEl.textContent = data.cart_count;
            updateCartCount(data.cart_count);
        }

        function postCart(url, params) {
            const body = new URLSearchParams(params);
            body.append('csrfmiddlewaretoken', csrfToken);
            return fetch(url, {
                method: 'POST',
                body: body,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            }).then(function (r) { return r.json(); });
        }

        function updateQuantity(item, quantity) {
            const stepper = item.querySelector('.qty-stepper');
            const input = item.querySelector('.qty-input');
            const stock = parseInt(item.dataset.stock, 10) || 1;
            quantity = Math.max(1, Math.min(quantity, stock));
            if (stepper.dataset.loading === 'true') return;
            stepper.dataset.loading = 'true';
            stepper.classList.add('is-loading');

            postCart(item.dataset.updateUrl, {
                quantity: quantity,
                color: item.dataset.color || '',
            })
                .then(function (data) {
                    if (!data.ok) return;
                    if (typeof data.quantity !== 'undefined') input.value = data.quantity;
                    const totalEl = item.querySelector('.cart-item-total');
                    if (totalEl && typeof data.item_total !== 'undefined') {
                        totalEl.textContent = formatMoney(data.item_total) + " so'm";
                    }
                    applySummary(data);
                })
                .catch(function () {
                    showToast("Xatolik yuz berdi, qayta urinib ko'ring.");
                })
                .finally(function () {
                    stepper.dataset.loading = 'false';
                    stepper.classList.remove('is-loading');
                });
        }

        function removeItem(item) {
            item.classList.add('is-removing');
            postCart(item.dataset.removeUrl, { color: item.dataset.color || '' })
                .then(function (data) {
                    if (!data.ok) {
                        item.classList.remove('is-removing');
                        return;
                    }
                    setTimeout(function () {
                        item.remove();
                        if (data.empty) {
                            window.location.reload();
                        } else {
                            applySummary(data);
                        }
                    }, 220);
                    showToast("Mahsulot savatdan o'chirildi.");
                })
                .catch(function () {
                    item.classList.remove('is-removing');
                    showToast("Xatolik yuz berdi, qayta urinib ko'ring.");
                });
        }

        cartPage.addEventListener('click', function (event) {
            const stepBtn = event.target.closest('.qty-btn');
            if (stepBtn) {
                const item = stepBtn.closest('.cart-item');
                const input = item.querySelector('.qty-input');
                const current = parseInt(input.value, 10) || 1;
                const delta = stepBtn.dataset.action === 'inc' ? 1 : -1;
                updateQuantity(item, current + delta);
                return;
            }
            const removeBtn = event.target.closest('.cart-item-remove');
            if (removeBtn) {
                removeItem(removeBtn.closest('.cart-item'));
            }
        });

        cartPage.querySelectorAll('.qty-input').forEach(function (input) {
            input.addEventListener('change', function () {
                const item = input.closest('.cart-item');
                const value = parseInt(input.value, 10);
                updateQuantity(item, isNaN(value) ? 1 : value);
            });
        });
    }

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
