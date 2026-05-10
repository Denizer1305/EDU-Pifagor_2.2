<script setup>
import { RouterLink } from "vue-router";

import BaseIcon from "../../../components/ui/BaseIcon.vue";
import { useVerificationCode } from "../composables/useVerificationCode";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const {
    codeDigits,
    verificationCode,
    isCodeComplete,
    setInputRef,
    handleInput,
    handleKeydown,
    handlePaste,
    resetCode,
} = useVerificationCode();

function submitVerifyEmailForm() {
    /*
     * API подтверждения почты подключим следующим этапом.
     * Сейчас страница переносится на Vue визуально.
     */
}

function resendCode() {
    /*
     * Повторную отправку кода подключим вместе с auth API.
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

            <div class="verify-form-meta">
                <div
                    v-for="item in content.meta"
                    :key="item.text"
                    class="verify-form-meta-item"
                >
                    <BaseIcon
                        :name="item.icon"
                        size="15"
                    />

                    <span>{{ item.text }}</span>
                </div>
            </div>

            <form
                class="registration-form"
                novalidate
                @submit.prevent="submitVerifyEmailForm"
            >
                <input
                    type="hidden"
                    name="verification_code"
                    :value="verificationCode"
                    class="verify-hidden-code"
                />

                <div class="form-group full">
                    <label class="form-label">
                        {{ content.fields.code.label }}
                    </label>

                    <div
                        class="verify-code-grid"
                        @paste="handlePaste"
                    >
                        <input
                            v-for="(_, index) in codeDigits"
                            :key="index"
                            :ref="(element) => setInputRef(element, index)"
                            :value="codeDigits[index]"
                            class="verify-code-input"
                            type="text"
                            inputmode="numeric"
                            maxlength="1"
                            :autocomplete="index === 0 ? 'one-time-code' : 'off'"
                            :aria-label="`Цифра ${index + 1} кода подтверждения`"
                            @input="handleInput($event, index)"
                            @keydown="handleKeydown($event, index)"
                        />
                    </div>

                    <div class="verify-note">
                        <strong>{{ content.fields.code.noteTitle }}</strong>
                        {{ content.fields.code.noteText }}
                        <strong>{{ content.fields.code.example }}</strong>
                        {{ content.fields.code.noteEnd }}
                    </div>
                </div>

                <div class="verify-links-row">
                    <button
                        class="btn btn-primary auth-submit"
                        type="submit"
                        :disabled="!isCodeComplete"
                    >
                        {{ content.submitLabel }}

                        <BaseIcon
                            name="arrow-right"
                            size="15"
                        />
                    </button>

                    <RouterLink
                        class="verify-secondary-link"
                        :to="content.backLink.to"
                    >
                        {{ content.backLink.label }}
                    </RouterLink>
                </div>

                <div class="verify-resend-box">
                    {{ content.resend.text }}

                    <button
                        type="button"
                        class="verify-resend-link"
                        @click="resendCode"
                    >
                        {{ content.resend.label }}
                    </button>

                    <button
                        type="button"
                        class="verify-reset-link"
                        @click="resetCode"
                    >
                        Очистить код
                    </button>
                </div>

                <div class="auth-legal">
                    {{ content.legal }}
                </div>
            </form>
        </div>
    </section>
</template>
