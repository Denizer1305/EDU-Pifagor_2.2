<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";
import ContactFindCard from "./ContactFindCard.vue";
import ContactMapCard from "./ContactMapCard.vue";
import ContactSocialCard from "./ContactSocialCard.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section
        id="contact-main"
        class="section contact-main"
    >
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="contact-shell fade-in">
                <div class="contact-layout">
                    <div class="contact-column">
                        <div class="contact-card">
                            <div class="contact-card-inner">
                                <div class="contact-card-topline">
                                    <BaseIcon
                                        :name="content.mainCard.topline.icon"
                                        size="15"
                                    />
                                    {{ content.mainCard.topline.text }}
                                </div>

                                <h3 class="contact-card-title">
                                    {{ content.mainCard.title }}
                                </h3>

                                <p class="contact-card-text">
                                    {{ content.mainCard.text }}
                                </p>

                                <div class="contact-info-list">
                                    <div
                                        v-for="item in content.mainCard.items"
                                        :key="item.label"
                                        class="contact-info-item"
                                    >
                                        <div class="contact-info-icon">
                                            <BaseIcon
                                                :name="item.icon"
                                                size="22"
                                            />
                                        </div>

                                        <div>
                                            <strong>{{ item.label }}</strong>

                                            <a
                                                v-if="item.href"
                                                :href="item.href"
                                            >
                                                {{ item.text }}
                                            </a>

                                            <span v-else>
                                                {{ item.text }}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div class="contact-actions">
                                    <a
                                        v-for="action in content.mainCard.actions"
                                        :key="action.label"
                                        :href="action.href"
                                        class="contact-action-chip"
                                    >
                                        <BaseIcon
                                            :name="action.icon"
                                            size="16"
                                        />
                                        {{ action.label }}
                                    </a>
                                </div>
                            </div>
                        </div>

                        <div class="contact-card">
                            <div class="contact-card-inner">
                                <div class="contact-card-topline">
                                    <BaseIcon
                                        :name="content.hoursCard.topline.icon"
                                        size="15"
                                    />
                                    {{ content.hoursCard.topline.text }}
                                </div>

                                <h3 class="contact-card-title">
                                    {{ content.hoursCard.title }}
                                </h3>

                                <p class="contact-card-text">
                                    {{ content.hoursCard.text }}
                                </p>

                                <div class="contact-hours-grid">
                                    <div
                                        v-for="item in content.hoursCard.items"
                                        :key="item.title"
                                        class="contact-hours-item"
                                    >
                                        <strong>{{ item.title }}</strong>
                                        <span>{{ item.text }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="contact-card">
                            <div class="contact-card-inner">
                                <div class="contact-card-topline">
                                    <BaseIcon
                                        :name="content.socialCard.topline.icon"
                                        size="15"
                                    />
                                    {{ content.socialCard.topline.text }}
                                </div>

                                <h3 class="contact-card-title">
                                    {{ content.socialCard.title }}
                                </h3>

                                <p class="contact-card-text">
                                    {{ content.socialCard.text }}
                                </p>

                                <div class="contact-social-grid">
                                    <ContactSocialCard
                                        v-for="social in content.socialCard.socials"
                                        :key="social.title"
                                        :social="social"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="contact-column">
                        <ContactMapCard :card="content.mapCard" />

                        <ContactFindCard :card="content.findCard" />
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
