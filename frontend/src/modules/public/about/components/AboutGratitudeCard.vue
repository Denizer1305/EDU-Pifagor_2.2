<script setup>
defineProps({
    card: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <article class="gratitude-card fade-in">
        <div class="gratitude-card-inner">
            <div class="gratitude-card-icon">
                <i :class="card.icon"></i>
            </div>

            <h3>
                {{ card.title }}
            </h3>

            <div
                v-if="card.tag"
                class="gratitude-person-tag"
            >
                {{ card.tag }}
            </div>

            <p>
                {{ card.text }}
            </p>

            <ul
                v-if="card.points?.length"
                class="gratitude-list"
            >
                <li
                    v-for="point in card.points"
                    :key="point"
                >
                    <i class="fas fa-check-circle"></i>
                    <span>{{ point }}</span>
                </li>
            </ul>
        </div>
    </article>
</template>