<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

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
                <BaseIcon
                    :name="item.icon"
                    size="22"
                />
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
