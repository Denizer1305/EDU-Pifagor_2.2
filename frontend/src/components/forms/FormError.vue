<script setup>
import BaseIcon from "../ui/BaseIcon.vue";

defineProps({
    message: {
        type: String,
        default: "",
    },
});
</script>

<template>
    <p
        v-if="message || $slots.default"
        class="form-error"
    >
        <BaseIcon
            name="exclamation"
            size="14"
        />

        <span>
            <slot>{{ message }}</slot>
        </span>
    </p>
</template>

<style scoped>
.form-error {
    display: inline-flex;
    align-items: flex-start;
    gap: 7px;
    margin: 0;
    color: var(--danger, #c94a4a);
    font-size: 0.8rem;
    font-weight: var(--font-weight-bold);
    line-height: 1.45;
}

.form-error .base-icon {
    margin-top: 2px;
    flex-shrink: 0;
}
</style>
