<script setup>
import { computed } from "vue";

const props = defineProps({
    as: {
        type: String,
        default: "div",
    },
    variant: {
        type: String,
        default: "default",
        validator(value) {
            return ["default", "glass", "flat", "outlined"].includes(value);
        },
    },
    padded: {
        type: Boolean,
        default: true,
    },
    hoverable: {
        type: Boolean,
        default: false,
    },
});

const cardClasses = computed(() => {
    return [
        "base-card",
        `base-card--${props.variant}`,
        {
            "base-card--padded": props.padded,
            "base-card--hoverable": props.hoverable,
        },
    ];
});
</script>

<template>
    <component
        :is="as"
        :class="cardClasses"
    >
        <slot />
    </component>
</template>

<style scoped>
.base-card {
    position: relative;
    overflow: hidden;
    border-radius: var(--radius-28);
    transition: var(--transition-soft);
}

.base-card--padded {
    padding: 24px;
}

.base-card--default {
    border: 1px solid var(--primary-08);
    background: var(--surface-card);
    box-shadow: var(--shadow-sm);
}

.base-card--glass {
    border: 1px solid var(--white-12);
    background: var(--surface-glass-max);
    box-shadow: var(--shadow-sm);
    backdrop-filter: var(--backdrop-glass);
}

.base-card--flat {
    background: var(--white);
}

.base-card--outlined {
    border: 1px solid var(--primary-08);
    background: transparent;
}

.base-card--hoverable:hover {
    transform: translateY(-5px);
    border-color: var(--accent-16);
    box-shadow: var(--shadow-md);
}
</style>
