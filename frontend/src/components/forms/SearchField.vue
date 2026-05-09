<script setup>
import BaseIcon from "../ui/BaseIcon.vue";

const model = defineModel({
    type: String,
    default: "",
});

defineProps({
    placeholder: {
        type: String,
        default: "Поиск",
    },
    disabled: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits({
    search: (value) => typeof value === "string",
    clear: null,
});

function submitSearch() {
    emit("search", model.value);
}

function clearSearch() {
    model.value = "";
    emit("clear");
}
</script>

<template>
    <form
        class="search-field"
        role="search"
        @submit.prevent="submitSearch"
    >
        <BaseIcon
            name="search"
            size="17"
            class="search-field__icon"
        />

        <input
            v-model="model"
            type="search"
            class="search-field__input"
            :placeholder="placeholder"
            :disabled="disabled"
        />

        <button
            v-if="model"
            type="button"
            class="search-field__clear"
            aria-label="Очистить поиск"
            @click="clearSearch"
        >
            <BaseIcon
                name="close"
                size="14"
            />
        </button>
    </form>
</template>

<style scoped>
.search-field {
    position: relative;
    display: flex;
    align-items: center;
    min-height: 46px;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-pill);
    background: var(--white-82);
    box-shadow: inset 0 0 0 1px var(--white-50);
    transition: var(--transition-soft);
}

.search-field:focus-within {
    border-color: var(--accent-24);
    background: var(--white);
    box-shadow:
        inset 0 0 0 1px var(--white-60),
        0 0 0 4px var(--accent-08);
}

.search-field__icon {
    margin-left: 16px;
    color: var(--secondary);
}

.search-field__input {
    width: 100%;
    min-width: 0;
    height: 44px;
    padding: 0 14px;
    border: 0;
    color: var(--primary);
    background: transparent;
    font: inherit;
    outline: none;
}

.search-field__input::placeholder {
    color: var(--secondary);
    opacity: 0.72;
}

.search-field__clear {
    display: grid;
    place-items: center;
    width: 34px;
    height: 34px;
    margin-right: 6px;
    border: 0;
    border-radius: var(--radius-round);
    color: var(--secondary);
    background: transparent;
    cursor: pointer;
    transition: var(--transition-soft);
}

.search-field__clear:hover {
    color: var(--accent);
    background: var(--accent-08);
}
</style>
