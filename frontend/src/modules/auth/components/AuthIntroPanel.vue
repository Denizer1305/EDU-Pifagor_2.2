<script setup>
import { BaseIcon } from "../../../components";

defineProps({
    content: {
        type: Object,
        required: true,
    },
});

const rings = ["one", "two", "three"];
const dots = ["one", "two"];
const miniLines = ["one", "two"];
</script>

<template>
    <section class="auth-intro fade-in">
        <div class="auth-intro-inner">
            <div class="auth-visual">
                <div class="auth-visual-shell">
                    <div
                        v-for="ring in rings"
                        :key="`auth-ring-${ring}`"
                        class="auth-ring"
                        :class="ring"
                    ></div>

                    <div
                        v-for="dot in dots"
                        :key="`auth-dot-${dot}`"
                        class="auth-dot"
                        :class="dot"
                    ></div>

                    <div
                        v-for="line in miniLines"
                        :key="`auth-mini-line-${line}`"
                        class="auth-mini-line"
                        :class="line"
                    ></div>

                    <div class="auth-mark one">
                        Π
                    </div>

                    <div class="auth-mark two">
                        Δ
                    </div>

                    <img
                        class="auth-logo-image"
                        :src="content.logo.src"
                        :alt="content.logo.alt"
                    />
                </div>
            </div>

            <div class="auth-badges">
                <span
                    v-for="badge in content.badges"
                    :key="badge.text"
                    class="auth-badge"
                >
                    <BaseIcon
                        :name="badge.icon"
                        size="13"
                    />

                    <span>{{ badge.text }}</span>
                </span>
            </div>

            <h1 class="auth-title">
                {{ content.title }}
            </h1>

            <p class="auth-subtitle">
                {{ content.subtitle }}
            </p>

            <div class="auth-meta">
                <div
                    v-for="item in content.meta"
                    :key="item.text"
                    class="auth-meta-item"
                >
                    <BaseIcon
                        :name="item.icon"
                        size="14"
                    />

                    <span>{{ item.text }}</span>
                </div>
            </div>
        </div>
    </section>
</template>
