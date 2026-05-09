<script setup>
import { onBeforeUnmount, watch } from "vue";

import BaseIcon from "../../../../components/ui/BaseIcon.vue";

const props = defineProps({
    teacher: {
        type: Object,
        default: null,
    },
    isOpen: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits({
    close: null,
});

function closeModal() {
    emit("close");
}

function handleKeydown(event) {
    if (event.key === "Escape") {
        closeModal();
    }
}

watch(
    () => props.isOpen,
    (isOpen) => {
        if (isOpen) {
            document.body.classList.add("is-modal-open");
            window.addEventListener("keydown", handleKeydown);
            return;
        }

        document.body.classList.remove("is-modal-open");
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
            v-if="isOpen && teacher"
            class="teacher-modal-overlay"
            role="presentation"
            @click.self="closeModal"
        >
            <div
                class="teacher-modal-window"
                role="dialog"
                aria-modal="true"
                :aria-labelledby="`${teacher.id}-title`"
            >
                <button
                    class="teacher-modal-close"
                    type="button"
                    aria-label="Закрыть окно"
                    @click="closeModal"
                >
                    <BaseIcon
                        name="close"
                        size="18"
                    />
                </button>

                <div class="teacher-modal-content">
                    <div class="teacher-modal-media">
                        <img
                            :src="teacher.image.src"
                            :alt="teacher.image.alt"
                        />
                    </div>

                    <div class="teacher-modal-panel">
                        <div class="teacher-modal-topline">
                            {{ teacher.role }}
                        </div>

                        <h3
                            :id="`${teacher.id}-title`"
                            class="teacher-modal-name"
                        >
                            {{ teacher.name }}
                        </h3>

                        <div class="teacher-modal-subject">
                            {{ teacher.direction }}
                        </div>

                        <p class="teacher-modal-description">
                            {{ teacher.description }}
                        </p>

                        <div
                            v-if="teacher.tags?.length"
                            class="teacher-modal-tags"
                        >
                            <span
                                v-for="tag in teacher.tags"
                                :key="tag"
                                class="teacher-modal-tag"
                            >
                                {{ tag }}
                            </span>
                        </div>

                        <div class="teacher-modal-section">
                            <div class="teacher-modal-section-title">
                                Награды и достижения
                            </div>

                            <ul class="teacher-modal-awards">
                                <li
                                    v-for="award in teacher.awards"
                                    :key="award"
                                >
                                    <BaseIcon
                                        name="award"
                                        size="17"
                                    />
                                    <span>{{ award }}</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </Teleport>
</template>
