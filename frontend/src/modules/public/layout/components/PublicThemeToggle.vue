<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

defineProps({
    buttonClass: {
        type: String,
        default: "theme-toggle",
    },
});

defineEmits({
    toggle: null,
});
</script>

<template>
    <button
        :class="buttonClass"
        type="button"
        aria-label="Переключить тему"
        @click="$emit('toggle')"
    >
        <BaseIcon
            name="sun"
            size="18"
        />

        <BaseIcon
            name="moon"
            size="18"
        />
    </button>
</template>
