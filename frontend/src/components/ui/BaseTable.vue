<script setup>
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
    emptyText: {
        type: String,
        default: "Нет данных для отображения.",
    },
});
</script>

<template>
    <div class="base-table-wrapper">
        <table class="base-table">
            <thead>
                <tr>
                    <th
                        v-for="column in columns"
                        :key="column.key"
                    >
                        {{ column.label }}
                    </th>
                </tr>
            </thead>

            <tbody>
                <tr
                    v-for="row in rows"
                    :key="row.id || JSON.stringify(row)"
                >
                    <td
                        v-for="column in columns"
                        :key="column.key"
                    >
                        <slot
                            :name="`cell-${column.key}`"
                            :row="row"
                            :value="row[column.key]"
                        >
                            {{ row[column.key] }}
                        </slot>
                    </td>
                </tr>

                <tr v-if="!rows.length">
                    <td :colspan="columns.length">
                        <div class="base-table__empty">
                            {{ emptyText }}
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.base-table-wrapper {
    width: 100%;
    overflow-x: auto;
    border: 1px solid var(--primary-08);
    border-radius: var(--radius-24);
    background: var(--white-86);
    box-shadow: var(--shadow-xs);
}

.base-table {
    width: 100%;
    border-collapse: collapse;
    min-width: 720px;
}

.base-table th,
.base-table td {
    padding: 15px 18px;
    border-bottom: 1px solid var(--primary-08);
    text-align: left;
    vertical-align: top;
}

.base-table th {
    color: var(--primary);
    background: var(--primary-04);
    font-size: 0.82rem;
    font-weight: var(--font-weight-bold);
}

.base-table td {
    color: var(--secondary);
    font-size: 0.88rem;
    line-height: 1.55;
}

.base-table tr:last-child td {
    border-bottom: 0;
}

.base-table__empty {
    padding: 26px;
    color: var(--secondary);
    text-align: center;
}
</style>
