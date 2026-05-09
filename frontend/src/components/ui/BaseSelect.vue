<script setup>
import { computed, useId } from "vue";

const model = defineModel({
    type: [String, Number],
    default: "",
});

const props = defineProps({
    id: {
        type: String,
        default: "",
    },
    name: {
        type: String,
        default: "",
    },
    label: {
        type: String,
        default: "",
    },
    placeholder: {
        type: String,
        default: "Выберите значение",
    },
    options: {
        type: Array,
        default() {
            return [];
        },
    },
    optionLabel: {
        type: String,
        default: "label",
    },
    optionValue: {
        type: String,
        default: "value",
    },
    error: {
        type: String,
        default: "",
    },
    disabled: {
        type: Boolean,
        default: false,
    },
    required: {
        type: Boolean,
        default: false,
    },
});

const generatedId = useId();

const selectId = computed(() => {
    return props.id || `base-select-${generatedId}`;
});

function getOptionLabel(option) {
    if (typeof option === "string" || typeof option === "number") {
        return option;
    }

    return option[props.optionLabel];
}

function getOptionValue(option) {
    if (typeof option === "string" || typeof option === "number") {
        return option;
    }

    return option[props.optionValue];
}
</script>

<template>
    <div class="base-select-field">
        <label
            v-if="label"
            :for="selectId"
            class="base-select-field__label"
        >
            {{ label }}
        </label>

        <select
            :id="selectId"
            v-model="model"
            :name="name"
            :disabled="disabled"
            :required="required"
            class="base-select-field__control"
            :class="{ 'base-select-field__control--error': error }"
        >
            <option
                value=""
                disabled
            >
                {{ placeholder }}
            </option>

            <option
                v-for="option in options"
                :key="getOptionValue(option)"
                :value="getOptionValue(option)"
            >
                {{ getOptionLabel(option) }}
            </option>
        </select>

        <p
            v-if="error"
            class="base-select-field__error"
        >
            {{ error }}
        </p>
    </div>
</template>

<style scoped>
.base-select-field {
    display: grid;
    gap: 8px;
}

.base-select-field__label {
    color: var(--primary);
    font-size: 0.9rem;
    font-weight: var(--font-weight-bold);
}

.base-select-field__control {
    width: 100%;
    min-height: 52px;
    padding: 0 16px;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-18);
    color: var(--primary);
    background: var(--white-82);
    font: inherit;
    transition: var(--transition-soft);
}

.base-select-field__control:focus {
    outline: none;
    border-color: var(--accent-24);
    box-shadow: 0 0 0 4px var(--accent-08);
}

.base-select-field__control--error {
    border-color: var(--danger, #c94a4a);
}

.base-select-field__error {
    margin: 0;
    color: var(--danger, #c94a4a);
    font-size: 0.8rem;
    line-height: 1.5;
}
</style>
