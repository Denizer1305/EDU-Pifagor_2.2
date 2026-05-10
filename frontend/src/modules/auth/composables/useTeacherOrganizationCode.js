import { computed, ref } from "vue";

const CODE_MIN_LENGTH = 6;
const CODE_MAX_LENGTH = 20;

export function useTeacherOrganizationCode() {
    const organizationCode = ref("");

    const normalizedCode = computed(() => {
        return organizationCode.value
            .trim()
            .replace(/\s+/g, "")
            .replace(/[^a-zA-Z0-9-]/g, "")
            .toUpperCase()
            .slice(0, CODE_MAX_LENGTH);
    });

    const isCodeReady = computed(() => {
        return normalizedCode.value.length >= CODE_MIN_LENGTH;
    });

    function updateOrganizationCode(value) {
        organizationCode.value = String(value)
            .replace(/\s+/g, "")
            .replace(/[^a-zA-Z0-9-]/g, "")
            .toUpperCase()
            .slice(0, CODE_MAX_LENGTH);
    }

    function clearOrganizationCode() {
        organizationCode.value = "";
    }

    return {
        organizationCode,
        normalizedCode,
        isCodeReady,
        updateOrganizationCode,
        clearOrganizationCode,
    };
}
