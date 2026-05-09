<script setup>
import { RouterLink, useRoute } from "vue-router";

import PublicThemeToggle from "./PublicThemeToggle.vue";

defineProps({
    navigationItems: {
        type: Array,
        required: true,
    },
    isOpen: {
        type: Boolean,
        default: false,
    },
});

defineEmits({
    close: null,
    toggleTheme: null,
});

const route = useRoute();

function isActiveNavigationItem(item) {
    return item.match.includes(route.name);
}
</script>

<template>
    <button
        class="mobile-overlay"
        type="button"
        aria-label="Закрыть мобильное меню"
        :class="{ active: isOpen }"
        @click="$emit('close')"
    ></button>

    <div
        class="mobile-menu"
        :class="{ active: isOpen }"
        aria-label="Мобильное меню"
    >
        <div
            class="mobile-menu-bg"
            aria-hidden="true"
        >
            <div class="mobile-menu-circle one"></div>
            <div class="mobile-menu-circle two"></div>
            <div class="mobile-menu-circle three"></div>
            <div class="mobile-menu-line one"></div>
            <div class="mobile-menu-line two"></div>
            <div class="mobile-menu-glow"></div>
        </div>

        <div class="mobile-menu-header">
            <RouterLink
                to="/"
                class="mobile-logo"
                @click="$emit('close')"
            >
                <img
                    src="/logo/light/logo.svg"
                    alt="Пифагор"
                />
                <span class="mobile-logo-text">ПИФАГОР</span>
            </RouterLink>

            <div class="mobile-header-actions">
                <PublicThemeToggle
                    button-class="mobile-theme-toggle"
                    @toggle="$emit('toggleTheme')"
                />

                <button
                    class="mobile-close-btn"
                    type="button"
                    aria-label="Закрыть меню"
                    @click="$emit('close')"
                >
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>

        <div class="mobile-menu-body">
            <nav
                class="mobile-nav"
                aria-label="Мобильная навигация"
            >
                <ul class="mobile-nav-list">
                    <li
                        v-for="item in navigationItems"
                        :key="item.to"
                    >
                        <RouterLink
                            :to="item.to"
                            class="mobile-nav-link"
                            :class="{ active: isActiveNavigationItem(item) }"
                            @click="$emit('close')"
                        >
                            <span class="mobile-nav-icon">
                                <i :class="item.icon"></i>
                            </span>

                            <span class="mobile-nav-content">
                                <span class="mobile-nav-title">
                                    {{ item.label }}
                                </span>

                                <span class="mobile-nav-desc">
                                    {{ item.description }}
                                </span>
                            </span>

                            <i class="fas fa-arrow-right mobile-nav-arrow"></i>
                        </RouterLink>
                    </li>
                </ul>
            </nav>

            <div class="mobile-auth">
                <RouterLink
                    to="/auth/login"
                    class="mobile-login-btn"
                    @click="$emit('close')"
                >
                    <i class="fas fa-sign-in-alt"></i>
                    Вход в кабинет
                </RouterLink>
            </div>
        </div>
    </div>
</template>