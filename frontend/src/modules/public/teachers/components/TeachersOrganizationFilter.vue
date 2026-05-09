<script setup>
defineProps({
    organizations: {
        type: Array,
        required: true,
    },
    modelValue: {
        type: String,
        required: true,
    },
});

const emit = defineEmits({
    "update:modelValue": (value) => typeof value === "string",
});

function selectOrganization(slug) {
    emit("update:modelValue", slug);
}
</script>

<template>
    <div class="teachers-organization-filter">
        <div class="teachers-organization-filter-head">
            <span class="teachers-organization-filter-label">
                Образовательная организация
            </span>
        </div>
    </div>
</template>
