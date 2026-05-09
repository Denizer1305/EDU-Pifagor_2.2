<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

defineProps({
    card: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <div class="contact-card contact-find-card">
        <div class="contact-card-inner">
            <div class="contact-card-topline">
                <BaseIcon
                    :name="card.topline.icon"
                    size="15"
                />
                {{ card.topline.text }}
            </div>

            <h3 class="contact-card-title">
                {{ card.title }}
            </h3>

            <p class="contact-card-text">
                {{ card.text }}
            </p>

            <div class="contact-find-steps">
                <div
                    v-for="step in card.steps"
                    :key="step.number"
                    class="contact-find-step"
                >
                    <div class="contact-find-step-number">
                        {{ step.number }}
                    </div>

                    <div>
                        <strong>{{ step.title }}</strong>
                        <span>{{ step.text }}</span>
                    </div>
                </div>
            </div>

            <ul class="contact-note-list">
                <li
                    v-for="note in card.notes"
                    :key="note"
                >
                    <BaseIcon
                        name="check-circle"
                        size="15"
                    />
                    <span>{{ note }}</span>
                </li>
            </ul>
        </div>
    </div>
</template>
