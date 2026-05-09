<script setup>
import PublicSectionHead from "../../home/shared/components/PublicSectionHead.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <section class="section platform-story">
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="platform-story-layout">
                <div class="platform-story-main fade-in">
                    <h3 class="platform-story-title">
                        {{ content.main.title }}
                    </h3>

                    <p
                        v-for="paragraph in content.main.paragraphs"
                        :key="paragraph"
                        class="platform-story-text"
                    >
                        {{ paragraph }}
                    </p>

                    <div class="platform-story-points">
                        <div
                            v-for="point in content.main.points"
                            :key="point.title"
                            class="platform-story-point"
                        >
                            <i :class="point.icon"></i>

                            <div>
                                <strong>{{ point.title }}</strong>
                                <span>{{ point.text }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <aside class="platform-story-side fade-in">
                    <div
                        v-for="card in content.sideCards"
                        :key="card.title"
                        class="platform-story-side-card"
                    >
                        <h4>
                            {{ card.title }}
                        </h4>

                        <p>
                            {{ card.text }}
                        </p>
                    </div>
                </aside>

                <div class="platform-story-bottom fade-in">
                    <div class="origin-showcase">
                        <div
                            class="origin-decor"
                            aria-hidden="true"
                        >
                            <div class="origin-decor-line top"></div>
                            <div class="origin-decor-line bottom"></div>
                            <div class="origin-decor-dot one"></div>
                            <div class="origin-decor-dot two"></div>
                        </div>

                        <div class="origin-text-col">
                            <div class="origin-icon-badge">
                                <i :class="content.origin.badge.icon"></i>
                                <span>{{ content.origin.badge.text }}</span>
                            </div>

                            <h3>
                                {{ content.origin.title }}
                            </h3>

                            <p>
                                {{ content.origin.text }}
                            </p>

                            <div class="origin-highlight">
                                <i :class="content.origin.highlight.icon"></i>
                                <span>{{ content.origin.highlight.text }}</span>
                            </div>
                        </div>

                        <div class="origin-media-col">
                            <div class="origin-media-wrapper">
                                <img
                                    :src="content.origin.image.src"
                                    :alt="content.origin.image.alt"
                                />

                                <div class="origin-media-overlay">
                                    <strong>
                                        {{ content.origin.overlay.title }}
                                    </strong>

                                    <span>
                                        {{ content.origin.overlay.text }}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>