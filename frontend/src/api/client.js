import { httpRequest } from "./http";

export const apiClient = {
    get(endpoint, options = {}) {
        return httpRequest(endpoint, {
            ...options,
            method: "GET",
        });
    },

    post(endpoint, body, options = {}) {
        return httpRequest(endpoint, {
            ...options,
            method: "POST",
            body,
        });
    },

    patch(endpoint, body, options = {}) {
        return httpRequest(endpoint, {
            ...options,
            method: "PATCH",
            body,
        });
    },

    delete(endpoint, options = {}) {
        return httpRequest(endpoint, {
            ...options,
            method: "DELETE",
        });
    },
};
