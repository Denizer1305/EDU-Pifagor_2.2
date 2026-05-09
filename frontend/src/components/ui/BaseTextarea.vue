<script setup>
import { computed, useId } from "vue";

const model = defineModel({
    type: String,
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
        default: "",
    },
    rows: {
        type: Number,
        default: 5,
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
});

const generatedId = useId();

const textareaId = computed(() => {
    return props.id || `base-textarea-${generatedId}`;
});
</script>

<template>
    <div class="base-textarea-field">
        <label
            v-if="label"
            :for="textareaId"
            class="base-textarea-field__label"
        >
            {{ label }}
        </label>

        <textarea
            :id="textareaId"
            v-model="model"
            :name="name"
            :rows="rows"
            :placeholder="placeholder"
            :disabled="disabled"
            :required="required"
            class="base-textarea-field__control"
            :class="{ 'base-textarea-field__control--error': error }"
        ></textarea>

        <p
            v-if="error"
            class="base-textarea-field__error"
        >
            {{ error }}
        </p>

        <p
            v-else-if="hint"
            class="base-textarea-field__hint"
        >
            {{ hint }}
        </p>
    </div>
</template>

<style scoped>
.base-textarea-field {
    display: grid;
    gap: 8px;
}

.base-textarea-field__label {
    color: var(--primary);
    font-size: 0.9rem;
    font-weight: var(--font-weight-bold);
    line-height: 1.35;
}

.base-textarea-field__control {
    width: 100%;
    min-height: 140px;
    resize: vertical;
    padding: 14px 16px;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-18);
    color: var(--primary);
    background: var(--white-82);
    box-shadow: inset 0 0 0 1px var(--white-50);
    font: inherit;
    line-height: 1.65;
    transition: var(--transition-soft);
}

.base-textarea-field__control:focus {
    outline: none;
    border-color: var(--accent-24);
    background: var(--white);
    box-shadow:
        inset 0 0 0 1px var(--white-60),
        0 0 0 4px var(--accent-08);
}

.base-textarea-field__control--error {
    border-color: var(--danger, #c94a4a);
}

.base-textarea-field__error,
.base-textarea-field__hint {
    margin: 0;
    font-size: 0.8rem;
    line-height: 1.5;
}

.base-textarea-field__error {
    color: var(--danger, #c94a4a);
}

.base-textarea-field__hint {
    color: var(--secondary);
}
</style>
