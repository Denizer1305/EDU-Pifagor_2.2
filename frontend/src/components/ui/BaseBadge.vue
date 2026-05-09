<script setup>
import { computed } from "vue";

import BaseIcon from "./BaseIcon.vue";

const props = defineProps({
    label: {
        type: String,
        default: "",
    },
    icon: {
        type: String,
        default: "",
    },
    variant: {
        type: String,
        default: "neutral",
        validator(value) {
            return [
                "neutral",
                "primary",
                "success",
                "warning",
                "danger",
                "accent",
            ].includes(value);
        },
    },
    size: {
        type: String,
        default: "md",
        validator(value) {
            return ["sm", "md"].includes(value);
        },
    },
});

const badgeClasses = computed(() => {
    return [
        "base-badge",
        `base-badge--${props.variant}`,
        `base-badge--${props.size}`,
    ];
});
</script>

<template>
    <span :class="badgeClasses">
        <BaseIcon
            v-if="icon"
            :name="icon"
            :size="size === 'sm' ? 13 : 15"
        />

        <span>
            <slot>{{ label }}</slot>
        </span>
    </span>
</template>

<style scoped>
.base-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    width: fit-content;
    border: 1px solid transparent;
    border-radius: var(--radius-pill);
    font-weight: var(--font-weight-bold);
    line-height: 1.2;
}

.base-badge--sm {
    min-height: 26px;
    padding: 4px 9px;
    font-size: 0.72rem;
}

.base-badge--md {
    min-height: 32px;
    padding: 6px 11px;
    font-size: 0.8rem;
}

.base-badge--neutral {
    color: var(--secondary);
    background: var(--primary-04);
    border-color: var(--primary-08);
}

.base-badge--primary {
    color: var(--primary);
    background: var(--primary-06);
    border-color: var(--primary-08);
}

.base-badge--accent {
    color: var(--accent);
    background: var(--accent-08);
    border-color: var(--accent-12);
}

.base-badge--success {
    color: var(--success, #2f855a);
    background: rgba(47, 133, 90, 0.1);
    border-color: rgba(47, 133, 90, 0.18);
}

.base-badge--warning {
    color: var(--warning, #b7791f);
    background: var(--warning-12, rgba(183, 121, 31, 0.12));
    border-color: var(--warning-20, rgba(183, 121, 31, 0.2));
}

.base-badge--danger {
    color: var(--danger, #c94a4a);
    background: rgba(201, 74, 74, 0.1);
    border-color: rgba(201, 74, 74, 0.18);
}
</style>
