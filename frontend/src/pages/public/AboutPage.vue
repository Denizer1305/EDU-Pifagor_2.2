<script setup>
import AboutCtaSection from "../../modules/public/about/components/AboutCtaSection.vue";
import AboutGratitudeSection from "../../modules/public/about/components/AboutGratitudeSection.vue";
import AboutHeroSection from "../../modules/public/about/components/AboutHeroSection.vue";
import AboutMissionSection from "../../modules/public/about/components/AboutMissionSection.vue";
import AboutRoadmapSection from "../../modules/public/about/components/AboutRoadmapSection.vue";
import AboutStorySection from "../../modules/public/about/components/AboutStorySection.vue";
import AboutTeamSection from "../../modules/public/about/components/AboutTeamSection.vue";

import {
    aboutCta,
    aboutGratitude,
    aboutHero,
    aboutMission,
    aboutRoadmap,
    aboutStory,
    aboutTeam,
} from "../../modules/public/about/data/aboutPage.data";
</script>

<template>
    <main class="about-page">
        <AboutHeroSection :content="aboutHero" />

        <AboutStorySection :content="aboutStory" />

        <AboutMissionSection :content="aboutMission" />

        <AboutRoadmapSection :content="aboutRoadmap" />

        <AboutTeamSection :content="aboutTeam" />

        <AboutGratitudeSection :content="aboutGratitude" />

        <AboutCtaSection :content="aboutCta" />
    </main>
</template>
