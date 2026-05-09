<script setup>
import { computed, useId } from "vue";

import FormError from "./FormError.vue";

const props = defineProps({
    id: {
        type: String,
        default: "",
    },
    label: {
        type: String,
        default: "",
    },
    hint: {
        type: String,
        default: "",
    },
    error: {
        type: String,
        default: "",
    },
    required: {
        type: Boolean,
        default: false,
    },
});

const generatedId = useId();

const fieldId = computed(() => {
    return props.id || `form-field-${generatedId}`;
});
</script>

<template>
    <div class="form-field">
        <label
            v-if="label"
            :for="fieldId"
            class="form-field__label"
        >
            {{ label }}

            <span
                v-if="required"
                class="form-field__required"
                aria-hidden="true"
            >
                *
            </span>
        </label>

        <slot :id="fieldId" />

        <FormError
            v-if="error"
            :message="error"
        />

        <p
            v-else-if="hint"
            class="form-field__hint"
        >
            {{ hint }}
        </p>
    </div>
</template>

<style scoped>
.form-field {
    display: grid;
    gap: 8px;
}

.form-field__label {
    color: var(--primary);
    font-size: 0.9rem;
    font-weight: var(--font-weight-bold);
    line-height: 1.35;
}

.form-field__required {
    color: var(--danger, #c94a4a);
}

.form-field__hint {
    margin: 0;
    color: var(--secondary);
    font-size: 0.8rem;
    line-height: 1.5;
}
</style>
