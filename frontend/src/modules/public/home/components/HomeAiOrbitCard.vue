<script setup>
defineProps({
    avatar: {
        type: Object,
        required: true,
    },
});

const orbitRings = ["one", "two", "three"];

const orbitNodes = [
    {
        className: "n1",
        icon: "fas fa-book",
    },
    {
        className: "n2",
        icon: "fas fa-check-double",
    },
    {
        className: "n3",
        icon: "fas fa-chart-pie",
    },
    {
        className: "n4",
        icon: "fas fa-comments",
    },
    {
        className: "n5",
        icon: "fas fa-lightbulb",
    },
];
</script>

<template>
    <article class="ai-card ai-orbit-card fade-in">
        <div class="ai-card-inner">
            <div class="ai-orbit-shell">
                <div
                    v-for="ring in orbitRings"
                    :key="ring"
                    class="ai-orbit-ring"
                    :class="ring"
                ></div>

                <div
                    v-for="node in orbitNodes"
                    :key="node.className"
                    class="ai-orbit-node"
                    :class="node.className"
                >
                    <i :class="node.icon"></i>
                </div>

                <div class="ai-core-avatar">
                    <img
                        :src="avatar.src"
                        :alt="avatar.alt"
                    />
                </div>
            </div>
        </div>
    </article>
</template>