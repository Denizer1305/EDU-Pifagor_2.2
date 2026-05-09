<script setup>
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
        <i class="fas fa-sun"></i>
        <i class="fas fa-moon"></i>
    </button>
</template>