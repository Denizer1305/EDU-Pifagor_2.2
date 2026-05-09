<script setup>
import BaseIcon from "./BaseIcon.vue";
import BaseButton from "./BaseButton.vue";

defineProps({
    icon: {
        type: String,
        default: "info",
    },
    title: {
        type: String,
        default: "Данных пока нет",
    },
    text: {
        type: String,
        default: "Когда данные появятся в системе, они будут отображены здесь.",
    },
    actionLabel: {
        type: String,
        default: "",
    },
    actionTo: {
        type: [String, Object],
        default: null,
    },
});

defineEmits({
    action: null,
});
</script>

<template>
    <div class="base-empty-state">
        <div class="base-empty-state__icon">
            <BaseIcon
                :name="icon"
                size="34"
            />
        </div>

        <h3 class="base-empty-state__title">
            {{ title }}
        </h3>

        <p class="base-empty-state__text">
            {{ text }}
        </p>

        <BaseButton
            v-if="actionLabel"
            variant="primary"
            :to="actionTo"
            @click="$emit('action')"
        >
            {{ actionLabel }}
        </BaseButton>
    </div>
</template>

<style scoped>
.base-empty-state {
    display: grid;
    justify-items: center;
    gap: 14px;
    min-height: 280px;
    padding: 38px 24px;
    border: 1px dashed var(--accent-20);
    border-radius: var(--radius-30);
    background:
        radial-gradient(circle at top right, var(--accent-06) 0%, transparent 34%),
        var(--white-72);
    text-align: center;
}

.base-empty-state__icon {
    display: grid;
    place-items: center;
    width: 74px;
    height: 74px;
    border-radius: var(--radius-24);
    color: var(--accent);
    background: var(--accent-10);
}

.base-empty-state__title {
    margin: 0;
    color: var(--primary);
    font-size: clamp(1.35rem, 2.4vw, 2.1rem);
    line-height: var(--line-height-title);
}

.base-empty-state__text {
    max-width: 560px;
    margin: 0;
    color: var(--secondary);
    font-size: 0.92rem;
    line-height: 1.7;
}
</style>
