<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";
import HomePartnerCard from "./HomePartnerCard.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section
        id="partners"
        class="section partners-section"
    >
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="partners-shell fade-in">
                <div class="partners-intro">
                    <article class="partners-intro-card">
                        <div class="partners-kicker">
                            {{ content.intro.label }}
                        </div>

                        <h3>
                            {{ content.intro.title }}
                        </h3>

                        <p>
                            {{ content.intro.text }}
                        </p>
                    </article>
                </div>

                <div
                    class="partners-diptych"
                    aria-label="Партнёры платформы"
                >
                    <HomePartnerCard
                        v-if="content.items?.[0]"
                        :partner="content.items[0]"
                    />

                    <div
                        class="partners-accent"
                        aria-hidden="true"
                    >
                        <div class="partners-accent-mark">
                            <BaseIcon
                                :name="content.accent.icon"
                                size="28"
                            />
                        </div>

                        <h4>
                            {{ content.accent.title }}
                        </h4>

                        <p>
                            {{ content.accent.text }}
                        </p>
                    </div>

                    <HomePartnerCard
                        v-if="content.items?.[1]"
                        :partner="content.items[1]"
                    />
                </div>

                <div class="partners-grid mobile-only">
                    <HomePartnerCard
                        v-for="partner in content.items"
                        :key="partner.name"
                        :partner="partner"
                        mode="card"
                    />
                </div>
            </div>
        </div>
    </section>
</template>
