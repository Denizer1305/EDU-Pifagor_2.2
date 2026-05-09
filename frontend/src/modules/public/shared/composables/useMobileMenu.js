import { onBeforeUnmount, onMounted, ref } from "vue";

const MOBILE_MENU_BODY_CLASS = "is-mobile-menu-open";

export function useMobileMenu() {
    const isMobileMenuOpen = ref(false);

    function openMobileMenu() {
        isMobileMenuOpen.value = true;
        document.body.classList.add(MOBILE_MENU_BODY_CLASS);
    }

    function closeMobileMenu() {
        isMobileMenuOpen.value = false;
        document.body.classList.remove(MOBILE_MENU_BODY_CLASS);
    }

    function toggleMobileMenu() {
        if (isMobileMenuOpen.value) {
            closeMobileMenu();
            return;
        }

        openMobileMenu();
    }

    function handleEscape(event) {
        if (event.key === "Escape") {
            closeMobileMenu();
        }
    }

    onMounted(() => {
        window.addEventListener("keydown", handleEscape);
    });

    onBeforeUnmount(() => {
        closeMobileMenu();
        window.removeEventListener("keydown", handleEscape);
    });

    return {
        isMobileMenuOpen,
        openMobileMenu,
        closeMobileMenu,
        toggleMobileMenu,
    };
}
