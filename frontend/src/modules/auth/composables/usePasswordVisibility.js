import { computed, ref } from "vue";

export function usePasswordVisibility() {
    const isPasswordVisible = ref(false);

    const passwordInputType = computed(() => {
        return isPasswordVisible.value ? "text" : "password";
    });

    const passwordToggleLabel = computed(() => {
        return isPasswordVisible.value ? "Скрыть пароль" : "Показать пароль";
    });

    const passwordToggleIcon = computed(() => {
        return isPasswordVisible.value ? "eye-crossed" : "eye";
    });

    function togglePasswordVisibility() {
        isPasswordVisible.value = !isPasswordVisible.value;
    }

    return {
        isPasswordVisible,
        passwordInputType,
        passwordToggleLabel,
        passwordToggleIcon,
        togglePasswordVisibility,
    };
}
