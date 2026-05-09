<script setup>
import BaseButton from "../ui/BaseButton.vue";
import SearchField from "../forms/SearchField.vue";

const search = defineModel("search", {
    type: String,
    default: "",
});

defineProps({
    title: {
        type: String,
        default: "",
    },
    description: {
        type: String,
        default: "",
    },
    searchPlaceholder: {
        type: String,
        default: "Поиск по данным",
    },
    createLabel: {
        type: String,
        default: "",
    },
    createTo: {
        type: [String, Object],
        default: null,
    },
    isLoading: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits({
    create: null,
    refresh: null,
    search: (value) => typeof value === "string",
});
</script>

<template>
    <div class="data-toolbar">
        <div class="data-toolbar__content">
            <h2 v-if="title">
                {{ title }}
            </h2>

            <p v-if="description">
                {{ description }}
            </p>
        </div>

        <div class="data-toolbar__actions">
            <SearchField
                v-model="search"
                :placeholder="searchPlaceholder"
                @search="$emit('search', $event)"
            />

            <BaseButton
                variant="secondary"
                icon="refresh"
                :loading="isLoading"
                @click="$emit('refresh')"
            >
                Обновить
            </BaseButton>

            <BaseButton
                v-if="createLabel"
                variant="primary"
                icon="plus"
                :to="createTo"
                @click="$emit('create')"
            >
                {{ createLabel }}
            </BaseButton>

            <slot name="actions" />
        </div>
    </div>
</template>

<style scoped>
.data-toolbar {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 20px;
    align-items: end;
}

.data-toolbar__content {
    display: grid;
    gap: 8px;
}

.data-toolbar__content h2 {
    margin: 0;
    color: var(--primary);
    font-size: clamp(1.8rem, 3vw, 2.8rem);
    line-height: var(--line-height-heading);
}

.data-toolbar__content p {
    max-width: 720px;
    margin: 0;
    color: var(--secondary);
    font-size: 0.92rem;
    line-height: 1.7;
}

.data-toolbar__actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 10px;
}

.data-toolbar__actions :deep(.search-field) {
    min-width: min(320px, 100%);
}

@media (max-width: 900px) {
    .data-toolbar {
        grid-template-columns: 1fr;
    }

    .data-toolbar__actions {
        justify-content: flex-start;
    }
}

@media (max-width: 560px) {
    .data-toolbar__actions {
        flex-direction: column;
    }

    .data-toolbar__actions :deep(.base-button),
    .data-toolbar__actions :deep(.search-field) {
        width: 100%;
    }
}
</style>
