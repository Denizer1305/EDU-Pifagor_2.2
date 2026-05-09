<script setup>
import { RouterLink, useRoute } from "vue-router";

import PublicThemeToggle from "./PublicThemeToggle.vue";

defineProps({
    navigationItems: {
        type: Array,
        required: true,
    },
    isMobileMenuOpen: {
        type: Boolean,
        default: false,
    },
});

defineEmits({
    openMenu: null,
    toggleTheme: null,
});

const route = useRoute();

function isActiveNavigationItem(item) {
    return item.match.includes(route.name);
}
</script>

<template>
    <header class="site-header">
        <div class="container">
            <div class="header-shell">
                <div class="logo-header">
                    <RouterLink
                        to="/"
                        aria-label="Главная страница | Пифагор"
                    >
                        <img
                            src="/logo/light/logo.svg"
                            alt="Пифагор"
                        />
                    </RouterLink>
                </div>

                <nav
                    class="header-nav"
                    aria-label="Основная навигация"
                >
                    <ul class="nav-links">
                        <li
                            v-for="item in navigationItems"
                            :key="item.to"
                        >
                            <RouterLink
                                :to="item.to"
                                :class="{ active: isActiveNavigationItem(item) }"
                            >
                                {{ item.label }}
                            </RouterLink>
                        </li>
                    </ul>
                </nav>

                <div class="header-actions">
                    <PublicThemeToggle @toggle="$emit('toggleTheme')" />

                    <RouterLink
                        to="/auth/login"
                        class="login-btn"
                    >
                        Вход в кабинет
                    </RouterLink>

                    <button
                        class="mobile-menu-toggle burger"
                        type="button"
                        aria-label="Открыть меню"
                        :aria-expanded="isMobileMenuOpen"
                        @click="$emit('openMenu')"
                    >
                        <span></span>
                        <span></span>
                        <span></span>
                    </button>
                </div>
            </div>
        </div>
    </header>
</template>
