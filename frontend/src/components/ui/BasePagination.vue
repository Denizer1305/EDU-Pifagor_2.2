<script setup>
import { computed } from "vue";

import BaseButton from "./BaseButton.vue";

const props = defineProps({
    page: {
        type: Number,
        required: true,
    },
    totalPages: {
        type: Number,
        required: true,
    },
});

const emit = defineEmits({
    change: (page) => Number.isInteger(page),
});

const canGoPrevious = computed(() => props.page > 1);
const canGoNext = computed(() => props.page < props.totalPages);

function goToPage(page) {
    if (page < 1 || page > props.totalPages || page === props.page) {
        return;
    }

    emit("change", page);
}
</script>

<template>
    <nav
        v-if="totalPages > 1"
        class="base-pagination"
        aria-label="Пагинация"
    >
        <BaseButton
            variant="secondary"
            size="sm"
            icon="arrow-left"
            :disabled="!canGoPrevious"
            @click="goToPage(page - 1)"
        >
            Назад
        </BaseButton>

        <span class="base-pagination__info">
            Страница {{ page }} из {{ totalPages }}
        </span>

        <BaseButton
            variant="secondary"
            size="sm"
            icon="arrow-right"
            icon-position="right"
            :disabled="!canGoNext"
            @click="goToPage(page + 1)"
        >
            Вперёд
        </BaseButton>
    </nav>
</template>

<style scoped>
.base-pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 12px;
}

.base-pagination__info {
    color: var(--secondary);
    font-size: 0.88rem;
    font-weight: var(--font-weight-bold);
}
</style>
