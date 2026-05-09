<script setup>
import BaseButton from "../ui/BaseButton.vue";
import BaseInput from "../ui/BaseInput.vue";
import BaseSelect from "../ui/BaseSelect.vue";

const model = defineModel({
    type: Object,
    default() {
        return {};
    },
});

defineProps({
    filters: {
        type: Array,
        default() {
            return [];
        },
    },
    applyLabel: {
        type: String,
        default: "Применить",
    },
    resetLabel: {
        type: String,
        default: "Сбросить",
    },
});

const emit = defineEmits({
    apply: (filters) => typeof filters === "object",
    reset: null,
});

function resetFilters() {
    Object.keys(model.value).forEach((key) => {
        model.value[key] = "";
    });

    emit("reset");
}

function applyFilters() {
    emit("apply", model.value);
}
</script>

<template>
    <section
        v-if="filters.length"
        class="data-filters"
    >
        <div class="data-filters__grid">
            <template
                v-for="filter in filters"
                :key="filter.key"
            >
                <BaseSelect
                    v-if="filter.type === 'select'"
                    v-model="model[filter.key]"
                    :label="filter.label"
                    :placeholder="filter.placeholder || 'Выберите значение'"
                    :options="filter.options || []"
                    :option-label="filter.optionLabel || 'label'"
                    :option-value="filter.optionValue || 'value'"
                />

                <BaseInput
                    v-else
                    v-model="model[filter.key]"
                    :type="filter.type || 'text'"
                    :label="filter.label"
                    :placeholder="filter.placeholder || ''"
                />
            </template>
        </div>

        <div class="data-filters__actions">
            <BaseButton
                variant="primary"
                icon="filter"
                @click="applyFilters"
            >
                {{ applyLabel }}
            </BaseButton>

            <BaseButton
                variant="secondary"
                icon="close"
                @click="resetFilters"
            >
                {{ resetLabel }}
            </BaseButton>
        </div>
    </section>
</template>

<style scoped>
.data-filters {
    display: grid;
    gap: 18px;
    padding: 20px;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-24);
    background: var(--white-76);
    box-shadow: var(--shadow-xs);
}

.data-filters__grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(180px, 1fr));
    gap: 14px;
}

.data-filters__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

@media (max-width: 1180px) {
    .data-filters__grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    .data-filters__grid {
        grid-template-columns: 1fr;
    }

    .data-filters__actions {
        flex-direction: column;
    }

    .data-filters__actions :deep(.base-button) {
        width: 100%;
    }
}
</style>
