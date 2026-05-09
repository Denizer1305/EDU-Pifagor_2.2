<script setup>
import BaseIcon from "../ui/BaseIcon.vue";

defineProps({
    title: {
        type: String,
        default: "Произошла ошибка",
    },
    message: {
        type: String,
        default: "",
    },
});
</script>

<template>
    <div
        class="feedback-message feedback-message--error"
        role="alert"
    >
        <div class="feedback-message__icon">
            <BaseIcon
                name="exclamation"
                size="22"
            />
        </div>

        <div class="feedback-message__content">
            <strong>
                {{ title }}
            </strong>

            <p v-if="message || $slots.default">
                <slot>{{ message }}</slot>
            </p>
        </div>
    </div>
</template>

<style scoped>
.feedback-message {
    display: grid;
    grid-template-columns: 46px minmax(0, 1fr);
    gap: 14px;
    padding: 16px;
    border-radius: var(--radius-20);
    line-height: 1.55;
}

.feedback-message--error {
    border: 1px solid rgba(201, 74, 74, 0.18);
    color: var(--danger, #c94a4a);
    background: rgba(201, 74, 74, 0.08);
}

.feedback-message__icon {
    display: grid;
    place-items: center;
    width: 46px;
    height: 46px;
    border-radius: var(--radius-16);
    background: rgba(201, 74, 74, 0.1);
}

.feedback-message__content {
    display: grid;
    gap: 4px;
}

.feedback-message__content strong {
    color: currentColor;
    font-size: 0.95rem;
}

.feedback-message__content p {
    margin: 0;
    color: var(--secondary);
    font-size: 0.86rem;
}
</style>
