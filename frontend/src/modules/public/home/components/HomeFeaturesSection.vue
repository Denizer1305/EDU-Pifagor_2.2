<script setup>
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";
import HomeFeatureCard from "./HomeFeatureCard.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section
        id="features"
        class="section features"
    >
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="features-layout">
                <div class="features-col main">
                    <HomeFeatureCard
                        v-for="card in content.mainCards"
                        :key="card.title"
                        :card="card"
                    />
                </div>

                <div class="features-col side">
                    <HomeFeatureCard
                        v-for="card in content.sideCards"
                        :key="card.title"
                        :card="card"
                    />
                </div>
            </div>
        </div>
    </section>
</template>
