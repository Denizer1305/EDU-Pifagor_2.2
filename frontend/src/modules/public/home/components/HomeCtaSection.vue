<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const ctaLines = ["one", "two", "three"];
const ctaCircles = ["one", "two"];
const ctaGlows = ["one", "two"];
const ctaParticles = ["one", "two", "three"];
const ctaRipples = ["one", "two"];

function getActionClass(action) {
    return [
        "cta-btn",
        action.variant,
    ];
}
</script>

<template>
    <section
        id="cta"
        class="section cta-section"
    >
        <div
            class="cta-bg"
            aria-hidden="true"
        >
            <div
                v-for="line in ctaLines"
                :key="`cta-line-${line}`"
                class="cta-line"
                :class="line"
            ></div>

            <div
                v-for="circle in ctaCircles"
                :key="`cta-circle-${circle}`"
                class="cta-circle"
                :class="circle"
            ></div>

            <div
                v-for="glow in ctaGlows"
                :key="`cta-glow-${glow}`"
                class="cta-glow"
                :class="glow"
            ></div>

            <div
                v-for="particle in ctaParticles"
                :key="`cta-particle-${particle}`"
                class="cta-particle"
                :class="particle"
            ></div>

            <div
                v-for="ripple in ctaRipples"
                :key="`cta-ripple-${ripple}`"
                class="cta-ripple"
                :class="ripple"
            ></div>
        </div>

        <div class="container">
            <div class="cta-shell fade-in">
                <div class="cta-content">
                    <h2>
                        {{ content.title }}
                    </h2>

                    <p>
                        {{ content.text }}
                    </p>
                </div>

                <div class="cta-actions">
                    <RouterLink
                        v-for="action in content.actions"
                        :key="action.label"
                        :to="action.to"
                        :class="getActionClass(action)"
                    >
                        {{ action.label }}

                        <BaseIcon
                            v-if="action.icon"
                            :name="action.icon"
                            size="16"
                        />
                    </RouterLink>
                </div>
            </div>
        </div>
    </section>
</template>
