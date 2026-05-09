import { computed, ref } from "vue";

export function useTeacherModal() {
    const selectedTeacher = ref(null);

    const isTeacherModalOpen = computed(() => Boolean(selectedTeacher.value));

    function openTeacherModal(teacher) {
        selectedTeacher.value = teacher;
    }

    function closeTeacherModal() {
        selectedTeacher.value = null;
    }

    return {
        selectedTeacher,
        isTeacherModalOpen,
        openTeacherModal,
        closeTeacherModal,
    };
}