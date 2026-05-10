import { computed, nextTick, ref } from "vue";

const CODE_LENGTH = 6;

export function useVerificationCode() {
    const codeDigits = ref(Array.from({ length: CODE_LENGTH }, () => ""));
    const inputRefs = ref([]);

    const verificationCode = computed(() => {
        return codeDigits.value.join("");
    });

    const isCodeComplete = computed(() => {
        return verificationCode.value.length === CODE_LENGTH;
    });

    function setInputRef(element, index) {
        if (element) {
            inputRefs.value[index] = element;
        }
    }

    function focusInput(index) {
        const input = inputRefs.value[index];

        if (input) {
            input.focus();
            input.select();
        }
    }

    function normalizeDigit(value) {
        return String(value).replace(/\D/g, "").slice(0, 1);
    }

    function handleInput(event, index) {
        const digit = normalizeDigit(event.target.value);

        codeDigits.value[index] = digit;
        event.target.value = digit;

        if (digit && index < CODE_LENGTH - 1) {
            nextTick(() => focusInput(index + 1));
        }
    }

    function handleKeydown(event, index) {
        if (event.key !== "Backspace") {
            return;
        }

        if (codeDigits.value[index]) {
            codeDigits.value[index] = "";
            return;
        }

        if (index > 0) {
            nextTick(() => focusInput(index - 1));
        }
    }

    function handlePaste(event) {
        const pastedCode = event.clipboardData
            .getData("text")
            .replace(/\D/g, "")
            .slice(0, CODE_LENGTH);

        if (!pastedCode) {
            return;
        }

        event.preventDefault();

        codeDigits.value = Array.from({ length: CODE_LENGTH }, (_, index) => {
            return pastedCode[index] || "";
        });

        const focusIndex = Math.min(pastedCode.length, CODE_LENGTH - 1);

        nextTick(() => focusInput(focusIndex));
    }

    function resetCode() {
        codeDigits.value = Array.from({ length: CODE_LENGTH }, () => "");
        nextTick(() => focusInput(0));
    }

    return {
        codeDigits,
        inputRefs,
        verificationCode,
        isCodeComplete,
        setInputRef,
        handleInput,
        handleKeydown,
        handlePaste,
        resetCode,
    };
}
