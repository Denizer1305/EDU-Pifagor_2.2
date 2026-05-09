<script setup>
import { RouterLink } from "vue-router";

defineProps({
    footer: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <footer class="site-footer">
        <div class="container">
            <div class="footer-shell">
                <div class="footer-main">
                    <div class="footer-brand">
                        <div class="footer-brand-mark">
                            <img
                                :src="footer.brand.logo.src"
                                :alt="footer.brand.logo.alt"
                            />
                        </div>

                        <div class="footer-brand-copy">
                            <h3>
                                {{ footer.brand.title }}
                            </h3>

                            <p>
                                {{ footer.brand.text }}
                            </p>
                        </div>
                    </div>

                    <div class="footer-socials">
                        <a
                            v-for="social in footer.socials"
                            :key="social.label"
                            :href="social.href"
                            class="footer-social-link"
                            :aria-label="social.ariaLabel"
                        >
                            <i
                                v-if="social.icon"
                                :class="social.icon"
                            ></i>

                            <img
                                v-if="social.image"
                                :src="social.image.src"
                                :alt="social.image.alt"
                                aria-hidden="true"
                            />

                            <span>
                                {{ social.label }}
                            </span>
                        </a>
                    </div>
                </div>

                <div class="footer-bottom">
                    <nav
                        class="footer-nav"
                        aria-label="Навигация в подвале"
                    >
                        <RouterLink
                            v-for="item in footer.navigation"
                            :key="item.to"
                            :to="item.to"
                        >
                            {{ item.label }}
                        </RouterLink>
                    </nav>

                    <div class="footer-note">
                        {{ footer.note }}
                    </div>
                </div>

                <div class="footer-legal">
                    <p>
                        {{ footer.copyright }}
                    </p>
                </div>
            </div>
        </div>
    </footer>
</template>