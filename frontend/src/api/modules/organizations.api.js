import { apiClient } from "../client";
import { API_ENDPOINTS } from "../endpoints";

export function fetchPublicOrganizations() {
    return apiClient.get(API_ENDPOINTS.publicOrganizations);
}

export function fetchPublicOrganizationTeachers(organizationId) {
    return apiClient.get(API_ENDPOINTS.publicOrganizationTeachers(organizationId));
}
