<template>
    <div class="app">
        <RouterView v-slot="{ Component, route }">
            <Transition
                name="page-fade"
                mode="out-in"
            >
                <component
                    :is="Component"
                    :key="route.fullPath"
                />
            </Transition>
        </RouterView>
    </div>
</template>

<style scoped>
.app {
    min-height: 100vh;
    color: var(--color-text-primary, #2f2f2f);
    background: var(--color-page-background, #eef1f6);
}

.page-fade-enter-active,
.page-fade-leave-active {
    transition:
        opacity 0.18s ease,
        transform 0.18s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
    opacity: 0;
    transform: translateY(6px);
}
</style>
