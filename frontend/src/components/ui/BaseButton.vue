<script setup>
import { computed } from "vue";
import { RouterLink } from "vue-router";

import BaseIcon from "./BaseIcon.vue";

const props = defineProps({
    tag: {
        type: String,
        default: "button",
    },
    to: {
        type: [String, Object],
        default: null,
    },
    href: {
        type: String,
        default: "",
    },
    type: {
        type: String,
        default: "button",
    },
    variant: {
        type: String,
        default: "primary",
        validator(value) {
            return [
                "primary",
                "secondary",
                "light",
                "ghost",
                "danger",
            ].includes(value);
        },
    },
    size: {
        type: String,
        default: "md",
        validator(value) {
            return ["sm", "md", "lg"].includes(value);
        },
    },
    icon: {
        type: String,
        default: "",
    },
    iconPosition: {
        type: String,
        default: "left",
        validator(value) {
            return ["left", "right"].includes(value);
        },
    },
    disabled: {
        type: Boolean,
        default: false,
    },
    loading: {
        type: Boolean,
        default: false,
    },
    block: {
        type: Boolean,
        default: false,
    },
});

defineEmits({
    click: null,
});

const componentTag = computed(() => {
    if (props.to) {
        return RouterLink;
    }

    if (props.href) {
        return "a";
    }

    return props.tag;
});

const buttonClasses = computed(() => {
    return [
        "base-button",
        `base-button--${props.variant}`,
        `base-button--${props.size}`,
        {
            "base-button--block": props.block,
            "base-button--loading": props.loading,
            "base-button--disabled": props.disabled,
        },
    ];
});

const iconSize = computed(() => {
    return props.size === "sm" ? 15 : 17;
});
</script>

<template>
    <component
        :is="componentTag"
        :class="buttonClasses"
        :to="to"
        :href="href || undefined"
        :type="componentTag === 'button' ? type : undefined"
        :disabled="componentTag === 'button' ? disabled || loading : undefined"
        :aria-disabled="disabled || loading"
        @click="$emit('click', $event)"
    >
        <BaseIcon
            v-if="loading"
            name="spinner"
            :size="iconSize"
            class="base-button__spinner"
        />

        <BaseIcon
            v-else-if="icon && iconPosition === 'left'"
            :name="icon"
            :size="iconSize"
        />

        <span class="base-button__content">
            <slot />
        </span>

        <BaseIcon
            v-if="!loading && icon && iconPosition === 'right'"
            :name="icon"
            :size="iconSize"
        />
    </component>
</template>

<style scoped>
.base-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    border: 1px solid transparent;
    border-radius: var(--radius-pill);
    font-family: var(--font-body);
    font-weight: var(--font-weight-bold);
    line-height: 1;
    cursor: pointer;
    transition: var(--transition-soft);
}

.base-button--sm {
    min-height: 38px;
    padding: 0 14px;
    font-size: 0.82rem;
}

.base-button--md {
    min-height: 46px;
    padding: 0 20px;
    font-size: 0.9rem;
}

.base-button--lg {
    min-height: 54px;
    padding: 0 26px;
    font-size: 0.96rem;
}

.base-button--primary {
    color: var(--white);
    background: var(--primary);
    border-color: var(--primary);
    box-shadow: var(--shadow-xs);
}

.base-button--primary:hover {
    background: var(--color-primary-900);
    transform: translateY(-2px);
}

.base-button--secondary {
    color: var(--primary);
    background: var(--white-82);
    border-color: var(--primary-08);
}

.base-button--secondary:hover {
    color: var(--accent);
    border-color: var(--accent-16);
    background: var(--white);
    transform: translateY(-2px);
}

.base-button--light {
    color: var(--accent);
    background: var(--accent-08);
    border-color: var(--accent-12);
}

.base-button--light:hover {
    color: var(--white);
    background: var(--accent);
    border-color: var(--accent);
    transform: translateY(-2px);
}

.base-button--ghost {
    color: var(--primary);
    background: transparent;
    border-color: transparent;
}

.base-button--ghost:hover {
    color: var(--accent);
    background: var(--accent-08);
}

.base-button--danger {
    color: var(--white);
    background: var(--danger, #c94a4a);
    border-color: var(--danger, #c94a4a);
}

.base-button--block {
    width: 100%;
}

.base-button--disabled,
.base-button:disabled {
    opacity: 0.55;
    cursor: not-allowed;
    transform: none;
}

.base-button__spinner {
    animation: baseButtonSpin 0.9s linear infinite;
}

@keyframes baseButtonSpin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}
</style>
