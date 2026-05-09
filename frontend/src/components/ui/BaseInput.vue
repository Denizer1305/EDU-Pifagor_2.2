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
    type: {
        type: String,
        default: "text",
    },
    label: {
        type: String,
        default: "",
    },
    placeholder: {
        type: String,
        default: "",
    },
    error: {
        type: String,
        default: "",
    },
    hint: {
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
    autocomplete: {
        type: String,
        default: "",
    },
});

const generatedId = useId();

const inputId = computed(() => {
    return props.id || `base-input-${generatedId}`;
});
</script>

<template>
    <div class="base-input-field">
        <label
            v-if="label"
            :for="inputId"
            class="base-input-field__label"
        >
            {{ label }}
        </label>

        <input
            :id="inputId"
            v-model="model"
            :name="name"
            :type="type"
            :placeholder="placeholder"
            :disabled="disabled"
            :required="required"
            :autocomplete="autocomplete || undefined"
            class="base-input-field__control"
            :class="{ 'base-input-field__control--error': error }"
        />

        <p
            v-if="error"
            class="base-input-field__error"
        >
            {{ error }}
        </p>

        <p
            v-else-if="hint"
            class="base-input-field__hint"
        >
            {{ hint }}
        </p>
    </div>
</template>

<style scoped>
.base-input-field {
    display: grid;
    gap: 8px;
}

.base-input-field__label {
    color: var(--primary);
    font-size: 0.9rem;
    font-weight: var(--font-weight-bold);
    line-height: 1.35;
}

.base-input-field__control {
    width: 100%;
    min-height: 52px;
    padding: 0 16px;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-18);
    color: var(--primary);
    background: var(--white-82);
    box-shadow: inset 0 0 0 1px var(--white-50);
    font: inherit;
    transition: var(--transition-soft);
}

.base-input-field__control:focus {
    outline: none;
    border-color: var(--accent-24);
    background: var(--white);
    box-shadow:
        inset 0 0 0 1px var(--white-60),
        0 0 0 4px var(--accent-08);
}

.base-input-field__control:disabled {
    opacity: 0.62;
    cursor: not-allowed;
}

.base-input-field__control--error {
    border-color: var(--danger, #c94a4a);
}

.base-input-field__error,
.base-input-field__hint {
    margin: 0;
    font-size: 0.8rem;
    line-height: 1.5;
}

.base-input-field__error {
    color: var(--danger, #c94a4a);
}

.base-input-field__hint {
    color: var(--secondary);
}
</style>
