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

const teachersHeroCanvasRef = ref(null);

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

useFloatingCanvas(teachersHeroCanvasRef, {
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
    <section class="teachers-hero">
        <div
            class="teachers-hero-grid-lines"
            aria-hidden="true"
        >
            <div
                v-for="line in gridLines"
                :key="line"
                class="teachers-hero-grid-line"
                :class="line"
            ></div>
        </div>

        <canvas
            ref="teachersHeroCanvasRef"
            class="teachers-hero-canvas"
            aria-hidden="true"
        ></canvas>

        <div
            class="teachers-hero-decor"
            aria-hidden="true"
        >
            <div
                v-for="circle in circles"
                :key="`teachers-circle-${circle}`"
                class="teachers-hero-circle"
                :class="circle"
            ></div>

            <div
                v-for="glow in glows"
                :key="`teachers-glow-${glow}`"
                class="teachers-hero-glow"
                :class="glow"
            ></div>

            <div
                v-for="line in movingLines"
                :key="`teachers-moving-line-${line}`"
                class="teachers-hero-moving-line"
                :class="line"
            ></div>

            <div
                v-for="dot in floatingDots"
                :key="`teachers-floating-dot-${dot}`"
                class="teachers-hero-floating-dot"
                :class="dot"
            ></div>
        </div>

        <div class="container teachers-hero-container">
            <div class="teachers-hero-content">
                <div class="teachers-hero-top-badges fade-in">
                    <span
                        v-for="badge in content.badges"
                        :key="badge.text"
                        class="teachers-hero-badge"
                    >
                        <BaseIcon
                            :name="badge.icon"
                            size="15"
                        />
                        {{ badge.text }}
                    </span>
                </div>

                <h1 class="teachers-hero-title fade-in">
                    {{ content.title }}
                </h1>

                <p class="teachers-hero-subtitle fade-in">
                    {{ content.subtitle }}
                </p>

                <p class="teachers-hero-description fade-in">
                    {{ content.description }}
                </p>

                <div class="teachers-hero-highlight fade-in">
                    <div
                        v-for="highlight in content.highlights"
                        :key="highlight"
                        class="teachers-hero-highlight-item"
                    >
                        <span class="teachers-hero-highlight-dot"></span>
                        <span>{{ highlight }}</span>
                    </div>
                </div>

                <div class="teachers-hero-actions">
                    <component
                        :is="action.to ? 'RouterLink' : 'a'"
                        v-for="action in content.actions"
                        :key="action.label"
                        :to="action.to"
                        :href="action.href"
                        :class="getActionClass(action)"
                    >
                        {{ action.label }}

                        <BaseIcon
                            v-if="action.icon"
                            :name="action.icon"
                            size="16"
                        />
                    </component>
                </div>
            </div>

            <div class="hero-visual fade-in">
                <div class="hero-visual-shell">
                    <div
                        v-for="ring in rings"
                        :key="`teachers-ring-${ring}`"
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
