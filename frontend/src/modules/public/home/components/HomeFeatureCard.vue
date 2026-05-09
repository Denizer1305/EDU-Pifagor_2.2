<script setup>
defineProps({
    card: {
        type: Object,
        required: true,
    },
});

const diagramBars = ["h1", "h2", "h3", "h4", "h5"];
</script>

<template>
    <article
        class="feature-card fade-in"
        :class="card.variant"
    >
        <div class="feature-content">
            <div class="feature-topline">
                <i :class="card.icon"></i>
                {{ card.label }}
            </div>

            <h3 class="feature-title">
                {{ card.title }}
            </h3>

            <p class="feature-description">
                {{ card.description }}
            </p>

            <ul
                v-if="card.points?.length"
                class="feature-points"
            >
                <li
                    v-for="point in card.points"
                    :key="point"
                >
                    <i class="fas fa-circle"></i>
                    <span>{{ point }}</span>
                </li>
            </ul>

            <div
                v-if="card.icons?.length"
                class="feature-icon-row"
            >
                <div
                    v-for="icon in card.icons"
                    :key="icon"
                    class="feature-icon-pill"
                >
                    <i :class="icon"></i>
                </div>
            </div>

            <div
                v-if="card.chips?.length"
                class="feature-side-grid"
            >
                <div
                    v-for="chip in card.chips"
                    :key="chip.title"
                    class="feature-chip"
                >
                    <strong>{{ chip.title }}</strong>
                    <span>{{ chip.text }}</span>
                </div>
            </div>

            <div
                v-if="card.hasDiagram"
                class="feature-mini-diagram"
            >
                <div class="feature-bars">
                    <div
                        v-for="bar in diagramBars"
                        :key="bar"
                        class="feature-bar"
                        :class="bar"
                    ></div>
                </div>
            </div>

            <div
                v-if="card.stats?.length"
                class="feature-stats"
            >
                <div
                    v-for="stat in card.stats"
                    :key="stat.value"
                    class="feature-stat"
                >
                    <strong>{{ stat.value }}</strong>
                    <span>{{ stat.text }}</span>
                </div>
            </div>
        </div>

        <div
            v-if="card.hasOrbit"
            class="feature-visual"
        >
            <div class="feature-visual-grid">
                <div class="feature-orbit">
                    <div class="feature-orbit-dot"></div>
                </div>
            </div>
        </div>
    </article>
</template>