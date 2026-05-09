<script setup>
import { computed, ref, watch } from "vue";

import { loadIconSvg } from "../../assets/brand/icons/rounded/icons.registry";

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

const iconSvg = ref("");
const isLoading = ref(false);

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
            "base-icon--missing": !iconSvg.value && !isLoading.value,
            "base-icon--loading": isLoading.value,
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

watch(
    () => props.name,
    async (iconName) => {
        const currentName = iconName;

        iconSvg.value = "";
        isLoading.value = true;

        const svg = await loadIconSvg(currentName);

        if (props.name === currentName) {
            iconSvg.value = svg;
            isLoading.value = false;
        }
    },
    {
        immediate: true,
    },
);
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
