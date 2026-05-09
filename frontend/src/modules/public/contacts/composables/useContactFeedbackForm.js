import { reactive, ref } from "vue";

const INITIAL_FORM = {
    name: "",
    email: "",
    message: "",
    files: [],
    consent: false,
};

function createInitialForm() {
    return {
        ...INITIAL_FORM,
        files: [],
    };
}

export function useContactFeedbackForm() {
    const form = reactive(createInitialForm());
    const isSubmitted = ref(false);

    function updateFiles(event) {
        form.files = Array.from(event.target.files || []);
    }

    function resetForm() {
        Object.assign(form, createInitialForm());
        isSubmitted.value = false;
    }

    function submitForm() {
        isSubmitted.value = true;

        /*
         * Backend для публичной формы обратной связи подключим позже.
         * Сейчас форма не отправляет данные наружу, а только показывает
         * успешное состояние на frontend.
         */
    }

    return {
        form,
        isSubmitted,
        updateFiles,
        resetForm,
        submitForm,
    };
}
