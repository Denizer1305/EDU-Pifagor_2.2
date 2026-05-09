<script setup>
defineProps({
    teacher: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits({
    open: (teacher) => Boolean(teacher),
});
</script>

<template>
    <button
        class="teacher-card fade-in"
        type="button"
        @click="emit('open', teacher)"
    >
        <div class="teacher-card-media">
            <img
                :src="teacher.image.src"
                :alt="teacher.image.alt"
            />
        </div>

        <div class="teacher-card-body">
            <div class="teacher-card-role">
                {{ teacher.role }}
            </div>

            <h3 class="teacher-card-name">
                {{ teacher.name }}
            </h3>

            <div class="teacher-card-subject">
                {{ teacher.subject }}
            </div>

            <div
                v-if="teacher.tags?.length"
                class="teacher-card-tags"
            >
                <span
                    v-for="tag in teacher.tags.slice(0, 3)"
                    :key="tag"
                    class="teacher-card-tag"
                >
                    {{ tag }}
                </span>
            </div>
        </div>
    </button>
</template>
