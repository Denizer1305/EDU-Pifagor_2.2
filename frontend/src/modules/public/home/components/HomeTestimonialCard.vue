<script setup>
defineProps({
    testimonial: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <article
        class="testimonial-panel"
        :class="testimonial.variant"
    >
        <div class="testimonial-photo">
            <img
                :src="testimonial.image.src"
                :alt="testimonial.image.alt"
            />
        </div>

        <div class="testimonial-copy">
            <div
                class="testimonial-quote-mark"
                aria-hidden="true"
            >
                “
            </div>

            <div class="testimonial-name">
                {{ testimonial.name }}
            </div>

            <div class="testimonial-text">
                {{ testimonial.text }}
            </div>
        </div>
    </article>
</template>
