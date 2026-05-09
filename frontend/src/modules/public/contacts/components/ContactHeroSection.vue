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

const contactHeroCanvasRef = ref(null);

const gridLines = [
    "vertical left",
    "vertical center",
    "vertical right",
    "horizontal top",
    "horizontal bottom",
];

const circles = ["one", "two", "three", "four"];
const glows = ["one", "two", "three"];
const movingLines = ["one", "two", "three", "four"];
const floatingDots = ["one", "two", "three", "four"];
const rings = ["one", "two", "three"];

useFloatingCanvas(contactHeroCanvasRef, {
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
    <section class="contact-hero">
        <div
            class="contact-hero-grid-lines"
            aria-hidden="true"
        >
            <div
                v-for="line in gridLines"
                :key="line"
                class="contact-hero-grid-line"
                :class="line"
            ></div>
        </div>

        <canvas
            ref="contactHeroCanvasRef"
            class="contact-hero-canvas"
            aria-hidden="true"
        ></canvas>

        <div
            class="contact-hero-decor"
            aria-hidden="true"
        >
            <div
                v-for="circle in circles"
                :key="`contact-circle-${circle}`"
                class="contact-hero-circle"
                :class="circle"
            ></div>

            <div
                v-for="glow in glows"
                :key="`contact-glow-${glow}`"
                class="contact-hero-glow"
                :class="glow"
            ></div>

            <div
                v-for="line in movingLines"
                :key="`contact-line-${line}`"
                class="contact-hero-moving-line"
                :class="line"
            ></div>

            <div
                v-for="dot in floatingDots"
                :key="`contact-dot-${dot}`"
                class="contact-hero-floating-dot"
                :class="dot"
            ></div>
        </div>

        <div class="container contact-hero-container">
            <div class="contact-hero-content">
                <div class="contact-hero-top-badges fade-in">
                    <span
                        v-for="badge in content.badges"
                        :key="badge.text"
                        class="contact-hero-badge"
                    >
                        <BaseIcon
                            :name="badge.icon"
                            size="15"
                        />
                        {{ badge.text }}
                    </span>
                </div>

                <h1 class="contact-hero-title fade-in">
                    {{ content.title }}
                </h1>

                <p class="contact-hero-subtitle fade-in">
                    {{ content.subtitle }}
                </p>

                <p class="contact-hero-description fade-in">
                    {{ content.description }}
                </p>

                <div class="contact-hero-highlight fade-in">
                    <div
                        v-for="highlight in content.highlights"
                        :key="highlight"
                        class="contact-hero-highlight-item"
                    >
                        <span class="contact-hero-highlight-dot"></span>
                        <span>{{ highlight }}</span>
                    </div>
                </div>

                <div class="contact-hero-actions">
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
                        :key="`contact-ring-${ring}`"
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
