const FALLBACK_TEACHER_IMAGE = "/assets/image/foto_teachers.webp";

function normalizeText(value, fallback = "") {
    if (value === null || value === undefined) {
        return fallback;
    }

    return String(value).trim() || fallback;
}

function normalizeArray(value) {
    if (Array.isArray(value)) {
        return value.filter(Boolean);
    }

    if (typeof value === "string") {
        return value
            .split(/[\n;]+/)
            .map((item) => item.trim())
            .filter(Boolean);
    }

    return [];
}

export function mapPublicOrganizationFromApi(apiOrganization) {
    const id = String(apiOrganization.id);

    return {
        slug: id,
        id: apiOrganization.id,
        name: normalizeText(apiOrganization.name),
        shortName:
            normalizeText(apiOrganization.short_name)
            || normalizeText(apiOrganization.name),
        description:
            normalizeText(apiOrganization.description)
            || normalizeText(apiOrganization.city)
            || "Образовательная организация платформы.",
        logoUrl: normalizeText(apiOrganization.logo_url),
        isDefault: false,
    };
}

export function mapPublicTeacherFromApi(apiTeacher) {
    const organizationId = apiTeacher.organization_id
        ? String(apiTeacher.organization_id)
        : "";

    const name = normalizeText(apiTeacher.name, "Преподаватель");

    const imageSrc =
        normalizeText(apiTeacher.image)
        || normalizeText(apiTeacher.cover_image)
        || normalizeText(apiTeacher.avatar)
        || FALLBACK_TEACHER_IMAGE;

    return {
        id: `teacher-${apiTeacher.id}`,
        sourceId: apiTeacher.id,
        organizationSlug: organizationId,

        name,
        role: normalizeText(apiTeacher.role, "Преподаватель"),
        subject: normalizeText(apiTeacher.subject, "Преподаватель"),
        direction:
            normalizeText(apiTeacher.direction)
            || normalizeText(apiTeacher.subject)
            || normalizeText(apiTeacher.role, "Преподаватель"),

        image: {
            src: imageSrc,
            alt: name,
        },

        description: normalizeText(
            apiTeacher.description,
            "Публичное описание преподавателя пока не заполнено.",
        ),

        education: normalizeText(apiTeacher.education),
        experience: apiTeacher.experience || null,
        awards: normalizeArray(apiTeacher.awards),
        tags: normalizeArray(apiTeacher.tags).slice(0, 5),
    };
}

export function chooseDefaultOrganization(organizations) {
    const defaultOrganization = organizations.find((organization) => {
        const searchText = `${organization.name} ${organization.shortName}`.toLowerCase();

        return searchText.includes("влгк") || searchText.includes("советкин");
    });

    return defaultOrganization || organizations[0] || null;
}
