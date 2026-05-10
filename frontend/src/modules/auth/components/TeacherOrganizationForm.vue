<script setup>
import { computed, ref } from "vue";
import { RouterLink } from "vue-router";

import BaseIcon from "../../../components/ui/BaseIcon.vue";
import { useTeacherOrganizationCode } from "../composables/useTeacherOrganizationCode";

const props = defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const {
    organizationCode,
    normalizedCode,
    isCodeReady,
    updateOrganizationCode,
    clearOrganizationCode,
} = useTeacherOrganizationCode();

const status = ref("idle");

const statusMessage = computed(() => {
    return props.content.statuses[status.value] || props.content.statuses.idle;
});

function submitOrganizationCode() {
    /*
     * Следующий этап:
     * POST /api/v1/organizations/teacher/join/
     *
     * payload:
     * {
     *     code: normalizedCode.value
     * }
     *
     * Ожидаемый backend-ответ:
     * {
     *     id: number,
     *     organization: {...},
     *     teacher: {...},
     *     status: "pending" | "active",
     *     submitted_at: string
     * }
     */

    if (!isCodeReady.value) {
        status.value = "invalid";
        return;
    }

    status.value = "pending";
}

function resetForm() {
    clearOrganizationCode();
    status.value = "idle";
}
</script>

<template>
    <section class="auth-form-shell fade-in">
        <div class="auth-form-inner">
            <div class="auth-form-topline">
                <BaseIcon
                    :name="content.topline.icon"
                    size="14"
                />

                <span>{{ content.topline.text }}</span>
            </div>

            <h2 class="auth-form-title">
                {{ content.title }}
            </h2>

            <p class="auth-form-description">
                {{ content.description }}
            </p>

            <form
                class="registration-form"
                @submit.prevent="submitOrganizationCode"
            >
                <div class="form-group full">
                    <label
                        class="form-label"
                        for="teacher-organization-code"
                    >
                        {{ content.fields.code.label }}
                    </label>

                    <div class="teacher-organization-code-shell">
                        <input
                            id="teacher-organization-code"
                            :value="organizationCode"
                            name="organization_code"
                            type="text"
                            inputmode="text"
                            autocomplete="one-time-code"
                            :placeholder="content.fields.code.placeholder"
                            required
                            @input="updateOrganizationCode($event.target.value)"
                        />

                        <button
                            v-if="organizationCode"
                            type="button"
                            class="teacher-organization-code-clear"
                            aria-label="Очистить код"
                            @click="resetForm"
                        >
                            <BaseIcon
                                name="close"
                                size="15"
                            />
                        </button>
                    </div>

                    <div class="teacher-organization-code-preview">
                        <span>{{ content.fields.code.previewLabel }}</span>

                        <strong>
                            {{ normalizedCode || content.fields.code.previewEmpty }}
                        </strong>
                    </div>
                </div>

                <div
                    class="teacher-organization-status"
                    :class="`teacher-organization-status--${statusMessage.variant}`"
                >
                    <BaseIcon
                        :name="statusMessage.icon"
                        size="18"
                    />

                    <div>
                        <strong>{{ statusMessage.title }}</strong>
                        <span>{{ statusMessage.text }}</span>
                    </div>
                </div>

                <div class="form-actions">
                    <button
                        class="btn btn-primary auth-submit"
                        type="submit"
                        :disabled="!isCodeReady"
                    >
                        {{ content.submitLabel }}

                        <BaseIcon
                            name="arrow-right"
                            size="15"
                        />
                    </button>

                    <RouterLink
                        class="teacher-organization-secondary-link"
                        :to="content.backLink.to"
                    >
                        {{ content.backLink.label }}
                    </RouterLink>
                </div>

                <div class="teacher-organization-help-box">
                    {{ content.help.text }}

                    <a :href="content.help.href">
                        {{ content.help.label }}
                    </a>
                </div>

                <div class="auth-legal">
                    {{ content.legal }}
                </div>
            </form>
        </div>
    </section>
</template>
