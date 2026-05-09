<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

function getActionClass(action) {
    return [
        "cta-btn",
        action.variant,
    ];
}
</script>

<template>
    <section class="section contact-page-cta">
        <div class="container">
            <div class="contact-page-cta-shell fade-in">
                <h2>
                    {{ content.title }}
                </h2>

                <p>
                    {{ content.text }}
                </p>

                <div class="contact-page-cta-actions">
                    <a
                        v-for="action in content.actions"
                        :key="action.label"
                        :href="action.href"
                        :class="getActionClass(action)"
                    >
                        {{ action.label }}

                        <BaseIcon
                            v-if="action.icon"
                            :name="action.icon"
                            size="16"
                        />
                    </a>
                </div>

                <div class="contact-page-cta-note">
                    {{ content.note }}
                </div>
            </div>
        </div>
    </section>
</template>
