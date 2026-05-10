<script setup>
import { RouterLink } from "vue-router";

import BaseIcon from "../../../components/ui/BaseIcon.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section class="auth-status-shell fade-in">
        <article class="auth-status-card">
            <div class="auth-status-icon">
                <BaseIcon
                    :name="content.icon"
                    size="34"
                />
            </div>

            <div class="auth-status-badge">
                <BaseIcon
                    :name="content.badge.icon"
                    size="14"
                />

                <span>{{ content.badge.text }}</span>
            </div>

            <h1 class="auth-status-title">
                {{ content.title }}
            </h1>

            <p class="auth-status-text">
                {{ content.text }}
            </p>

            <div
                v-if="content.items?.length"
                class="auth-status-list"
            >
                <div
                    v-for="item in content.items"
                    :key="item.title"
                    class="auth-status-list-item"
                >
                    <div class="auth-status-list-icon">
                        <BaseIcon
                            :name="item.icon"
                            size="18"
                        />
                    </div>

                    <div>
                        <strong>{{ item.title }}</strong>
                        <span>{{ item.text }}</span>
                    </div>
                </div>
            </div>

            <div
                v-if="content.actions?.length"
                class="auth-status-actions"
            >
                <RouterLink
                    v-for="action in content.actions"
                    :key="action.label"
                    :to="action.to"
                    class="auth-status-btn"
                    :class="`auth-status-btn--${action.variant}`"
                >
                    <BaseIcon
                        v-if="action.icon"
                        :name="action.icon"
                        size="16"
                    />

                    {{ action.label }}
                </RouterLink>
            </div>

            <div
                v-if="content.note"
                class="auth-status-note"
            >
                {{ content.note }}
            </div>
        </article>
    </section>
</template>
