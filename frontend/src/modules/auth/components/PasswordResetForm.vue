<script setup>
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";

import BaseIcon from "../../../components/ui/BaseIcon.vue";
import { usePasswordStrength } from "../composables/usePasswordStrength";
import { usePasswordVisibility } from "../composables/usePasswordVisibility";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const password = ref("");
const passwordConfirm = ref("");

const passwordVisibility = usePasswordVisibility();
const confirmPasswordVisibility = usePasswordVisibility();

const {
    rules,
    strength,
    isPasswordStrong,
} = usePasswordStrength(password);

const isPasswordMatched = computed(() => {
    return password.value && password.value === passwordConfirm.value;
});

const canSubmit = computed(() => {
    return isPasswordStrong.value && isPasswordMatched.value;
});

function submitResetPasswordForm() {
    /*
     * API сброса пароля подключим следующим этапом.
     *
     * Будущий payload:
     * {
     *     uid: route.query.uid или route.params.uid,
     *     token: route.query.token или route.params.token,
     *     password: password.value,
     *     password_confirm: passwordConfirm.value
     * }
     */
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
                @submit.prevent="submitResetPasswordForm"
            >
                <input
                    type="hidden"
                    name="uid"
                    value=""
                />

                <input
                    type="hidden"
                    name="token"
                    value=""
                />

                <div class="form-group full">
                    <label
                        class="form-label"
                        for="reset-password"
                    >
                        {{ content.fields.password.label }}
                    </label>

                    <div class="input-shell">
                        <input
                            id="reset-password"
                            v-model="password"
                            name="password"
                            :type="passwordVisibility.passwordInputType.value"
                            :placeholder="content.fields.password.placeholder"
                            autocomplete="new-password"
                            required
                        />

                        <button
                            class="password-toggle"
                            type="button"
                            :aria-label="passwordVisibility.passwordToggleLabel.value"
                            @click="passwordVisibility.togglePasswordVisibility"
                        >
                            <BaseIcon
                                :name="passwordVisibility.passwordToggleIcon.value"
                                size="17"
                            />
                        </button>
                    </div>
                </div>

                <div
                    class="password-strength"
                    :class="`password-strength--${strength.variant}`"
                >
                    <div class="password-strength-top">
                        <span class="password-strength-label">
                            {{ content.strength.label }}
                        </span>

                        <span class="password-strength-value">
                            {{ strength.label }}
                        </span>
                    </div>

                    <div class="password-strength-bar">
                        <div
                            class="password-strength-fill"
                            :style="{ width: `${strength.percent}%` }"
                        ></div>
                    </div>
                </div>

                <div class="password-rules">
                    <div
                        v-for="rule in rules"
                        :key="rule.key"
                        class="password-rule"
                        :class="{ 'password-rule--passed': rule.passed }"
                    >
                        <span class="password-rule-dot"></span>

                        <span>{{ rule.label }}</span>
                    </div>
                </div>

                <div class="form-group full">
                    <label
                        class="form-label"
                        for="reset-password-confirm"
                    >
                        {{ content.fields.passwordConfirm.label }}
                    </label>

                    <div class="input-shell">
                        <input
                            id="reset-password-confirm"
                            v-model="passwordConfirm"
                            name="password_confirm"
                            :type="confirmPasswordVisibility.passwordInputType.value"
                            :placeholder="content.fields.passwordConfirm.placeholder"
                            autocomplete="new-password"
                            required
                        />

                        <button
                            class="password-toggle"
                            type="button"
                            :aria-label="confirmPasswordVisibility.passwordToggleLabel.value"
                            @click="confirmPasswordVisibility.togglePasswordVisibility"
                        >
                            <BaseIcon
                                :name="confirmPasswordVisibility.passwordToggleIcon.value"
                                size="17"
                            />
                        </button>
                    </div>
                </div>

                <div
                    v-if="passwordConfirm"
                    class="reset-match-note"
                    :class="{ 'reset-match-note--success': isPasswordMatched }"
                >
                    <BaseIcon
                        :name="isPasswordMatched ? 'check-circle' : 'exclamation'"
                        size="15"
                    />

                    <span>
                        {{ isPasswordMatched ? content.match.success : content.match.error }}
                    </span>
                </div>

                <div class="reset-note">
                    <strong>{{ content.note.title }}</strong>
                    {{ content.note.text }}
                </div>

                <div class="reset-actions">
                    <button
                        class="btn btn-primary auth-submit"
                        type="submit"
                        :disabled="!canSubmit"
                    >
                        {{ content.submitLabel }}

                        <BaseIcon
                            name="arrow-right"
                            size="15"
                        />
                    </button>

                    <RouterLink
                        class="reset-back-link"
                        :to="content.backLink.to"
                    >
                        {{ content.backLink.label }}
                    </RouterLink>
                </div>

                <div class="auth-legal">
                    {{ content.legal }}
                </div>
            </form>
        </div>
    </section>
</template>
