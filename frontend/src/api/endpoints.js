export const API_ENDPOINTS = {
    publicOrganizations: "/organizations/public/",

    publicOrganizationTeachers(organizationId) {
        return `/organizations/public/${organizationId}/teachers/`;
    },
};
