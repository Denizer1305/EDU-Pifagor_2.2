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
    <section class="section teachers-page-cta">
        <div class="container">
            <div class="teachers-page-cta-shell fade-in">
                <h2>
                    {{ content.title }}
                </h2>

                <p>
                    {{ content.text }}
                </p>

                <div class="teachers-page-cta-actions">
                    <RouterLink
                        v-for="action in content.actions"
                        :key="action.label"
                        :to="action.to"
                        :class="getActionClass(action)"
                    >
                        {{ action.label }}

                        <BaseIcon
                            v-if="action.icon"
                            :name="action.icon"
                            size="16"
                        />
                    </RouterLink>
                </div>

                <div class="teachers-page-cta-note">
                    {{ content.note }}
                </div>
            </div>
        </div>
    </section>
</template>
