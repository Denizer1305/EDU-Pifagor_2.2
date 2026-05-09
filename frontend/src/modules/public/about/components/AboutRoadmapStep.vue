<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

defineProps({
    step: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <div class="about-roadmap-step fade-in">
        <div class="about-roadmap-card">
            <h3>
                {{ step.title }}
            </h3>

            <p>
                {{ step.text }}
            </p>

            <ul>
                <li
                    v-for="point in step.points"
                    :key="point"
                >
                    <BaseIcon
                        name="check-circle"
                        size="15"
                    />
                    <span>{{ point }}</span>
                </li>
            </ul>
        </div>
    </div>
</template>
