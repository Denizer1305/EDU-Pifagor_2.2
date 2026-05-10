<script setup>
import { reactive } from "vue";
import { RouterLink } from "vue-router";

import { BaseIcon } from "../../../components";
import { usePasswordVisibility } from "../composables/usePasswordVisibility";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const form = reactive({
    email: "",
    password: "",
    rememberMe: false,
});

const {
    passwordInputType,
    passwordToggleLabel,
    passwordToggleIcon,
    togglePasswordVisibility,
} = usePasswordVisibility();

function submitLoginForm() {
    /*
     * API авторизации подключим следующим этапом.
     * Сейчас страница переносится на Vue только визуально.
     */
}
</script>

<template>
    <section class="auth-form-shell fade-in">
        <div class="auth-form-inner">
            <div class="auth-form-topline">
                <BaseIcon
                    :name="content.topline.icon"
                    size="13"
                />
                {{ content.topline.text }}
            </div>

            <h2 class="auth-form-title">
                {{ content.title }}
            </h2>

            <p class="auth-form-description">
                {{ content.description }}
            </p>

            <div class="login-form-meta">
                <div
                    v-for="role in content.roles"
                    :key="role.text"
                    class="login-form-meta-item"
                >
                    <BaseIcon
                        :name="role.icon"
                        size="13"
                    />
                    {{ role.text }}
                </div>
            </div>

            <form
                class="registration-form"
                @submit.prevent="submitLoginForm"
            >
                <div class="form-group full">
                    <label
                        class="form-label"
                        for="login-email"
                    >
                        {{ content.fields.email.label }}
                    </label>

                    <div class="input-shell">
                        <input
                            id="login-email"
                            v-model="form.email"
                            name="email"
                            type="email"
                            :placeholder="content.fields.email.placeholder"
                            autocomplete="email"
                            required
                        />
                    </div>
                </div>

                <div class="form-group full">
                    <label
                        class="form-label"
                        for="login-password"
                    >
                        {{ content.fields.password.label }}
                    </label>

                    <div class="input-shell">
                        <input
                            id="login-password"
                            v-model="form.password"
                            name="password"
                            :type="passwordInputType"
                            :placeholder="content.fields.password.placeholder"
                            autocomplete="current-password"
                            required
                        />

                        <button
                            class="password-toggle"
                            type="button"
                            :aria-label="passwordToggleLabel"
                            @click="togglePasswordVisibility"
                        >
                            <BaseIcon
                                :name="passwordToggleIcon"
                                size="13"
                            />
                        </button>
                    </div>
                </div>

                <div class="form-check">
                    <input
                        id="rememberMe"
                        v-model="form.rememberMe"
                        name="remember_me"
                        type="checkbox"
                    />

                    <label for="rememberMe">
                        {{ content.fields.remember.label }}
                    </label>
                </div>

                <div class="login-links-row">
                    <button
                        class="btn btn-primary auth-submit"
                        type="submit"
                    >
                        {{ content.submitLabel }}

                        <BaseIcon
                            name="arrow-right"
                            size="13"
                        />
                    </button>

                    <RouterLink
                        class="login-forgot-link"
                        :to="content.forgotPassword.to"
                    >
                        {{ content.forgotPassword.label }}
                    </RouterLink>
                </div>

                <div class="login-register-box">
                    {{ content.register.textBefore }}

                    <RouterLink :to="content.register.to">
                        {{ content.register.label }}
                    </RouterLink>

                    {{ content.register.textAfter }}
                </div>

                <div class="auth-legal">
                    {{ content.legal }}
                </div>
            </form>
        </div>
    </section>
</template>
