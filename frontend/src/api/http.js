import { ApiError } from "./errors";

const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

function getApiBaseUrl() {
    return import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
}

function buildUrl(endpoint) {
    const baseUrl = getApiBaseUrl().replace(/\/$/, "");
    const normalizedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;

    return `${baseUrl}${normalizedEndpoint}`;
}

async function parseResponse(response) {
    const contentType = response.headers.get("content-type") || "";

    if (!contentType.includes("application/json")) {
        return null;
    }

    return response.json();
}

export async function httpRequest(endpoint, options = {}) {
    const requestOptions = {
        method: options.method || "GET",
        headers: {
            Accept: "application/json",
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...(options.headers || {}),
        },
        credentials: options.credentials || "include",
    };

    if (options.body) {
        requestOptions.body = JSON.stringify(options.body);
    }

    const response = await fetch(buildUrl(endpoint), requestOptions);
    const data = await parseResponse(response);

    if (!response.ok) {
        throw new ApiError(
            data?.detail || data?.message || "Ошибка запроса к серверу.",
            {
                status: response.status,
                data,
            },
        );
    }

    return data;
}
