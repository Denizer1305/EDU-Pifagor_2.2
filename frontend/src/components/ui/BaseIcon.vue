<script setup>
import { computed } from "vue";

import { getIconSvg } from "../../assets/brand/icons/rounded/icons.registry";

const props = defineProps({
    name: {
        type: String,
        required: true,
    },
    size: {
        type: [String, Number],
        default: 24,
    },
    title: {
        type: String,
        default: "",
    },
    decorative: {
        type: Boolean,
        default: true,
    },
    monochrome: {
        type: Boolean,
        default: true,
    },
});

const iconSvg = computed(() => {
    return getIconSvg(props.name);
});

const iconSize = computed(() => {
    if (typeof props.size === "number") {
        return `${props.size}px`;
    }

    const preparedSize = String(props.size).trim();

    if (/^\d+$/.test(preparedSize)) {
        return `${preparedSize}px`;
    }

    return preparedSize;
});

const iconClasses = computed(() => {
    return [
        "base-icon",
        {
            "base-icon--missing": !iconSvg.value,
            "base-icon--monochrome": props.monochrome,
        },
    ];
});

const iconStyle = computed(() => {
    return {
        "--base-icon-size": iconSize.value,
    };
});

const accessibilityAttributes = computed(() => {
    if (props.decorative && !props.title) {
        return {
            "aria-hidden": "true",
        };
    }

    return {
        role: "img",
        "aria-label": props.title || props.name,
    };
});
</script>

<template>
    <span
        :class="iconClasses"
        :style="iconStyle"
        v-bind="accessibilityAttributes"
    >
        <span
            v-if="iconSvg"
            class="base-icon__svg"
            v-html="iconSvg"
        ></span>

        <span
            v-else
            class="base-icon__fallback"
            aria-hidden="true"
        ></span>
    </span>
</template>
