<script setup>
import { onBeforeUnmount, watch } from "vue";

import BaseIcon from "./BaseIcon.vue";

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false,
    },
    title: {
        type: String,
        default: "",
    },
    size: {
        type: String,
        default: "md",
        validator(value) {
            return ["sm", "md", "lg", "xl"].includes(value);
        },
    },
    closeOnOverlay: {
        type: Boolean,
        default: true,
    },
});

const emit = defineEmits({
    "update:modelValue": (value) => typeof value === "boolean",
    close: null,
});

function closeModal() {
    emit("update:modelValue", false);
    emit("close");
}

function handleOverlayClick() {
    if (props.closeOnOverlay) {
        closeModal();
    }
}

function handleKeydown(event) {
    if (event.key === "Escape" && props.modelValue) {
        closeModal();
    }
}

watch(
    () => props.modelValue,
    (isOpen) => {
        document.body.classList.toggle("is-modal-open", isOpen);

        if (isOpen) {
            window.addEventListener("keydown", handleKeydown);
            return;
        }

        window.removeEventListener("keydown", handleKeydown);
    },
);

onBeforeUnmount(() => {
    document.body.classList.remove("is-modal-open");
    window.removeEventListener("keydown", handleKeydown);
});
</script>

<template>
    <Teleport to="body">
        <div
            v-if="modelValue"
            class="base-modal"
            role="presentation"
            @click.self="handleOverlayClick"
        >
            <section
                class="base-modal__window"
                :class="`base-modal__window--${size}`"
                role="dialog"
                aria-modal="true"
                :aria-label="title || 'Модальное окно'"
            >
                <header class="base-modal__header">
                    <h3
                        v-if="title"
                        class="base-modal__title"
                    >
                        {{ title }}
                    </h3>

                    <button
                        type="button"
                        class="base-modal__close"
                        aria-label="Закрыть окно"
                        @click="closeModal"
                    >
                        <BaseIcon
                            name="close"
                            size="18"
                        />
                    </button>
                </header>

                <div class="base-modal__body">
                    <slot />
                </div>

                <footer
                    v-if="$slots.footer"
                    class="base-modal__footer"
                >
                    <slot name="footer" />
                </footer>
            </section>
        </div>
    </Teleport>
</template>

<style scoped>
.base-modal {
    position: fixed;
    inset: 0;
    z-index: var(--z-modal);
    display: grid;
    place-items: center;
    padding: 24px;
    background: rgba(19, 25, 35, 0.58);
    backdrop-filter: var(--blur-sm);
}

.base-modal__window {
    width: min(100%, 720px);
    max-height: calc(100vh - 48px);
    overflow: hidden;
    border: 1px solid var(--white-14);
    border-radius: var(--radius-32);
    background: var(--surface-glass-max);
    box-shadow: 0 32px 80px var(--black-28);
    backdrop-filter: var(--backdrop-glass-strong);
}

.base-modal__window--sm {
    max-width: 460px;
}

.base-modal__window--md {
    max-width: 720px;
}

.base-modal__window--lg {
    max-width: 980px;
}

.base-modal__window--xl {
    max-width: 1180px;
}

.base-modal__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding: 22px 24px;
    border-bottom: 1px solid var(--primary-08);
}

.base-modal__title {
    margin: 0;
    color: var(--primary);
    font-size: clamp(1.4rem, 2.5vw, 2rem);
}

.base-modal__close {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-14);
    color: var(--primary);
    background: var(--white-90);
    cursor: pointer;
    transition: var(--transition-soft);
}

.base-modal__close:hover {
    color: var(--accent);
    transform: rotate(90deg);
}

.base-modal__body {
    max-height: calc(100vh - 180px);
    overflow-y: auto;
    padding: 24px;
}

.base-modal__footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 18px 24px;
    border-top: 1px solid var(--primary-08);
}
</style>
