import { computed, onMounted, ref } from "vue";

const THEME_STORAGE_KEY = "pifagor-theme";
const LIGHT_THEME = "light";
const DARK_THEME = "dark";

function getPreferredTheme() {
    if (typeof window === "undefined") {
        return LIGHT_THEME;
    }

    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);

    if ([LIGHT_THEME, DARK_THEME].includes(savedTheme)) {
        return savedTheme;
    }

    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

    return prefersDark ? DARK_THEME : LIGHT_THEME;
}

export function usePublicTheme() {
    const theme = ref(LIGHT_THEME);

    const isDarkTheme = computed(() => theme.value === DARK_THEME);

    function applyTheme(nextTheme) {
        theme.value = nextTheme;

        document.documentElement.dataset.theme = nextTheme;
        document.body.dataset.theme = nextTheme;

        document.documentElement.classList.toggle("dark-theme", nextTheme === DARK_THEME);
        document.body.classList.toggle("dark-theme", nextTheme === DARK_THEME);

        localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    }

    function toggleTheme() {
        applyTheme(isDarkTheme.value ? LIGHT_THEME : DARK_THEME);
    }

    onMounted(() => {
        applyTheme(getPreferredTheme());
    });

    return {
        theme,
        isDarkTheme,
        applyTheme,
        toggleTheme,
    };
}