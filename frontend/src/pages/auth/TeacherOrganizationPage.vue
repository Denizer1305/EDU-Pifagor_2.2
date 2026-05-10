<script setup>
import AuthIntroPanel from "../../modules/auth/components/AuthIntroPanel.vue";
import TeacherOrganizationForm from "../../modules/auth/components/TeacherOrganizationForm.vue";

import {
    teacherOrganizationFormContent,
    teacherOrganizationIntroContent,
} from "../../modules/auth/data/authPages.data";
</script>

<template>
    <main class="auth-section teacher-organization-page">
        <div
            class="auth-grid-lines"
            aria-hidden="true"
        >
            <div class="auth-grid-line vertical left"></div>
            <div class="auth-grid-line vertical center"></div>
            <div class="auth-grid-line vertical right"></div>
            <div class="auth-grid-line horizontal top"></div>
            <div class="auth-grid-line horizontal bottom"></div>
        </div>

        <div
            class="auth-decor"
            aria-hidden="true"
        >
            <div class="auth-circle one"></div>
            <div class="auth-circle two"></div>
            <div class="auth-circle three"></div>

            <div class="auth-glow one"></div>
            <div class="auth-glow two"></div>

            <div class="auth-moving-line one"></div>
            <div class="auth-moving-line two"></div>
            <div class="auth-moving-line three"></div>
        </div>

        <div class="container">
            <div class="auth-layout auth-layout--teacher-organization">
                <AuthIntroPanel :content="teacherOrganizationIntroContent" />

                <TeacherOrganizationForm :content="teacherOrganizationFormContent" />
            </div>
        </div>
    </main>
</template>
