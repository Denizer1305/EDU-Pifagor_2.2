<script setup>
import { ref } from "vue";

import TeachersCatalogSection from "../../modules/public/teachers/components/TeachersCatalogSection.vue";
import TeachersCtaSection from "../../modules/public/teachers/components/TeachersCtaSection.vue";
import TeachersHeroSection from "../../modules/public/teachers/components/TeachersHeroSection.vue";
import TeacherModal from "../../modules/public/teachers/components/TeacherModal.vue";

import { useTeacherModal } from "../../modules/public/teachers/composables/useTeacherModal";

import {
    teachersCatalog,
    teachersCta,
    teachersHero,
    teachersOrganizations,
    teachersPageConfig,
    teachersList,
} from "../../modules/public/teachers/data/teachersPage.data";

const selectedOrganizationSlug = ref(teachersPageConfig.defaultOrganizationSlug);

const {
    selectedTeacher,
    isTeacherModalOpen,
    openTeacherModal,
    closeTeacherModal,
} = useTeacherModal();
</script>

<template>
    <main class="teachers-page">
        <TeachersHeroSection :content="teachersHero" />

        <TeachersCatalogSection
            v-model:selected-organization-slug="selectedOrganizationSlug"
            :content="teachersCatalog"
            :organizations="teachersOrganizations"
            :teachers="teachersList"
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