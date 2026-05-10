import { computed } from "vue";

export function usePasswordStrength(password) {
    const rules = computed(() => {
        const value = password.value || "";

        return [
            {
                key: "length",
                label: "Не менее 8 символов",
                passed: value.length >= 8,
            },
            {
                key: "upper",
                label: "Хотя бы одна заглавная буква",
                passed: /[A-ZА-ЯЁ]/.test(value),
            },
            {
                key: "digit",
                label: "Хотя бы одна цифра",
                passed: /\d/.test(value),
            },
        ];
    });

    const passedRulesCount = computed(() => {
        return rules.value.filter((rule) => rule.passed).length;
    });

    const strength = computed(() => {
        if (!password.value) {
            return {
                label: "Недостаточно",
                variant: "empty",
                percent: 0,
            };
        }

        if (passedRulesCount.value <= 1) {
            return {
                label: "Слабый",
                variant: "weak",
                percent: 34,
            };
        }

        if (passedRulesCount.value === 2) {
            return {
                label: "Средний",
                variant: "medium",
                percent: 68,
            };
        }

        return {
            label: "Надёжный",
            variant: "strong",
            percent: 100,
        };
    });

    const isPasswordStrong = computed(() => {
        return passedRulesCount.value === rules.value.length;
    });

    return {
        rules,
        strength,
        isPasswordStrong,
    };
}
