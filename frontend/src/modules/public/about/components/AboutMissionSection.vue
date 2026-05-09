<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section class="section about-mission">
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="about-mission-shell fade-in">
                <div class="about-mission-layout">
                    <div class="about-mission-main">
                        <div class="about-mission-panel about-mission-panel-lead">
                            <span class="about-mission-kicker">
                                {{ content.lead.kicker }}
                            </span>

                            <h3>
                                {{ content.lead.title }}
                            </h3>

                            <p
                                v-for="paragraph in content.lead.paragraphs"
                                :key="paragraph"
                            >
                                {{ paragraph }}
                            </p>
                        </div>

                        <div class="about-mission-values">
                            <div
                                v-for="value in content.values"
                                :key="value.title"
                                class="about-mission-value"
                            >
                                <strong>{{ value.title }}</strong>
                                <span>{{ value.text }}</span>
                            </div>
                        </div>
                    </div>

                    <aside class="about-mission-side">
                        <div
                            v-for="card in content.sideCards"
                            :key="card.title"
                            class="about-mission-side-card"
                        >
                            <div class="about-mission-side-icon">
                                <BaseIcon
                                    :name="card.icon"
                                    size="25"
                                />
                            </div>

                            <h4>
                                {{ card.title }}
                            </h4>

                            <p>
                                {{ card.text }}
                            </p>
                        </div>
                    </aside>
                </div>
            </div>
        </div>
    </section>
</template>
