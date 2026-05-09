<script setup>
import HomeAiSection from "@/modules/public/home/components/HomeAiSection.vue";
import HomeCtaSection from "@/modules/public/home/components/HomeCtaSection.vue";
import HomeFeaturesSection from "@/modules/public/home/components/HomeFeaturesSection.vue";
import HomeHeroSection from "@/modules/public/home/components/HomeHeroSection.vue";
import HomePartnersSection from "@/modules/public/home/components/HomePartnersSection.vue";
import HomeTestimonialsSection from "@/modules/public/home/components/HomeTestimonialsSection.vue";

import {
    homeAi,
    homeCta,
    homeFeatures,
    homeHero,
    homePartners,
    homeTestimonials,
} from "@/modules/public/home/data/homePage.data";
</script>

<template>
    <main class="home-page">
        <HomeHeroSection :content="homeHero" />

        <HomeFeaturesSection :content="homeFeatures" />

        <HomeAiSection :content="homeAi" />

        <HomePartnersSection :content="homePartners" />

        <HomeTestimonialsSection :content="homeTestimonials" />

        <HomeCtaSection :content="homeCta" />
    </main>
</template>