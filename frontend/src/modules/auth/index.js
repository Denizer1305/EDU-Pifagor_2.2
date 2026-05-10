export { default as AuthIntroPanel } from "./components/AuthIntroPanel.vue";
export { default as EmailVerifyForm } from "./components/EmailVerifyForm.vue";
export { default as ForgotPasswordForm } from "./components/ForgotPasswordForm.vue";
export { default as LoginForm } from "./components/LoginForm.vue";
export { default as RegisterForm } from "./components/RegisterForm.vue";
export { default as ResetPasswordForm } from "./components/ResetPasswordForm.vue";
export { default as TeacherOrganizationForm } from "./components/TeacherOrganizationForm.vue";
export { default as LogoutConfirmCard } from "./components/LogoutConfirmCard.vue";
export { default as AuthStatusCard } from "./components/AuthStatusCard.vue";

export { usePasswordStrength } from "./composables/usePasswordStrength";
export { usePasswordVisibility } from "./composables/usePasswordVisibility";
export { useTeacherOrganizationCode } from "./composables/useTeacherOrganizationCode";
export { useVerificationCode } from "./composables/useVerificationCode";

export {
    checkEmailPageContent,
    emailVerifiedPageContent,
    emailVerifyFormContent,
    emailVerifyIntroContent,
    forgotPasswordFormContent,
    forgotPasswordIntroContent,
    linkExpiredPageContent,
    loginFormContent,
    loginIntroContent,
    logoutPageContent,
    registerFormContent,
    registerIntroContent,
    resetPasswordFormContent,
    resetPasswordIntroContent,
    teacherOrganizationFormContent,
    teacherOrganizationIntroContent,
    teacherPendingPageContent,
} from "./data/authPages.data";
