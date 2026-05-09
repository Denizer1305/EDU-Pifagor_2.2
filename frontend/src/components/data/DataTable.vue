<script setup>
import BaseIcon from "../ui/BaseIcon.vue";

defineProps({
    columns: {
        type: Array,
        required: true,
    },
    rows: {
        type: Array,
        default() {
            return [];
        },
    },
    rowKey: {
        type: String,
        default: "id",
    },
    emptyText: {
        type: String,
        default: "Нет данных для отображения.",
    },
    loading: {
        type: Boolean,
        default: false,
    },
});
</script>

<template>
    <div class="data-table">
        <div
            v-if="loading"
            class="data-table__state"
        >
            <BaseIcon
                name="spinner"
                size="30"
                class="data-table__spinner"
            />

            <span>Загружаем данные</span>
        </div>

        <div
            v-else
            class="data-table__scroll"
        >
            <table>
                <thead>
                    <tr>
                        <th
                            v-for="column in columns"
                            :key="column.key"
                            :style="{ width: column.width || undefined }"
                        >
                            {{ column.label }}
                        </th>

                        <th v-if="$slots.actions">
                            Действия
                        </th>
                    </tr>
                </thead>

                <tbody>
                    <tr
                        v-for="row in rows"
                        :key="row[rowKey] || JSON.stringify(row)"
                    >
                        <td
                            v-for="column in columns"
                            :key="column.key"
                            :data-label="column.label"
                        >
                            <slot
                                :name="`cell-${column.key}`"
                                :row="row"
                                :value="row[column.key]"
                            >
                                {{ row[column.key] }}
                            </slot>
                        </td>

                        <td
                            v-if="$slots.actions"
                            class="data-table__actions"
                            data-label="Действия"
                        >
                            <slot
                                name="actions"
                                :row="row"
                            />
                        </td>
                    </tr>

                    <tr v-if="!rows.length">
                        <td :colspan="columns.length + ($slots.actions ? 1 : 0)">
                            <div class="data-table__empty">
                                {{ emptyText }}
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.data-table {
    overflow: hidden;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-24);
    background: var(--white-86);
    box-shadow: var(--shadow-xs);
}

.data-table__scroll {
    width: 100%;
    overflow-x: auto;
}

.data-table table {
    width: 100%;
    min-width: 760px;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 15px 18px;
    border-bottom: 1px solid var(--primary-08);
    text-align: left;
    vertical-align: top;
}

.data-table th {
    color: var(--primary);
    background: var(--primary-04);
    font-size: 0.8rem;
    font-weight: var(--font-weight-bold);
    white-space: nowrap;
}

.data-table td {
    color: var(--secondary);
    font-size: 0.88rem;
    line-height: 1.55;
}

.data-table tr:last-child td {
    border-bottom: 0;
}

.data-table__actions {
    white-space: nowrap;
}

.data-table__state,
.data-table__empty {
    display: grid;
    justify-items: center;
    gap: 10px;
    padding: 34px 22px;
    color: var(--secondary);
    text-align: center;
    font-size: 0.9rem;
    font-weight: var(--font-weight-bold);
}

.data-table__spinner {
    color: var(--accent);
    animation: dataTableSpin 0.9s linear infinite;
}

@keyframes dataTableSpin {
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 720px) {
    .data-table table,
    .data-table thead,
    .data-table tbody,
    .data-table th,
    .data-table td,
    .data-table tr {
        display: block;
    }

    .data-table table {
        min-width: 0;
    }

    .data-table thead {
        display: none;
    }

    .data-table tr {
        padding: 12px;
        border-bottom: 1px solid var(--primary-08);
    }

    .data-table tr:last-child {
        border-bottom: 0;
    }

    .data-table td {
        display: grid;
        grid-template-columns: 130px minmax(0, 1fr);
        gap: 12px;
        padding: 9px 6px;
        border-bottom: 0;
    }

    .data-table td::before {
        content: attr(data-label);
        color: var(--primary);
        font-weight: var(--font-weight-bold);
    }

    .data-table__empty {
        display: block;
    }

    .data-table__empty::before {
        display: none;
    }
}
</style>
