<script setup>
import ContactCtaSection from "../../modules/public/contacts/components/ContactCtaSection.vue";
import ContactFeedbackSection from "../../modules/public/contacts/components/ContactFeedbackSection.vue";
import ContactHeroSection from "../../modules/public/contacts/components/ContactHeroSection.vue";
import ContactInfoSection from "../../modules/public/contacts/components/ContactInfoSection.vue";

import {
    contactCta,
    contactFeedback,
    contactHero,
    contactInfo,
} from "../../modules/public/contacts/data/contactsPage.data";
</script>

<template>
    <main class="contact-page">
        <ContactHeroSection :content="contactHero" />

        <ContactInfoSection :content="contactInfo" />

        <ContactFeedbackSection :content="contactFeedback" />

        <ContactCtaSection :content="contactCta" />
    </main>
</template>
