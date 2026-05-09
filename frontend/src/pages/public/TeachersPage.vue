<script setup>
import { onMounted, ref, watch } from "vue";

import TeachersCatalogSection from "../../modules/public/teachers/components/TeachersCatalogSection.vue";
import TeachersCtaSection from "../../modules/public/teachers/components/TeachersCtaSection.vue";
import TeachersHeroSection from "../../modules/public/teachers/components/TeachersHeroSection.vue";
import TeacherModal from "../../modules/public/teachers/components/TeacherModal.vue";

import { useTeacherModal } from "../../modules/public/teachers/composables/useTeacherModal";
import {
    getPublicTeachersByOrganization,
    getPublicTeachersInitialData,
} from "../../modules/public/teachers/services/publicTeachers.service";

import {
    teachersCatalog,
    teachersCta,
    teachersHero,
    teachersPageConfig,
} from "../../modules/public/teachers/data/teachersPage.data";

const selectedOrganizationSlug = ref(teachersPageConfig.defaultOrganizationSlug);

const organizations = ref([]);
const teachers = ref([]);

const isTeachersLoading = ref(false);
const teachersErrorMessage = ref("");
const isInitialSelectionChanging = ref(false);

const {
    selectedTeacher,
    isTeacherModalOpen,
    openTeacherModal,
    closeTeacherModal,
} = useTeacherModal();

async function loadInitialTeachersData() {
    isTeachersLoading.value = true;
    teachersErrorMessage.value = "";

    try {
        const result = await getPublicTeachersInitialData();

        organizations.value = result.organizations;
        teachers.value = result.teachers;

        isInitialSelectionChanging.value = true;
        selectedOrganizationSlug.value = result.defaultOrganizationSlug;
        isInitialSelectionChanging.value = false;

        if (!result.organizations.length) {
            teachersErrorMessage.value =
                "В базе данных пока нет активных образовательных организаций для публичного отображения.";
        }
    } catch (error) {
        organizations.value = [];
        teachers.value = [];
        selectedOrganizationSlug.value = "";

        teachersErrorMessage.value =
            "Не удалось загрузить список преподавателей из базы данных.";
    } finally {
        isTeachersLoading.value = false;
        isInitialSelectionChanging.value = false;
    }
}

async function loadTeachersByOrganization(organizationSlug) {
    if (!organizationSlug) {
        teachers.value = [];
        return;
    }

    isTeachersLoading.value = true;
    teachersErrorMessage.value = "";

    try {
        teachers.value = await getPublicTeachersByOrganization(organizationSlug);
    } catch (error) {
        teachers.value = [];

        teachersErrorMessage.value =
            "Не удалось загрузить преподавателей выбранной образовательной организации.";
    } finally {
        isTeachersLoading.value = false;
    }
}

watch(selectedOrganizationSlug, async (organizationSlug, previousOrganizationSlug) => {
    if (
        isInitialSelectionChanging.value
        || organizationSlug === previousOrganizationSlug
    ) {
        return;
    }

    await loadTeachersByOrganization(organizationSlug);
});

onMounted(() => {
    loadInitialTeachersData();
});
</script>

<template>
    <main class="teachers-page">
        <TeachersHeroSection :content="teachersHero" />

        <TeachersCatalogSection
            v-model:selected-organization-slug="selectedOrganizationSlug"
            :content="teachersCatalog"
            :organizations="organizations"
            :teachers="teachers"
            :is-loading="isTeachersLoading"
            :error-message="teachersErrorMessage"
            @open-teacher="openTeacherModal"
        />

        <TeachersCtaSection :content="teachersCta" />

        <TeacherModal
            :teacher="selectedTeacher"
            :is-open="isTeacherModalOpen"
            @close="closeTeacherModal"
        />
    </main>
</template>
