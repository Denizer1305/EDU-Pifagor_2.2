<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";
import AboutGratitudeCard from "./AboutGratitudeCard.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section
        id="gratitude"
        class="section gratitude-section"
    >
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="gratitude-architecture">
                <div class="gratitude-column">
                    <AboutGratitudeCard
                        v-for="card in content.leftCards"
                        :key="card.title"
                        :card="card"
                    />
                </div>

                <article class="gratitude-center fade-in">
                    <div class="gratitude-center-inner">
                        <div class="gratitude-center-mark">
                            <BaseIcon
                                :name="content.center.icon"
                                size="30"
                            />
                        </div>

                        <h3 class="gratitude-center-title">
                            {{ content.center.title }}
                        </h3>

                        <p class="gratitude-center-text">
                            {{ content.center.text }}
                        </p>

                        <div class="gratitude-center-note">
                            {{ content.center.note }}
                        </div>
                    </div>
                </article>

                <div class="gratitude-column">
                    <AboutGratitudeCard
                        v-for="card in content.rightCards"
                        :key="card.title"
                        :card="card"
                    />
                </div>
            </div>
        </div>
    </section>
</template>
