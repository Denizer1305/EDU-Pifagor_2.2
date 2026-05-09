<script setup>
defineProps({
    item: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <article class="ai-mini-card">
        <div class="ai-mini-top">
            <div class="ai-mini-icon">
                <i :class="item.icon"></i>
            </div>

            <div class="ai-mini-title">
                {{ item.title }}
            </div>
        </div>

        <div class="ai-mini-text">
            {{ item.text }}
        </div>
    </article>
</template>