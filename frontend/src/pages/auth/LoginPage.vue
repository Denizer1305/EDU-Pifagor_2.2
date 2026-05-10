<script setup>
import AuthIntroPanel from "../../modules/auth/components/AuthIntroPanel.vue";
import LoginForm from "../../modules/auth/components/LoginForm.vue";

import {
    loginFormContent,
    loginIntroContent,
} from "../../modules/auth/data/authPages.data";
</script>

<template>
    <main class="auth-section login-page">
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
            <div class="auth-layout">
                <AuthIntroPanel :content="loginIntroContent" />

                <LoginForm :content="loginFormContent" />
            </div>
        </div>
    </main>
</template>
