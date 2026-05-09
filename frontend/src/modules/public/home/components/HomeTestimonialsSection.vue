<script setup>
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";
import HomeTestimonialCard from "./HomeTestimonialCard.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section
        id="testimonials"
        class="section testimonials-section"
    >
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="testimonials-shell fade-in">
                <div class="testimonials-mosaic">
                    <HomeTestimonialCard
                        v-for="testimonial in content.items"
                        :key="testimonial.name"
                        :testimonial="testimonial"
                    />
                </div>
            </div>
        </div>
    </section>
</template>
