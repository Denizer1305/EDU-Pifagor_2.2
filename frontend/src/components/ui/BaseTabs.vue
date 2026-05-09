<script setup>
const model = defineModel({
    type: String,
    required: true,
});

defineProps({
    tabs: {
        type: Array,
        required: true,
    },
});
</script>

<template>
    <div
        class="base-tabs"
        role="tablist"
    >
        <button
            v-for="tab in tabs"
            :key="tab.value"
            type="button"
            class="base-tabs__button"
            :class="{ 'base-tabs__button--active': model === tab.value }"
            role="tab"
            :aria-selected="model === tab.value"
            @click="model = tab.value"
        >
            {{ tab.label }}
        </button>
    </div>
</template>

<style scoped>
.base-tabs {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 6px;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-pill);
    background: var(--white-72);
}

.base-tabs__button {
    min-height: 38px;
    padding: 0 16px;
    border: 0;
    border-radius: var(--radius-pill);
    color: var(--secondary);
    background: transparent;
    font-weight: var(--font-weight-bold);
    cursor: pointer;
    transition: var(--transition-soft);
}

.base-tabs__button:hover,
.base-tabs__button--active {
    color: var(--white);
    background: var(--primary);
}
</style>
