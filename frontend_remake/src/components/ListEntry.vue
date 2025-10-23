<template>
    <router-link
        :to="to"
        class="list-entry no-deco"
        @click="onClick && onClick(item)"
    >
        <i v-if="icon" :class="icon"></i>
        <div class="flex-row space-between vertical-align">
            <div class="flex-col">
                <label>{{ item[labelField] }}</label>
                <div v-if="subField" class="sub-field">
                    {{ item[subField] }}
                </div>
                <div v-else-if="description" class="sub-field">
                    {{ description }}
                </div>
            </div>
            <div class="controls flex-row">
                <i 
                    v-for="action in actions" 
                    @click.prevent="action.method(item)" 
                    class="btn btn-text btn-icon"
                    :class="action.icon"
                ></i>
                <i 
                    v-if="onEdit" 
                    @click.prevent="onEdit(item)" 
                    class="bx bxs-edit btn btn-text btn-icon"
                ></i>
                <i 
                    v-if="onDelete" 
                    @click.prevent="onDelete(item)" 
                    class="bx bxs-trash btn btn-text btn-icon btn-icon-danger"
                ></i>
            </div>
        </div>
    </router-link>
</template>

<script setup>
defineProps({
    item: Object,
    to: String,
    icon: String,
    labelField: { type: String, default: "name" },
    subField: String,
    description: String,
    onClick: Function,
    onEdit: Function,
    onDelete: Function,
    actions: {
        type: Array,
        default: () => []
    }
})

const isLink = (value) => {
    if (!value) return false
    // simple URL check
    return value.startsWith('http://') || value.startsWith('https://')
}
</script>

<style scoped>
.list-entry {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    box-sizing: border-box;
    padding: 12px 16px;
    background: var(--color-neutral-100);
    border: 1px solid var(--color-neutral-200);
    border-radius: var(--btn-radius);
    cursor: pointer;
    transition: all var(--t-fast);
    box-shadow: var(--shadow-xs);
}
.list-entry:hover {
    background: var(--color-neutral-50);
    /* border-color: var(--color-primary-200); */
    box-shadow: var(--shadow-sm);
    transform: translateY(var(--btn-translate));
}
/* .list-entry:hover label {
    text-decoration: underline;
} */
.list-entry label {
    cursor: pointer;
    font-weight: var(--fw-medium);
    font-size: var(--fs-2);
    color: var(--text-dark-primary);
}
.list-entry .sub-field {
    font-size: var(--fs-1);
    color: var(--text-dark-secondary);
    margin-top: 2px;
}
.list-entry .controls {
    transition: var(--t-fast) opacity;
    opacity: 0;
}
.list-entry:hover .controls {
    opacity: 1;
}
.list-entry i {
    font-size: var(--fs-5);
    padding-inline: 4px;
}
.list-entry .controls i {
    font-size: var(--fs-4);
    padding: 10px;
    border-radius: 12px;
    transition: all var(--t-fast);
}

.list-entry .btn:hover {
  background-color: var(--color-primary-100);
  color: var(--color-primary-700);
  transform: scale(1.05);
}
</style>
