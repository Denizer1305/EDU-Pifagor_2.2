<script setup>
import { reactive } from "vue";
import { RouterLink } from "vue-router";

import BaseIcon from "../../../components/ui/BaseIcon.vue";
import { usePasswordVisibility } from "../composables/usePasswordVisibility";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const form = reactive({
    role: "student",
    lastName: "",
    firstName: "",
    middleName: "",
    phone: "",
    email: "",
    password: "",
    passwordConfirm: "",
    agreeRules: false,
});

const passwordVisibility = usePasswordVisibility();
const passwordConfirmVisibility = usePasswordVisibility();

function submitRegisterForm() {
    /*
     * API регистрации подключим следующим этапом.
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
                @submit.prevent="submitRegisterForm"
            >
                <div class="form-group full">
                    <label class="form-label">
                        {{ content.fields.role.label }}
                    </label>

                    <div class="role-switcher">
                        <label
                            v-for="role in content.roles"
                            :key="role.value"
                            class="role-option"
                        >
                            <input
                                v-model="form.role"
                                type="radio"
                                name="role"
                                :value="role.value"
                            />

                            <span>
                                {{ role.label }}
                            </span>
                        </label>
                    </div>
                </div>

                <div class="form-grid">
                    <div class="form-group">
                        <label
                            class="form-label"
                            for="register-last-name"
                        >
                            {{ content.fields.lastName.label }}
                        </label>

                        <div class="input-shell">
                            <input
                                id="register-last-name"
                                v-model="form.lastName"
                                name="last_name"
                                type="text"
                                :placeholder="content.fields.lastName.placeholder"
                                autocomplete="family-name"
                                required
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label
                            class="form-label"
                            for="register-first-name"
                        >
                            {{ content.fields.firstName.label }}
                        </label>

                        <div class="input-shell">
                            <input
                                id="register-first-name"
                                v-model="form.firstName"
                                name="first_name"
                                type="text"
                                :placeholder="content.fields.firstName.placeholder"
                                autocomplete="given-name"
                                required
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label
                            class="form-label"
                            for="register-middle-name"
                        >
                            {{ content.fields.middleName.label }}
                        </label>

                        <div class="input-shell">
                            <input
                                id="register-middle-name"
                                v-model="form.middleName"
                                name="middle_name"
                                type="text"
                                :placeholder="content.fields.middleName.placeholder"
                                autocomplete="additional-name"
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label
                            class="form-label"
                            for="register-phone"
                        >
                            {{ content.fields.phone.label }}
                        </label>

                        <div class="input-shell">
                            <input
                                id="register-phone"
                                v-model="form.phone"
                                name="phone"
                                type="tel"
                                :placeholder="content.fields.phone.placeholder"
                                autocomplete="tel"
                                required
                            />
                        </div>
                    </div>

                    <div class="form-group full">
                        <label
                            class="form-label"
                            for="register-email"
                        >
                            {{ content.fields.email.label }}
                        </label>

                        <div class="input-shell">
                            <input
                                id="register-email"
                                v-model="form.email"
                                name="email"
                                type="email"
                                :placeholder="content.fields.email.placeholder"
                                autocomplete="email"
                                required
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label
                            class="form-label"
                            for="register-password"
                        >
                            {{ content.fields.password.label }}
                        </label>

                        <div class="input-shell">
                            <input
                                id="register-password"
                                v-model="form.password"
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

                    <div class="form-group">
                        <label
                            class="form-label"
                            for="register-password-confirm"
                        >
                            {{ content.fields.passwordConfirm.label }}
                        </label>

                        <div class="input-shell">
                            <input
                                id="register-password-confirm"
                                v-model="form.passwordConfirm"
                                name="password_confirm"
                                :type="passwordConfirmVisibility.passwordInputType.value"
                                :placeholder="content.fields.passwordConfirm.placeholder"
                                autocomplete="new-password"
                                required
                            />

                            <button
                                class="password-toggle"
                                type="button"
                                :aria-label="passwordConfirmVisibility.passwordToggleLabel.value"
                                @click="passwordConfirmVisibility.togglePasswordVisibility"
                            >
                                <BaseIcon
                                    :name="passwordConfirmVisibility.passwordToggleIcon.value"
                                    size="17"
                                />
                            </button>
                        </div>
                    </div>
                </div>

                <div class="form-check">
                    <input
                        id="agreeRules"
                        v-model="form.agreeRules"
                        name="agree_rules"
                        type="checkbox"
                        required
                    />

                    <label for="agreeRules">
                        {{ content.fields.agreement.textBefore }}

                        <a href="#">
                            {{ content.fields.agreement.rulesLabel }}
                        </a>

                        {{ content.fields.agreement.textMiddle }}

                        <a href="#">
                            {{ content.fields.agreement.personalDataLabel }}
                        </a>.
                    </label>
                </div>

                <div class="form-actions">
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

                    <div class="auth-login-link">
                        {{ content.login.textBefore }}

                        <RouterLink :to="content.login.to">
                            {{ content.login.label }}
                        </RouterLink>
                    </div>
                </div>

                <div class="auth-legal">
                    {{ content.legal }}
                </div>
            </form>
        </div>
    </section>
</template>
