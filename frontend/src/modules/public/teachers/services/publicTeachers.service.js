import {
    fetchPublicOrganizationTeachers,
    fetchPublicOrganizations,
} from "../../../../api/modules/organizations.api";

import {
    chooseDefaultOrganization,
    mapPublicOrganizationFromApi,
    mapPublicTeacherFromApi,
} from "../mappers/publicTeachers.mapper";

export async function getPublicOrganizations() {
    const organizations = await fetchPublicOrganizations();

    return organizations.map(mapPublicOrganizationFromApi);
}

export async function getPublicTeachersByOrganization(organizationSlug) {
    const teachers = await fetchPublicOrganizationTeachers(organizationSlug);

    return teachers.map(mapPublicTeacherFromApi);
}

export async function getPublicTeachersInitialData() {
    const organizations = await getPublicOrganizations();
    const defaultOrganization = chooseDefaultOrganization(organizations);

    if (!defaultOrganization) {
        return {
            organizations: [],
            defaultOrganizationSlug: "",
            teachers: [],
        };
    }

    const teachers = await getPublicTeachersByOrganization(defaultOrganization.slug);

    return {
        organizations,
        defaultOrganizationSlug: defaultOrganization.slug,
        teachers,
    };
}
