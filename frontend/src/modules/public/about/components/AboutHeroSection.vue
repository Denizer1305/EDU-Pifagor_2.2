<script setup>
import { ref } from "vue";

import BaseIcon from "../../../../components/ui/BaseIcon.vue";
import { useFloatingCanvas } from "../../shared/composables/useFloatingCanvas";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const aboutHeroCanvasRef = ref(null);

const gridLines = [
    "vertical left",
    "vertical center",
    "vertical right",
    "horizontal top",
    "horizontal bottom",
];

const circles = ["one", "two", "three", "four", "five"];
const glows = ["one", "two", "three"];
const movingLines = ["one", "two", "three", "four"];
const floatingDots = ["one", "two", "three", "four"];
const rings = ["one", "two", "three"];

useFloatingCanvas(aboutHeroCanvasRef, {
    pointsCount: 48,
    lineDistance: 135,
});

function getActionClass(action) {
    return [
        "btn",
        `btn-${action.variant}`,
        "fade-in",
    ];
}
</script>

<template>
    <section class="about-hero">
        <div
            class="about-hero-grid-lines"
            aria-hidden="true"
        >
            <div
                v-for="line in gridLines"
                :key="line"
                class="about-hero-grid-line"
                :class="line"
            ></div>
        </div>

        <canvas
            ref="aboutHeroCanvasRef"
            class="about-hero-canvas"
            aria-hidden="true"
        ></canvas>

        <div
            class="about-hero-decor"
            aria-hidden="true"
        >
            <div
                v-for="circle in circles"
                :key="`about-circle-${circle}`"
                class="about-hero-circle"
                :class="circle"
            ></div>

            <div
                v-for="glow in glows"
                :key="`about-glow-${glow}`"
                class="about-hero-glow"
                :class="glow"
            ></div>

            <div
                v-for="line in movingLines"
                :key="`about-moving-line-${line}`"
                class="about-hero-moving-line"
                :class="line"
            ></div>

            <div
                v-for="dot in floatingDots"
                :key="`about-floating-dot-${dot}`"
                class="about-hero-floating-dot"
                :class="dot"
            ></div>
        </div>

        <div class="container about-hero-container">
            <div class="about-hero-content">
                <div class="about-hero-top-badges fade-in">
                    <span
                        v-for="badge in content.badges"
                        :key="badge.text"
                        class="about-hero-badge"
                    >
                        <BaseIcon
                            :name="badge.icon"
                            size="15"
                        />
                        {{ badge.text }}
                    </span>
                </div>

                <h1 class="about-hero-title fade-in">
                    {{ content.title }}
                </h1>

                <p class="about-hero-subtitle fade-in">
                    {{ content.subtitle }}
                </p>

                <p class="about-hero-description fade-in">
                    {{ content.description }}
                </p>

                <div class="about-hero-highlight fade-in">
                    <div
                        v-for="highlight in content.highlights"
                        :key="highlight"
                        class="about-hero-highlight-item"
                    >
                        <span class="about-hero-highlight-dot"></span>
                        <span>{{ highlight }}</span>
                    </div>
                </div>

                <div class="about-hero-actions">
                    <a
                        v-for="action in content.actions"
                        :key="action.label"
                        :href="action.href"
                        :class="getActionClass(action)"
                    >
                        {{ action.label }}

                        <BaseIcon
                            v-if="action.icon"
                            :name="action.icon"
                            size="16"
                        />
                    </a>
                </div>
            </div>

            <div class="hero-visual fade-in">
                <div class="hero-visual-shell">
                    <div
                        v-for="ring in rings"
                        :key="`about-ring-${ring}`"
                        class="hero-ring"
                        :class="ring"
                    ></div>

                    <div class="hero-dot one"></div>
                    <div class="hero-dot two"></div>

                    <div class="hero-mini-line one"></div>
                    <div class="hero-mini-line two"></div>

                    <div class="hero-greek-mark one">
                        Π
                    </div>

                    <div class="hero-greek-mark two">
                        Δ
                    </div>

                    <div class="hero-logo-wrap">
                        <img
                            :src="content.logo.src"
                            :alt="content.logo.alt"
                        />
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>
