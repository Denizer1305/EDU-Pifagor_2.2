<script setup>
defineProps({
    partner: {
        type: Object,
        required: true,
    },
    mode: {
        type: String,
        default: "diptych",
        validator(value) {
            return ["diptych", "card"].includes(value);
        },
    },
});
</script>

<template>
    <article
        v-if="mode === 'diptych'"
        class="partners-diptych-panel"
        :class="partner.variant"
    >
        <div class="partners-diptych-media">
            <img
                :src="partner.image.src"
                :alt="partner.image.alt"
            />
        </div>

        <div class="partners-diptych-content">
            <div class="partner-tag">
                {{ partner.tag }}
            </div>

            <h4>
                {{ partner.name }}
            </h4>

            <p>
                {{ partner.text }}
            </p>
        </div>
    </article>

    <article
        v-else
        class="partner-card"
    >
        <div class="partner-tag">
            {{ partner.tag }}
        </div>

        <img
            :src="partner.image.src"
            :alt="partner.image.alt"
        />

        <h4>
            {{ partner.name }}
        </h4>

        <p>
            {{ partner.text }}
        </p>
    </article>
</template>
