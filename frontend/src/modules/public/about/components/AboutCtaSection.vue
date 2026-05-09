<script setup>
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
    <section class="section about-page-cta">
        <div class="container">
            <div class="about-page-cta-shell fade-in">
                <h2>
                    {{ content.title }}
                </h2>

                <p>
                    {{ content.text }}
                </p>

                <div class="about-page-cta-actions">
                    <RouterLink
                        v-for="action in content.actions"
                        :key="action.label"
                        :to="action.to"
                        :class="getActionClass(action)"
                    >
                        {{ action.label }}

                        <i
                            v-if="action.icon"
                            :class="action.icon"
                        ></i>
                    </RouterLink>
                </div>

                <div class="about-page-cta-note">
                    {{ content.note }}
                </div>
            </div>
        </div>
    </section>
</template>