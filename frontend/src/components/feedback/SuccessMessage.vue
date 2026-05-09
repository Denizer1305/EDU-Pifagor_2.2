<script setup>
import BaseIcon from "../ui/BaseIcon.vue";

defineProps({
    title: {
        type: String,
        default: "Готово",
    },
    message: {
        type: String,
        default: "",
    },
});
</script>

<template>
    <div
        class="feedback-message feedback-message--success"
        role="status"
    >
        <div class="feedback-message__icon">
            <BaseIcon
                name="check-circle"
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

.feedback-message--success {
    border: 1px solid rgba(47, 133, 90, 0.18);
    color: var(--success, #2f855a);
    background: rgba(47, 133, 90, 0.08);
}

.feedback-message__icon {
    display: grid;
    place-items: center;
    width: 46px;
    height: 46px;
    border-radius: var(--radius-16);
    background: rgba(47, 133, 90, 0.1);
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
