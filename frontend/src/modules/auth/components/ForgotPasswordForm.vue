<script setup>
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";

import BaseIcon from "../../../components/ui/BaseIcon.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const email = ref("");
const status = ref("idle");

const isEmailReady = computed(() => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim());
});

function submitForgotPasswordForm() {
    /*
     * API восстановления пароля подключим следующим этапом.
     *
     * Будущий endpoint:
     * POST /api/v1/auth/password/forgot/
     *
     * payload:
     * {
     *     email: email.value
     * }
     */

    if (!isEmailReady.value) {
        status.value = "invalid";
        return;
    }

    status.value = "sent";
}
</script>

<template>
    <section class="auth-form-shell fade-in">
        <div class="auth-form-inner">
            <div class="auth-form-topline">
                <BaseIcon
                    :name="content.topline.icon"
                    size="14"
                />

                <span>{{ content.topline.text }}</span>
            </div>

            <h2 class="auth-form-title">
                {{ content.title }}
            </h2>

            <p class="auth-form-description">
                {{ content.description }}
            </p>

            <form
                class="registration-form"
                novalidate
                @submit.prevent="submitForgotPasswordForm"
            >
                <div class="form-group full">
                    <label
                        class="form-label"
                        for="forgot-email"
                    >
                        {{ content.fields.email.label }}
                    </label>

                    <div class="input-shell">
                        <input
                            id="forgot-email"
                            v-model="email"
                            class="form-input"
                            type="email"
                            name="email"
                            :placeholder="content.fields.email.placeholder"
                            autocomplete="email"
                            required
                        />
                    </div>
                </div>

                <div
                    v-if="status === 'invalid'"
                    class="forgot-status forgot-status--warning"
                >
                    <BaseIcon
                        name="exclamation"
                        size="16"
                    />

                    <span>{{ content.statuses.invalid }}</span>
                </div>

                <div
                    v-if="status === 'sent'"
                    class="forgot-status forgot-status--success"
                >
                    <BaseIcon
                        name="check-circle"
                        size="16"
                    />

                    <span>{{ content.statuses.sent }}</span>
                </div>

                <div class="forgot-note">
                    <strong>{{ content.note.title }}</strong>
                    {{ content.note.text }}
                </div>

                <div class="forgot-actions">
                    <button
                        class="btn btn-primary auth-submit"
                        type="submit"
                    >
                        {{ content.submitLabel }}

                        <BaseIcon
                            name="arrow-right"
                            size="15"
                        />
                    </button>

                    <RouterLink
                        class="forgot-back-link"
                        :to="content.backLink.to"
                    >
                        {{ content.backLink.label }}
                    </RouterLink>
                </div>

                <div class="forgot-support-box">
                    {{ content.support.text }}

                    <RouterLink :to="content.support.to">
                        {{ content.support.label }}
                    </RouterLink>.
                </div>

                <div class="auth-legal">
                    {{ content.legal }}
                </div>
            </form>
        </div>
    </section>
</template>
