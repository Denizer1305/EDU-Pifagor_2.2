<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";
import { useContactFeedbackForm } from "../composables/useContactFeedbackForm";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const {
    form,
    isSubmitted,
    updateFiles,
    resetForm,
    submitForm,
} = useContactFeedbackForm();
</script>

<template>
    <section class="section contact-form-section">
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="contact-form-wrapper fade-in">
                <div class="contact-form-card-full">
                    <form
                        class="contact-feedback-form"
                        @submit.prevent="submitForm"
                    >
                        <div class="form-row">
                            <div class="form-group">
                                <label
                                    for="cf-name"
                                    class="form-label"
                                >
                                    {{ content.fields.name.label }}
                                </label>

                                <input
                                    id="cf-name"
                                    v-model="form.name"
                                    type="text"
                                    name="name"
                                    class="form-input"
                                    :placeholder="content.fields.name.placeholder"
                                    required
                                />
                            </div>

                            <div class="form-group">
                                <label
                                    for="cf-email"
                                    class="form-label"
                                >
                                    {{ content.fields.email.label }}
                                </label>

                                <input
                                    id="cf-email"
                                    v-model="form.email"
                                    type="email"
                                    name="email"
                                    class="form-input"
                                    :placeholder="content.fields.email.placeholder"
                                    required
                                />
                            </div>
                        </div>

                        <div class="form-group">
                            <label
                                for="cf-message"
                                class="form-label"
                            >
                                {{ content.fields.message.label }}
                            </label>

                            <textarea
                                id="cf-message"
                                v-model="form.message"
                                name="message"
                                class="form-textarea"
                                :placeholder="content.fields.message.placeholder"
                                required
                            ></textarea>
                        </div>

                        <div class="form-group">
                            <label
                                for="cf-attachments"
                                class="form-label"
                            >
                                {{ content.fields.files.label }}
                            </label>

                            <div class="file-upload-wrapper">
                                <input
                                    id="cf-attachments"
                                    type="file"
                                    name="attachments[]"
                                    class="form-file"
                                    multiple
                                    accept="image/*,.pdf,.doc,.docx"
                                    @change="updateFiles"
                                />

                                <span class="file-upload-hint">
                                    {{ content.fields.files.hint }}
                                </span>

                                <span
                                    v-if="form.files.length"
                                    class="file-upload-count"
                                >
                                    Выбрано файлов: {{ form.files.length }}
                                </span>
                            </div>
                        </div>

                        <div class="form-checkbox">
                            <input
                                id="cf-consent"
                                v-model="form.consent"
                                type="checkbox"
                                name="consent"
                                required
                            />

                            <label for="cf-consent">
                                {{ content.fields.consent }}
                            </label>
                        </div>

                        <div
                            v-if="isSubmitted"
                            class="contact-form-success"
                        >
                            <BaseIcon
                                name="check-circle"
                                size="18"
                            />
                            <span>{{ content.successMessage }}</span>
                        </div>

                        <div class="contact-form-actions">
                            <button
                                type="submit"
                                class="form-submit-btn"
                            >
                                <BaseIcon
                                    name="paper-plane"
                                    size="17"
                                />
                                {{ content.submitLabel }}
                            </button>

                            <button
                                v-if="isSubmitted"
                                type="button"
                                class="form-reset-btn"
                                @click="resetForm"
                            >
                                Заполнить заново
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </section>
</template>
