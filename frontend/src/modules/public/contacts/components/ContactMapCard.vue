<script setup>
import BaseIcon from "../../../../components/ui/BaseIcon.vue";

defineProps({
    card: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <div
        :id="card.id"
        class="contact-card contact-map-card"
    >
        <div class="contact-map-wrap">
            <div class="contact-map-head">
                <div class="contact-card-topline">
                    <BaseIcon
                        :name="card.topline.icon"
                        size="15"
                    />
                    {{ card.topline.text }}
                </div>

                <h3 class="contact-card-title">
                    {{ card.title }}
                </h3>

                <p class="contact-card-text">
                    {{ card.text }}
                </p>
            </div>

            <a
                :href="card.mapHref"
                class="contact-map-box"
                target="_blank"
                rel="noopener noreferrer"
                :aria-label="`Открыть карту: ${card.address}`"
            >
                <div class="contact-map-placeholder">
                    <div class="contact-map-placeholder-icon">
                        <BaseIcon
                            name="map-location-dot"
                            size="38"
                        />
                    </div>

                    <strong>
                        Открыть адрес на Яндекс Картах
                    </strong>

                    <span>
                        {{ card.address }}
                    </span>
                </div>

                <div class="contact-map-fallback">
                    {{ card.fallback }}
                </div>
            </a>

            <div class="contact-map-note">
                Адрес для навигации:
                <strong>{{ card.address }}</strong>
            </div>
        </div>
    </div>
</template>
