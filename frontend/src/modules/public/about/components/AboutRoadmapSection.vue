<script setup>
import PublicSectionHead from "../../home/shared/components/PublicSectionHead.vue";
import AboutRoadmapStep from "./AboutRoadmapStep.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section class="section about-roadmap">
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <p class="about-roadmap-intro fade-in">
                {{ content.intro }}
            </p>

            <div class="about-roadmap-track">
                <AboutRoadmapStep
                    v-for="stepItem in content.steps"
                    :key="stepItem.title"
                    :step="stepItem"
                />
            </div>
        </div>
    </section>
</template>