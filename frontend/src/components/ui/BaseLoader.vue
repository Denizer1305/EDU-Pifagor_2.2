<script setup>
import BaseIcon from "./BaseIcon.vue";

defineProps({
    text: {
        type: String,
        default: "Загрузка данных",
    },
    size: {
        type: [String, Number],
        default: 34,
    },
});
</script>

<template>
    <div class="base-loader">
        <BaseIcon
            name="spinner"
            :size="size"
            class="base-loader__icon"
        />

        <span
            v-if="text"
            class="base-loader__text"
        >
            {{ text }}
        </span>
    </div>
</template>

<style scoped>
.base-loader {
    display: grid;
    justify-items: center;
    gap: 12px;
    padding: 28px;
    color: var(--accent);
    text-align: center;
}

.base-loader__icon {
    animation: baseLoaderSpin 0.9s linear infinite;
}

.base-loader__text {
    color: var(--secondary);
    font-size: 0.9rem;
    font-weight: var(--font-weight-bold);
}

@keyframes baseLoaderSpin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}
</style>
