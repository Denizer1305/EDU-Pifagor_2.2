export class ApiError extends Error {
    constructor(message, options = {}) {
        super(message);

        this.name = "ApiError";
        this.status = options.status || null;
        this.data = options.data || null;
    }
}

export function getApiErrorMessage(error) {
    if (error instanceof ApiError) {
        return error.message;
    }

    if (error instanceof Error) {
        return error.message;
    }

    return "Не удалось выполнить запрос к серверу.";
}
