<script setup>
import { useRouter } from "vue-router";

import BaseIcon from "../../../components/ui/BaseIcon.vue";

const props = defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const router = useRouter();

function confirmLogout() {
    /*
     * Следующий этап:
     * 1. POST /api/v1/auth/logout/
     * 2. Очистка auth.store
     * 3. Очистка токенов
     * 4. router.push("/")
     */

    router.push(props.content.confirmAction.to);
}
</script>

<template>
    <section class="logout-shell fade-in">
        <div class="logout-card">
            <RouterLink
                :to="content.logo.to"
                class="logout-logo"
                :aria-label="content.logo.ariaLabel"
            >
                <img
                    :src="content.logo.src"
                    :alt="content.logo.alt"
                />
            </RouterLink>

            <h1 class="logout-title">
                {{ content.title }}
            </h1>

            <p class="logout-text">
                {{ content.text }}
            </p>

            <div class="logout-info">
                <div
                    v-for="item in content.info"
                    :key="item.title"
                    class="logout-info-item"
                >
                    <div class="logout-info-icon">
                        <BaseIcon
                            :name="item.icon"
                            size="22"
                        />
                    </div>

                    <div class="logout-info-copy">
                        <strong>{{ item.title }}</strong>
                        <span>{{ item.text }}</span>
                    </div>
                </div>
            </div>

            <div class="logout-actions">
                <RouterLink
                    :to="content.cancelAction.to"
                    class="logout-btn logout-btn--light"
                >
                    <BaseIcon
                        :name="content.cancelAction.icon"
                        size="16"
                    />

                    {{ content.cancelAction.label }}
                </RouterLink>

                <button
                    type="button"
                    class="logout-btn logout-btn--primary"
                    @click="confirmLogout"
                >
                    <BaseIcon
                        :name="content.confirmAction.icon"
                        size="16"
                    />

                    {{ content.confirmAction.label }}
                </button>
            </div>
        </div>
    </section>
</template>
