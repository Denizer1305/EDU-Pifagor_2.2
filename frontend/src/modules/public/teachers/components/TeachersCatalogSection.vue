<script setup>
import { computed } from "vue";

import PublicSectionHead from "../../home/shared/components/PublicSectionHead.vue";
import TeacherCard from "./TeacherCard.vue";
import TeachersOrganizationFilter from "./TeachersOrganizationFilter.vue";

const props = defineProps({
    content: {
        type: Object,
        required: true,
    },
    organizations: {
        type: Array,
        required: true,
    },
    teachers: {
        type: Array,
        required: true,
    },
    selectedOrganizationSlug: {
        type: String,
        required: true,
    },
});

const emit = defineEmits({
    "update:selectedOrganizationSlug": (value) => typeof value === "string",
    "open-teacher": (teacher) => Boolean(teacher),
});

const selectedOrganization = computed(() => {
    return props.organizations.find((organization) => {
        return organization.slug === props.selectedOrganizationSlug;
    });
});

const filteredTeachers = computed(() => {
    return props.teachers.filter((teacher) => {
        return teacher.organizationSlug === props.selectedOrganizationSlug;
    });
});

function updateSelectedOrganization(slug) {
    emit("update:selectedOrganizationSlug", slug);
}

function openTeacher(teacher) {
    emit("open-teacher", teacher);
}
</script>

<template>
    <section
        id="teachers-catalog"
        class="section teachers-catalog"
    >
        <div class="container">
            <PublicSectionHead
                :label="content.label"
                :title="content.title"
                :description="content.description"
            />

            <div class="teachers-shell fade-in">
                <TeachersOrganizationFilter
                    :model-value="selectedOrganizationSlug"
                    :organizations="organizations"
                    @update:model-value="updateSelectedOrganization"
                />

                <div
                    v-if="selectedOrganization"
                    class="teachers-current-organization"
                >
                    <div>
                        <span class="teachers-current-label">
                            Сейчас выбрана организация
                        </span>

                        <strong>
                            {{ selectedOrganization.name }}
                        </strong>
                    </div>

                    <span class="teachers-current-count">
                        {{ filteredTeachers.length }} преподавателей
                    </span>
                </div>

                <div
                    v-if="filteredTeachers.length"
                    class="teachers-grid"
                >
                    <TeacherCard
                        v-for="teacher in filteredTeachers"
                        :key="teacher.id"
                        :teacher="teacher"
                        @open="openTeacher"
                    />
                </div>

                <div
                    v-else
                    class="teachers-empty-state"
                >
                    <div class="teachers-empty-icon">
                        <i class="fas fa-chalkboard-user"></i>
                    </div>

                    <h3>
                        {{ content.emptyTitle }}
                    </h3>

                    <p>
                        {{ content.emptyText }}
                    </p>
                </div>
            </div>
        </div>
    </section>
</template>