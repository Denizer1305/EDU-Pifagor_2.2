<script setup>
import BaseButton from "../ui/BaseButton.vue";
import BaseModal from "../ui/BaseModal.vue";

const model = defineModel({
    type: Boolean,
    default: false,
});

defineProps({
    title: {
        type: String,
        default: "Подтвердите действие",
    },
    message: {
        type: String,
        default: "Вы уверены, что хотите продолжить?",
    },
    confirmLabel: {
        type: String,
        default: "Подтвердить",
    },
    cancelLabel: {
        type: String,
        default: "Отмена",
    },
    confirmVariant: {
        type: String,
        default: "danger",
    },
    loading: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits({
    confirm: null,
    cancel: null,
});

function cancelDialog() {
    model.value = false;
    emit("cancel");
}

function confirmDialog() {
    emit("confirm");
}
</script>

<template>
    <BaseModal
        v-model="model"
        :title="title"
        size="sm"
        @close="cancelDialog"
    >
        <p class="confirm-dialog__message">
            <slot>{{ message }}</slot>
        </p>

        <template #footer>
            <BaseButton
                variant="secondary"
                :disabled="loading"
                @click="cancelDialog"
            >
                {{ cancelLabel }}
            </BaseButton>

            <BaseButton
                :variant="confirmVariant"
                :loading="loading"
                @click="confirmDialog"
            >
                {{ confirmLabel }}
            </BaseButton>
        </template>
    </BaseModal>
</template>

<style scoped>
.confirm-dialog__message {
    margin: 0;
    color: var(--secondary);
    font-size: 0.94rem;
    line-height: 1.7;
}
</style>
