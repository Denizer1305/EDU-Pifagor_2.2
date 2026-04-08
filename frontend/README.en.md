# Frontend — EDU-Pifagor

The frontend part of **Pifagor Educational Platform** is built with **Vue 3 + Vite** and is responsible for the user interface, routing, role-based dashboards, forms, scheduling views, and analytics screens.

## Purpose

The frontend provides:
- public platform pages;
- authentication and personal dashboards;
- separate interfaces for admin, teacher, student, and parent;
- builders for courses, lessons, assignments, and schedules;
- feedback interfaces;
- dashboards and analytics screens.

## Main Stack

- Vue 3
- Vite
- Vue Router
- Pinia
- Axios
- SCSS

Optional additions:
- vee-validate
- yup
- ApexCharts

## Suggested Frontend Structure

```text
frontend/
├── README.md
├── package.json
├── vite.config.js
├── .env.example
├── index.html
├── public/
└── src/
    ├── main.js
    ├── App.vue
    ├── router/
    ├── stores/
    ├── api/
    ├── layouts/
    ├── pages/
    ├── components/
    ├── modules/
    ├── composables/
    ├── utils/
    ├── constants/
    ├── assets/
    ├── styles/
    └── widgets/
```

## Main Interface Areas

### public
- home page;
- about platform;
- teachers;
- contacts.

### auth
- login;
- registration;
- verification email;
- password reset.

### teacher
- my courses;
- lessons;
- materials;
- assignments;
- tests;
- schedule;
- analytics;
- overdue students.

### student
- my courses;
- assignments;
- diary;
- schedule;
- notifications.

### parent
- child performance;
- attendance;
- schedule;
- notifications.

### admin
- users;
- organizations;
- groups;
- subjects;
- data management;
- user feedback.

## Architectural Principles

- routes are separated by roles;
- API logic is placed in `src/api/`;
- reusable domain UI belongs in `src/modules/`;
- base and shared components belong in `src/components/`;
- layouts define dashboard structure;
- Pinia is used for global state.

## Local Run

```bash
npm install
npm run dev
```

## Environment Variables

Main ones:
- `VITE_APP_NAME`
- `VITE_API_BASE_URL`

## Build

```bash
npm run build
```

## Recommended Implementation Order

1. auth + router + guards
2. layouts
3. users / profile
4. courses
5. assignments / testing
6. schedule
7. analytics
8. feedback / notifications
