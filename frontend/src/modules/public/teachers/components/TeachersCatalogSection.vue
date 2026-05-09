<script setup>
import { computed } from "vue";

import BaseIcon from "../../../../components/ui/BaseIcon.vue";
import PublicSectionHead from "../../shared/components/PublicSectionHead.vue";
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
    isLoading: {
        type: Boolean,
        default: false,
    },
    errorMessage: {
        type: String,
        default: "",
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
    if (!props.selectedOrganizationSlug) {
        return [];
    }

    return props.teachers.filter((teacher) => {
        return teacher.organizationSlug === props.selectedOrganizationSlug;
    });
});

const hasOrganizations = computed(() => props.organizations.length > 0);

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
                    v-if="hasOrganizations"
                    :model-value="selectedOrganizationSlug"
                    :organizations="organizations"
                    @update:model-value="updateSelectedOrganization"
                />

                <div
                    v-if="errorMessage"
                    class="teachers-api-status warning"
                >
                    <BaseIcon
                        name="info"
                        size="17"
                    />
                    <span>{{ errorMessage }}</span>
                </div>

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
                    v-if="isLoading"
                    class="teachers-empty-state"
                >
                    <div class="teachers-empty-icon">
                        <BaseIcon
                            name="spinner"
                            size="32"
                            class="teachers-loading-icon"
                        />
                    </div>

                    <h3>
                        Загружаем преподавателей
                    </h3>

                    <p>
                        Получаем актуальный список преподавателей выбранной образовательной организации.
                    </p>
                </div>

                <div
                    v-else-if="filteredTeachers.length"
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
                    v-else-if="!hasOrganizations"
                    class="teachers-empty-state"
                >
                    <div class="teachers-empty-icon">
                        <BaseIcon
                            name="building-columns"
                            size="32"
                        />
                    </div>

                    <h3>
                        {{ content.emptyOrganizationsTitle }}
                    </h3>

                    <p>
                        {{ content.emptyOrganizationsText }}
                    </p>
                </div>

                <div
                    v-else
                    class="teachers-empty-state"
                >
                    <div class="teachers-empty-icon">
                        <BaseIcon
                            name="teacher"
                            size="32"
                        />
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
