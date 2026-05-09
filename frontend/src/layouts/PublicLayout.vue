<script setup>
import { watch } from "vue";
import { RouterView, useRoute } from "vue-router";

import PublicFooter from "../modules/public/layout/components/PublicFooter.vue";
import PublicHeader from "../modules/public/layout/components/PublicHeader.vue";
import PublicMobileMenu from "../modules/public/layout/components/PublicMobileMenu.vue";

import { useMobileMenu } from "../modules/public/home/composables/useMobileMenu";
import { usePublicTheme } from "../modules/public/home/composables/usePublicTheme";

import {
    publicNavigationItems,
} from "../modules/public/layout/data/publicNavigation.data";

import { publicFooter } from "../modules/public/layout/data/publicFooter.data";

const route = useRoute();

const {
    isMobileMenuOpen,
    openMobileMenu,
    closeMobileMenu,
} = useMobileMenu();

const {
    toggleTheme,
} = usePublicTheme();

watch(
    () => route.fullPath,
    () => {
        closeMobileMenu();
    },
);
</script>

<template>
    <div class="public-layout">
        <PublicHeader
            :navigation-items="publicNavigationItems"
            :is-mobile-menu-open="isMobileMenuOpen"
            @open-menu="openMobileMenu"
            @toggle-theme="toggleTheme"
        />

        <PublicMobileMenu
            :navigation-items="publicNavigationItems"
            :is-open="isMobileMenuOpen"
            @close="closeMobileMenu"
            @toggle-theme="toggleTheme"
        />

        <RouterView />

        <PublicFooter :footer="publicFooter" />
    </div>
</template>