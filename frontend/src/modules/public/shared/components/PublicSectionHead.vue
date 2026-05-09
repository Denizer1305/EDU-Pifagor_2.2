<script setup>
defineProps({
    label: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    description: {
        type: String,
        default: "",
    },
});
</script>

<template>
    <div class="section-head fade-in">
        <div class="section-label">
            {{ label }}
        </div>

        <h2 class="section-title">
            {{ title }}
        </h2>

        <p
            v-if="description"
            class="section-description"
        >
            {{ description }}
        </p>
    </div>
</template>
