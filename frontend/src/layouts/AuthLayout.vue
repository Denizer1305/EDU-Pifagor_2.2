<script setup>
import { RouterLink, RouterView } from "vue-router";

import BaseIcon from "../components/ui/BaseIcon.vue";
import { usePublicTheme } from "../modules/public/shared/composables/usePublicTheme";

const {
    toggleTheme,
} = usePublicTheme();
</script>

<template>
    <div class="auth-layout-page">
        <header class="auth-header">
            <div class="container">
                <div class="auth-header-shell auth-header-shell--simple">
                    <RouterLink
                        to="/"
                        class="auth-header-logo"
                        aria-label="Пифагор — на главную"
                    >
                        <img
                            src="/logo/light/logo.svg"
                            alt="Пифагор"
                        />
                    </RouterLink>

                    <button
                        class="auth-theme-toggle"
                        type="button"
                        aria-label="Переключить тему"
                        @click="toggleTheme"
                    >
                        <BaseIcon
                            name="sun"
                            size="18"
                        />

                        <BaseIcon
                            name="moon"
                            size="18"
                        />
                    </button>
                </div>
            </div>
        </header>

        <RouterView />
    </div>
</template>
