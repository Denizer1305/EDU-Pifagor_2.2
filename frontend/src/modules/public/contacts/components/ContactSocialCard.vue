<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

defineProps({
    social: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <a
        :href="social.href"
        class="contact-social-card"
    >
        <span class="contact-social-icon">
            <BaseIcon
                :name="social.name || social.icon || social.title"
                size="22"
            />
        </span>

        <strong>{{ social.title }}</strong>
        <span>{{ social.text }}</span>
    </a>
</template>
