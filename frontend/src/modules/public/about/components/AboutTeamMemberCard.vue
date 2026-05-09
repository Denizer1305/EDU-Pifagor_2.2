<script setup>
defineProps({
    member: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <article class="team-member fade-in">
        <div class="team-member-media">
            <img
                :src="member.image.src"
                :alt="member.image.alt"
            />
        </div>

        <div class="team-member-body">
            <h3>
                {{ member.name }}
            </h3>

            <div class="team-member-role">
                {{ member.role }}
            </div>

            <p>
                {{ member.text }}
            </p>
        </div>
    </article>
</template>